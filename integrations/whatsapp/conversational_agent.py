"""
Agente Conversacional Inteligente para WhatsApp
Processa todas as interações e direciona para agentes especializados
"""
from typing import Dict, List, Optional, Any
import json
import base64
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class WhatsAppConversationalAgent:
    """Agente IA que entende e responde via WhatsApp"""

    def __init__(
        self,
        llm_manager,
        evolution_api_client,
        crm_service,
        document_service,
        financial_service,
        agenda_service
    ):
        """
        Inicializa agente conversacional

        Args:
            llm_manager: Gerenciador de LLMs
            evolution_api_client: Cliente Evolution API
            crm_service: Serviço CRM
            document_service: Serviço de documentos
            financial_service: Serviço financeiro (Asaas)
            agenda_service: Serviço de agenda
        """
        self.llm = llm_manager
        self.whatsapp = evolution_api_client
        self.crm = crm_service
        self.docs = document_service
        self.finance = financial_service
        self.agenda = agenda_service

        # Contexto de conversas ativas
        self.conversations = {}

    # ==================== PROCESSAMENTO DE MENSAGENS ====================

    async def process_message(
        self,
        phone: str,
        message: str,
        media: Optional[Dict] = None
    ) -> str:
        """
        Processa mensagem recebida do WhatsApp

        Args:
            phone: Número do telefone
            message: Texto da mensagem
            media: Mídia anexada (imagem, documento, etc)

        Returns:
            Resposta para enviar
        """
        # Obter ou criar contexto da conversa
        context = self.conversations.get(phone, {
            'historico': [],
            'cliente_id': None,
            'aguardando': None
        })

        # Adicionar mensagem ao histórico
        context['historico'].append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.now()
        })

        # Identificar intenção usando LLM
        intencao = await self._identificar_intencao(message, media, context)

        # Rotear para agente especializado
        resposta = await self._rotear_para_agente(
            intencao=intencao,
            message=message,
            media=media,
            context=context,
            phone=phone
        )

        # Adicionar resposta ao histórico
        context['historico'].append({
            'role': 'assistant',
            'content': resposta,
            'timestamp': datetime.now()
        })

        # Salvar contexto
        self.conversations[phone] = context

        return resposta

    async def _identificar_intencao(
        self,
        message: str,
        media: Optional[Dict],
        context: Dict
    ) -> Dict:
        """
        Identifica intenção do usuário usando LLM

        Returns:
            {
                'tipo': 'cadastro_cliente', 'procuracao', 'pagamento', etc,
                'confianca': 0.95,
                'entidades': {...},
                'precisa_confirmacao': False
            }
        """
        # System prompt especializado
        system_prompt = """
        Você é um assistente jurídico inteligente que identifica a intenção do usuário.

        INTENÇÕES POSSÍVEIS:
        1. cadastro_cliente - Usuário quer cadastrar novo cliente
        2. consulta_cliente - Usuário quer consultar dados de cliente
        3. gerar_procuracao - Usuário pede procuração
        4. gerar_contrato - Usuário pede contrato
        5. gerar_peticao - Usuário quer gerar petição
        6. pagamento - Usuário envia comprovante ou consulta pagamento
        7. agendar_consulta - Usuário quer agendar horário
        8. consultar_processo - Usuário quer ver andamento de processo
        9. duvida_geral - Dúvida ou conversa geral
        10. saudacao - Saudação inicial

        ENTIDADES:
        - nome_cliente
        - cpf
        - email
        - telefone
        - tipo_documento
        - valor
        - data

        Retorne JSON com: tipo, confianca, entidades, precisa_confirmacao
        """

        prompt = f"""
        Mensagem do usuário: "{message}"
        Tem mídia anexada: {bool(media)}
        Tipo de mídia: {media.get('type') if media else None}

        Histórico recente:
        {self._formatar_historico(context.get('historico', [])[-3:])}

        Identifique a intenção e extraia entidades.
        """

        response = self.llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            task_type="chat",
            budget="low",  # Usa modelo rápido
            temperature=0.3
        )

        try:
            intencao = json.loads(response)
        except:
            # Fallback se não retornar JSON válido
            intencao = {
                'tipo': 'duvida_geral',
                'confianca': 0.5,
                'entidades': {},
                'precisa_confirmacao': False
            }

        return intencao

    async def _rotear_para_agente(
        self,
        intencao: Dict,
        message: str,
        media: Optional[Dict],
        context: Dict,
        phone: str
    ) -> str:
        """Roteia para agente especializado"""

        tipo = intencao['tipo']

        # Roteamento
        if tipo == 'cadastro_cliente':
            return await self._handle_cadastro_cliente(message, media, context, phone)

        elif tipo == 'gerar_procuracao':
            return await self._handle_gerar_procuracao(message, context, phone)

        elif tipo == 'gerar_peticao':
            return await self._handle_gerar_peticao(message, context, phone)

        elif tipo == 'pagamento':
            return await self._handle_pagamento(message, media, context, phone)

        elif tipo == 'agendar_consulta':
            return await self._handle_agendar_consulta(message, context, phone)

        elif tipo == 'consultar_processo':
            return await self._handle_consultar_processo(message, context, phone)

        elif tipo == 'saudacao':
            return self._saudacao_inicial()

        else:
            return await self._handle_duvida_geral(message, context)

    # ==================== CADASTRO DE CLIENTE ====================

    async def _handle_cadastro_cliente(
        self,
        message: str,
        media: Optional[Dict],
        context: Dict,
        phone: str
    ) -> str:
        """
        Cadastra cliente extraindo dados da mensagem ou documento

        Fluxo:
        1. Se tem documento → extrai dados com IA
        2. Se só texto → pede informações faltantes
        3. Confirma dados antes de salvar
        """
        if media and media.get('type') in ['document', 'image']:
            # EXTRAÇÃO COM VISION AI
            dados_extraidos = await self._extrair_dados_documento(media)

            # Validar dados extraídos
            if self._validar_dados_cliente(dados_extraidos):
                # Salvar no CRM
                cliente = self.crm.criar_cliente(dados_extraidos)

                context['cliente_id'] = cliente['id']

                return f"""
✅ *Cliente cadastrado com sucesso!*

📋 *Dados cadastrados:*
👤 Nome: {cliente['nome']}
📧 Email: {cliente['email']}
📱 Telefone: {cliente['telefone']}
🆔 CPF: {cliente['cpf']}

O que mais posso fazer por você?
                """
            else:
                # Dados incompletos
                return f"""
📄 Analisei o documento, mas faltam algumas informações:

{self._listar_dados_faltantes(dados_extraidos)}

Por favor, me envie essas informações.
                """
        else:
            # Extrair dados do texto
            dados = await self._extrair_dados_texto(message)

            if dados.get('nome') and dados.get('cpf'):
                # Dados suficientes, confirmar
                context['aguardando'] = {
                    'tipo': 'confirmar_cadastro',
                    'dados': dados
                }

                return f"""
📝 *Confirme os dados para cadastro:*

👤 Nome: {dados.get('nome')}
🆔 CPF: {dados.get('cpf')}
📧 Email: {dados.get('email', 'Não informado')}
📱 Telefone: {dados.get('telefone', phone)}

Confirma? (sim/não)
                """
            else:
                # Pedir dados
                return """
👋 Vou cadastrar um novo cliente!

Por favor, me envie:
1️⃣ Nome completo
2️⃣ CPF
3️⃣ Email
4️⃣ Endereço (opcional)

Ou envie um documento (RG, CNH, comprovante) que eu extraio os dados automaticamente! 📄
                """

    async def _extrair_dados_documento(self, media: Dict) -> Dict:
        """
        Extrai dados de documento usando Vision AI

        Args:
            media: {
                'type': 'document' ou 'image',
                'url': 'https://...',
                'base64': '...'
            }

        Returns:
            Dados extraídos
        """
        # Baixar documento
        documento_bytes = await self.whatsapp.download_media(media['url'])

        # Se for imagem, usar GPT-4 Vision
        if media['type'] == 'image':
            dados = await self._extrair_com_vision(documento_bytes)
        else:
            # Se for PDF/DOC, extrair texto e processar
            texto = self.docs.extract_text(documento_bytes)
            dados = await self._extrair_dados_texto(texto)

        return dados

    async def _extrair_com_vision(self, image_bytes: bytes) -> Dict:
        """Extrai dados de imagem com GPT-4 Vision"""

        base64_image = base64.b64encode(image_bytes).decode('utf-8')

        prompt = """
        Analise esta imagem de documento (RG, CNH, comprovante, etc) e extraia:

        - nome_completo
        - cpf
        - rg
        - data_nascimento
        - endereco
        - telefone
        - email

        Retorne JSON com os dados encontrados. Se não encontrar algum dado, não inclua no JSON.
        """

        # Usar GPT-4 Vision
        response = await self.llm.generate(
            prompt=prompt,
            model="gpt-4-vision-preview",
            task_type="análise_complexa",
            temperature=0.2,
            additional_params={
                'image': f"data:image/jpeg;base64,{base64_image}"
            }
        )

        try:
            return json.loads(response)
        except:
            return {}

    # ==================== GERAÇÃO DE PROCURAÇÃO ====================

    async def _handle_gerar_procuracao(
        self,
        message: str,
        context: Dict,
        phone: str
    ) -> str:
        """
        Gera procuração automaticamente

        Fluxo:
        1. Identifica cliente mencionado ou usa último da conversa
        2. Pega dados do CRM
        3. Gera procuração com template do escritório
        4. Envia PDF para assinatura digital
        """
        # Identificar cliente
        cliente_nome = self._extrair_nome_cliente(message)

        if cliente_nome:
            cliente = self.crm.buscar_cliente_por_nome(cliente_nome)
        elif context.get('cliente_id'):
            cliente = self.crm.buscar_cliente(context['cliente_id'])
        else:
            return "De qual cliente você quer a procuração? Me diga o nome."

        if not cliente:
            return f"Não encontrei o cliente '{cliente_nome}'. Tem certeza do nome?"

        # Dados do escritório (pegar de config)
        escritorio = {
            'nome': 'Silva & Santos Advogados',
            'oab_advogado': 'OAB/SP 123456',
            'advogado_nome': 'Dr. João Silva',
            'endereco': 'Rua Exemplo, 123 - São Paulo/SP'
        }

        # Gerar procuração
        procuracao_texto = self._gerar_procuracao_template(cliente, escritorio)

        # Gerar PDF
        pdf_bytes = self.docs.gerar_pdf(procuracao_texto)

        # Enviar para DocuSign/ClickSign
        link_assinatura = await self._enviar_para_assinatura(
            documento=pdf_bytes,
            signatario={
                'nome': cliente['nome'],
                'email': cliente['email'],
                'telefone': cliente['telefone']
            }
        )

        # Enviar PDF e link no WhatsApp
        await self.whatsapp.send_document(
            phone=phone,
            document=pdf_bytes,
            filename=f"Procuracao_{cliente['nome']}.pdf",
            caption="📄 Procuração gerada!"
        )

        return f"""
✅ *Procuração gerada com sucesso!*

👤 Cliente: {cliente['nome']}
📄 Documento enviado acima

🔗 *Link para assinatura digital:*
{link_assinatura}

O cliente pode assinar diretamente pelo celular!
        """

    def _gerar_procuracao_template(self, cliente: Dict, escritorio: Dict) -> str:
        """Gera texto da procuração"""
        return f"""
PROCURAÇÃO

OUTORGANTE: {cliente['nome']}, brasileiro(a), portador(a) do CPF nº {cliente['cpf']},
residente e domiciliado(a) em {cliente.get('endereco', '...')}.

OUTORGADO: {escritorio['advogado_nome']}, {escritorio['oab_advogado']},
com escritório na {escritorio['endereco']}.

PODERES: Pelo presente instrumento particular de PROCURAÇÃO, o(a) OUTORGANTE
constitui e nomeia seu bastante Procurador o(a) OUTORGADO acima qualificado(a),
a quem confere amplos poderes para representá-lo(a) em juízo ou fora dele,
podendo propor as ações que entender necessárias e defender os seus interesses
em qualquer instância, inclusive nos Tribunais Superiores, com os poderes da
cláusula ad judicia et extra, e ainda os especiais para confessar, reconhecer a
procedência do pedido, transigir, desistir, renunciar ao direito sobre o qual se
funda a ação, receber, dar quitação, firmar compromisso, bem como substabelecer
esta em outrem, com ou sem reservas de iguais poderes, podendo ainda, requerer
a expedição de alvarás, praticando todos os atos necessários ao fiel cumprimento
do presente mandato.

{datetime.now().strftime('%d de %B de %Y')}

_________________________________
{cliente['nome']}
CPF: {cliente['cpf']}
        """

    async def _enviar_para_assinatura(
        self,
        documento: bytes,
        signatario: Dict
    ) -> str:
        """
        Envia documento para plataforma de assinatura digital

        Returns:
            Link de assinatura
        """
        # Integração com DocuSign/ClickSign/D4Sign
        # Por enquanto, retorna link simulado
        return f"https://assinatura.lobojur.com.br/{signatario['telefone']}/procuracao"

    # ==================== PROCESSAMENTO DE PAGAMENTO ====================

    async def _handle_pagamento(
        self,
        message: str,
        media: Optional[Dict],
        context: Dict,
        phone: str
    ) -> str:
        """
        Processa comprovante de pagamento

        Fluxo:
        1. Recebe comprovante (imagem ou PDF)
        2. Extrai dados com Vision AI: valor, data, banco
        3. Busca cobrança no Asaas
        4. Confirma pagamento
        5. Atualiza financeiro
        """
        if not media:
            return """
💰 *Consulta de Pagamento*

Por favor, envie o comprovante de pagamento (foto ou PDF) para eu processar!

Ou me diga o que precisa:
• Ver faturas em aberto
• Gerar boleto
• Gerar PIX
            """

        # Extrair dados do comprovante com Vision AI
        dados_pagamento = await self._extrair_dados_comprovante(media)

        if not dados_pagamento.get('valor'):
            return "Não consegui identificar o valor no comprovante. Pode me enviar outro mais claro?"

        # Buscar cobrança no Asaas
        cliente = self.crm.buscar_cliente_por_telefone(phone)

        if cliente:
            cobranças = self.finance.buscar_cobranças_pendentes(cliente['asaas_id'])

            # Matching de valor
            cobranca_encontrada = next(
                (c for c in cobranças if abs(c['valor'] - dados_pagamento['valor']) < 0.01),
                None
            )

            if cobranca_encontrada:
                # Confirmar pagamento
                self.finance.confirmar_pagamento(
                    cobranca_id=cobranca_encontrada['id'],
                    comprovante_url=media['url']
                )

                return f"""
✅ *Pagamento confirmado!*

💰 Valor: R$ {dados_pagamento['valor']:.2f}
📅 Data: {dados_pagamento.get('data', 'Hoje')}
🏦 Banco: {dados_pagamento.get('banco', 'N/A')}

📋 Referência: {cobranca_encontrada['descricao']}

Obrigado! Seu pagamento foi registrado. 🎉
                """
            else:
                return f"""
⚠️ Pagamento recebido mas não encontrei cobrança pendente com esse valor (R$ {dados_pagamento['valor']:.2f}).

Seus pagamentos pendentes:
{self._listar_cobranças(cobranças)}

O comprovante foi salvo e nosso financeiro vai analisar. Ok?
                """
        else:
            return "Primeiro preciso cadastrar você como cliente. Me envie seus dados!"

    async def _extrair_dados_comprovante(self, media: Dict) -> Dict:
        """
        Extrai dados de comprovante de pagamento

        Returns:
            {
                'valor': 150.00,
                'data': '2024-12-08',
                'banco': 'Nubank',
                'tipo': 'PIX',
                'destinatario': '...'
            }
        """
        documento_bytes = await self.whatsapp.download_media(media['url'])
        base64_img = base64.b64encode(documento_bytes).decode('utf-8')

        prompt = """
        Analise este comprovante de pagamento e extraia:
        - valor (número decimal)
        - data (YYYY-MM-DD)
        - banco
        - tipo (PIX, TED, boleto, etc)
        - destinatario

        Retorne JSON.
        """

        response = await self.llm.generate(
            prompt=prompt,
            model="gpt-4-vision-preview",
            task_type="análise_complexa",
            temperature=0.1,
            additional_params={'image': f"data:image/jpeg;base64,{base64_img}"}
        )

        try:
            return json.loads(response)
        except:
            return {}

    # ==================== UTILITÁRIOS ====================

    def _formatar_historico(self, mensagens: List[Dict]) -> str:
        """Formata histórico de mensagens"""
        return "\n".join([
            f"{m['role']}: {m['content']}"
            for m in mensagens
        ])

    def _saudacao_inicial(self) -> str:
        """Saudação inicial"""
        return """
👋 Olá! Sou o assistente virtual do *LoboJur*!

Posso te ajudar com:

📋 *Cadastros*
• Cadastrar novo cliente
• Atualizar dados

📄 *Documentos*
• Gerar procuração
• Criar contratos
• Fazer petições

💰 *Financeiro*
• Enviar comprovantes
• Gerar boletos/PIX
• Consultar faturas

📅 *Agendamentos*
• Marcar consulta
• Ver agenda

🔍 *Processos*
• Consultar andamentos
• Buscar jurisprudências

Como posso ajudar? 😊
        """

    def _validar_dados_cliente(self, dados: Dict) -> bool:
        """Valida se dados de cliente estão completos"""
        campos_obrigatorios = ['nome', 'cpf']
        return all(dados.get(campo) for campo in campos_obrigatorios)

    def _extrair_nome_cliente(self, message: str) -> Optional[str]:
        """Extrai nome de cliente da mensagem"""
        # Padrões como: "procuração do João", "contrato da Maria"
        patterns = [
            r'(?:do|da|de)\s+([A-ZÁÉÍÓÚ][a-záéíóú]+(?:\s+[A-ZÁÉÍÓÚ][a-záéíóú]+)*)',
            r'cliente\s+([A-ZÁÉÍÓÚ][a-záéíóú]+(?:\s+[A-ZÁÉÍÓÚ][a-záéíóú]+)*)',
        ]

        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                return match.group(1)

        return None
