"""
Camada de Integração - Conecta todos os módulos do sistema
"""
from typing import Dict, Any, Optional
import asyncio
from pathlib import Path

# Importar todos os módulos
from integrations.asaas.client import AsaasClient
from integrations.escavador.client import EscavadorClient
from integrations.whatsapp.evolution_api_client import EvolutionAPIClient
from integrations.whatsapp.conversational_agent import WhatsAppConversationalAgent
from ai_engine.llm_providers.multi_llm_manager import MultiLLMManager
from ai_engine.rag_system.juridical_rag import JuridicalRAG
from database.db_manager import DatabaseManager


class LoboJurCore:
    """Núcleo central do sistema - integra todos os módulos"""

    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa sistema completo

        Args:
            config: {
                'openai_key': '...',
                'anthropic_key': '...',
                'google_key': '...',
                'asaas_key': '...',
                'escavador_key': '...',
                'evolution_api_url': '...',
                'evolution_api_key': '...',
                'evolution_instance': '...',
                'database_path': '...'
            }
        """
        self.config = config
        self._initialize_modules()

    def _initialize_modules(self):
        """Inicializa todos os módulos"""

        # 1. Banco de Dados
        self.db = DatabaseManager(
            db_path=self.config.get('database_path', 'data/lobojur.db')
        )

        # 2. LLM Manager (Multi-modelo)
        llm_keys = {
            'openai': self.config.get('openai_key'),
            'anthropic': self.config.get('anthropic_key'),
            'google': self.config.get('google_key'),
            'cohere': self.config.get('cohere_key')
        }
        # Remover chaves None
        llm_keys = {k: v for k, v in llm_keys.items() if v}

        self.llm = MultiLLMManager(api_keys=llm_keys)

        # 3. RAG System
        self.rag = JuridicalRAG(
            persist_directory=self.config.get('rag_directory', 'data/rag_storage')
        )

        # 4. Asaas (Financeiro)
        if self.config.get('asaas_key'):
            self.asaas = AsaasClient(
                api_key=self.config['asaas_key'],
                sandbox=self.config.get('asaas_sandbox', True)
            )
        else:
            self.asaas = None

        # 5. Escavador (Pesquisa)
        if self.config.get('escavador_key'):
            self.escavador = EscavadorClient(
                api_key=self.config['escavador_key']
            )
        else:
            self.escavador = None

        # 6. Evolution API (WhatsApp)
        if all([
            self.config.get('evolution_api_url'),
            self.config.get('evolution_api_key'),
            self.config.get('evolution_instance')
        ]):
            self.whatsapp = EvolutionAPIClient(
                api_url=self.config['evolution_api_url'],
                api_key=self.config['evolution_api_key'],
                instance_name=self.config['evolution_instance']
            )
        else:
            self.whatsapp = None

        # 7. Agente Conversacional WhatsApp
        if self.whatsapp:
            self.whatsapp_agent = WhatsAppConversationalAgent(
                llm_manager=self.llm,
                evolution_api_client=self.whatsapp,
                crm_service=CRMService(self.db),
                document_service=DocumentService(self.db),
                financial_service=FinancialService(self.db, self.asaas),
                agenda_service=AgendaService(self.db)
            )
        else:
            self.whatsapp_agent = None

    # ==================== FLUXOS COMPLETOS ====================

    async def processar_mensagem_whatsapp(
        self,
        phone: str,
        message: str,
        media: Optional[Dict] = None
    ) -> str:
        """
        Processa mensagem do WhatsApp e retorna resposta

        Este é o ponto de entrada principal para WhatsApp
        """
        if not self.whatsapp_agent:
            raise ValueError("WhatsApp não configurado")

        return await self.whatsapp_agent.process_message(phone, message, media)

    async def gerar_peticao_completa(
        self,
        area_direito: str,
        contexto: str,
        cliente_id: Optional[int] = None
    ) -> Dict:
        """
        Gera petição completa com IA + RAG

        Fluxo:
        1. Busca jurisprudências (Escavador + RAG)
        2. Busca doutrinas (RAG)
        3. Busca legislação (RAG)
        4. Gera petição com LLM (Claude Opus ou Gemini Pro)
        5. Salva no banco
        """
        # 1. Buscar fundamentação no RAG
        fundamentacao = self.rag.hybrid_search(
            query=contexto,
            collections=['jurisprudencias', 'doutrinas', 'legislacao'],
            n_results_per_collection=3
        )

        # 2. Buscar jurisprudências online (Escavador)
        if self.escavador:
            try:
                jurisps_online = await asyncio.to_thread(
                    self.escavador.buscar_jurisprudencia,
                    query=contexto,
                    tribunal="STJ",
                    per_page=3
                )

                # Adicionar ao RAG para futuro
                for j in jurisps_online:
                    self.rag.add_jurisprudencia(
                        texto=j.get('ementa', ''),
                        metadata={
                            'tribunal': 'STJ',
                            'numero_processo': j.get('numero', ''),
                            'area_direito': area_direito
                        }
                    )
            except Exception as e:
                print(f"Erro ao buscar jurisprudências: {e}")
                jurisps_online = []
        else:
            jurisps_online = []

        # 3. Montar contexto rico para LLM
        contexto_completo = self._montar_contexto_peticao(
            contexto=contexto,
            fundamentacao=fundamentacao,
            jurisps_online=jurisps_online
        )

        # 4. Gerar petição com melhor LLM
        system_prompt = f"""
        Você é um advogado especialista em {area_direito}.
        Gere uma petição inicial completa e fundamentada.
        """

        peticao_texto = await asyncio.to_thread(
            self.llm.generate,
            prompt=contexto_completo,
            system_prompt=system_prompt,
            task_type="petições_complexas",
            budget="high",  # Usar melhor modelo
            temperature=0.3,
            max_tokens=4000
        )

        # 5. Salvar no banco
        peticao_id = self.db.salvar_peticao({
            'area_id': self._get_area_id(area_direito),
            'titulo': f"Petição - {area_direito}",
            'conteudo': peticao_texto,
            'contexto_usuario': contexto,
            'jurisprudencias_utilizadas': fundamentacao.get('jurisprudencias', []),
            'doutrinas_utilizadas': fundamentacao.get('doutrinas', [])
        })

        return {
            'id': peticao_id,
            'texto': peticao_texto,
            'fundamentacao': fundamentacao
        }

    def _montar_contexto_peticao(
        self,
        contexto: str,
        fundamentacao: Dict,
        jurisps_online: list
    ) -> str:
        """Monta contexto rico para geração de petição"""
        partes = [
            "# CONTEXTO DO CASO",
            contexto,
            "\n# JURISPRUDÊNCIAS RELEVANTES"
        ]

        # Adicionar jurisprudências do RAG
        for j in fundamentacao.get('jurisprudencias', []):
            partes.append(f"\n**{j['metadata'].get('tribunal')}** (Score: {j['score']:.2f})")
            partes.append(j['texto'][:500])

        # Adicionar jurisprudências online
        for j in jurisps_online:
            partes.append(f"\n**{j.get('tribunal')}** - {j.get('numero')}")
            partes.append(j.get('ementa', '')[:500])

        # Adicionar doutrinas
        partes.append("\n# DOUTRINA")
        for d in fundamentacao.get('doutrinas', []):
            partes.append(f"\n**{d['metadata'].get('autor')}** (Score: {d['score']:.2f})")
            partes.append(d['texto'][:500])

        # Adicionar legislação
        partes.append("\n# LEGISLAÇÃO APLICÁVEL")
        for l in fundamentacao.get('legislacao', []):
            partes.append(f"\n**Art. {l['metadata'].get('artigo')}**")
            partes.append(l['texto'])

        return "\n\n".join(partes)

    def _get_area_id(self, area_nome: str) -> int:
        """Obtém ID da área do direito"""
        area = self.db.get_area_by_nome(area_nome)
        return area.id if area else 1

    async def processar_pagamento_automatico(
        self,
        cliente_id: int,
        comprovante_bytes: bytes
    ) -> Dict:
        """
        Processa pagamento automaticamente

        1. Extrai dados do comprovante com Vision AI
        2. Busca cobrança no Asaas
        3. Confirma pagamento
        4. Atualiza banco de dados
        5. Envia confirmação por WhatsApp
        """
        # 1. Extrair dados com Vision AI
        base64_img = base64.b64encode(comprovante_bytes).decode('utf-8')

        prompt = """
        Extraia do comprovante de pagamento:
        - valor (decimal)
        - data (YYYY-MM-DD)
        - tipo (PIX, TED, Boleto)

        Retorne JSON.
        """

        dados_json = await asyncio.to_thread(
            self.llm.generate,
            prompt=prompt,
            model="gpt-4-vision-preview",
            task_type="análise_complexa",
            temperature=0.1,
            additional_params={'image': f"data:image/jpeg;base64,{base64_img}"}
        )

        import json
        dados = json.loads(dados_json)

        # 2. Buscar cobrança no Asaas
        if self.asaas:
            # Implementar lógica de busca e confirmação
            pass

        return {
            'status': 'processado',
            'dados': dados
        }


# ==================== SERVIÇOS ====================

class CRMService:
    """Serviço de CRM"""
    def __init__(self, db):
        self.db = db

    def criar_cliente(self, dados: Dict) -> Dict:
        """Cria cliente no CRM"""
        # Implementar
        return {'id': 1, **dados}

    def buscar_cliente_por_nome(self, nome: str):
        """Busca cliente por nome"""
        # Implementar
        return None

    def buscar_cliente(self, cliente_id: int):
        """Busca cliente por ID"""
        # Implementar
        return None

    def buscar_cliente_por_telefone(self, telefone: str):
        """Busca cliente por telefone"""
        # Implementar
        return None


class DocumentService:
    """Serviço de documentos"""
    def __init__(self, db):
        self.db = db

    def extract_text(self, document_bytes: bytes) -> str:
        """Extrai texto de documento"""
        # Implementar
        return ""

    def gerar_pdf(self, texto: str) -> bytes:
        """Gera PDF"""
        # Implementar
        return b""


class FinancialService:
    """Serviço financeiro"""
    def __init__(self, db, asaas_client):
        self.db = db
        self.asaas = asaas_client

    def buscar_cobranças_pendentes(self, cliente_asaas_id: str):
        """Busca cobranças pendentes"""
        # Implementar
        return []

    def confirmar_pagamento(self, cobranca_id: str, comprovante_url: str):
        """Confirma pagamento"""
        # Implementar
        pass


class AgendaService:
    """Serviço de agenda"""
    def __init__(self, db):
        self.db = db

    # Implementar métodos de agenda


# ==================== EXEMPLO DE USO ====================

async def exemplo_sistema_completo():
    """Exemplo de uso do sistema completo"""

    # Configuração
    config = {
        'openai_key': 'sk-...',
        'anthropic_key': 'sk-ant-...',
        'google_key': 'AIza...',
        'asaas_key': 'xxx',
        'escavador_key': 'xxx',
        'evolution_api_url': 'https://api.evolution.com',
        'evolution_api_key': 'xxx',
        'evolution_instance': 'lobojur',
        'database_path': 'data/lobojur.db',
        'rag_directory': 'data/rag_storage'
    }

    # Inicializar sistema
    lobojur = LoboJurCore(config)

    # 1. Processar mensagem do WhatsApp
    resposta = await lobojur.processar_mensagem_whatsapp(
        phone="5511999999999",
        message="Quero cadastrar um cliente novo"
    )
    print(f"Resposta WhatsApp: {resposta}")

    # 2. Gerar petição completa
    peticao = await lobojur.gerar_peticao_completa(
        area_direito="Direito Civil",
        contexto="Cliente sofreu danos morais por cobrança indevida...",
        cliente_id=123
    )
    print(f"Petição gerada: {peticao['id']}")

    # 3. Processar pagamento
    with open('comprovante.jpg', 'rb') as f:
        resultado = await lobojur.processar_pagamento_automatico(
            cliente_id=123,
            comprovante_bytes=f.read()
        )
    print(f"Pagamento: {resultado}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(exemplo_sistema_completo())
