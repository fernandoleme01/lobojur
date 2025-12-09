"""
Agente Especialista em Direito Tributário
"""
from typing import Dict, List


class AgenteDireitoTributario:
    """Agente especializado em Direito Tributário"""

    def __init__(self, llm, jurisprudencia_service, doutrina_service):
        self.llm = llm
        self.jurisprudencia_service = jurisprudencia_service
        self.doutrina_service = doutrina_service

        self.backstory = """
        Você é um advogado tributarista experiente, especializado em:
        - Planejamento tributário
        - Execuções fiscais
        - Mandado de segurança tributário
        - Ações anulatórias de débito fiscal
        - Repetição de indébito tributário
        - Compensação tributária
        - Parcelamentos especiais (PERT, REFIS)
        - Consultoria tributária empresarial
        - Compliance tributário
        - Contencioso administrativo (CARF)

        Tributos principais:
        - IRPJ/CSLL
        - PIS/COFINS
        - ICMS
        - ISS
        - IPI
        - Contribuições previdenciárias

        Legislação principal:
        - Código Tributário Nacional (Lei 5.172/66)
        - Constituição Federal (arts. 145 a 162)
        - Lei 6.830/80 (Execuções Fiscais)
        - LC 123/06 (Simples Nacional)
        - IN RFB (normas infralegais)

        Doutrinadores:
        - Hugo de Brito Machado
        - Paulo de Barros Carvalho
        - Roque Antonio Carrazza
        - Sacha Calmon Navarro Coêlho
        - Ricardo Alexandre
        """

    async def analisar_caso(self, contexto: str) -> Dict:
        """Analisa caso tributário"""
        tipo_acao = self._identificar_tipo_acao(contexto)
        partes = self._identificar_partes(contexto)
        fatos = self._extrair_fatos(contexto)
        tributos = self._identificar_tributos(contexto)
        fundamentos = self._identificar_fundamentos(contexto)
        pedidos = self._sugerir_pedidos(contexto, tipo_acao)
        teses = self._identificar_teses(contexto)

        return {
            'tipo_acao': tipo_acao,
            'partes': partes,
            'fatos': fatos,
            'tributos_envolvidos': tributos,
            'fundamentos': fundamentos,
            'pedidos': pedidos,
            'teses_tributarias': teses
        }

    def _identificar_tipo_acao(self, contexto: str) -> str:
        """Identifica tipo de ação tributária"""
        contexto_lower = contexto.lower()

        tipos = {
            'mandado de segurança tributário': ['mandado de segurança', 'ms', 'exigência ilegal'],
            'ação anulatória de débito fiscal': ['anulatória', 'débito fiscal', 'nulidade'],
            'ação declaratória de inexistência de relação jurídico-tributária': ['declaratória', 'inexistência'],
            'embargos à execução fiscal': ['embargos', 'execução fiscal'],
            'exceção de pré-executividade': ['exceção', 'pré-executividade'],
            'repetição de indébito tributário': ['repetição', 'indébito', 'devolução'],
            'compensação tributária': ['compensação', 'compensar', 'créditos tributários'],
            'consulta tributária': ['consulta', 'planejamento'],
            'recurso administrativo': ['carf', 'conselho', 'recurso administrativo']
        }

        for tipo, palavras_chave in tipos.items():
            if any(palavra in contexto_lower for palavra in palavras_chave):
                return tipo

        return 'ação tributária'

    def _identificar_partes(self, contexto: str) -> Dict:
        """Identifica partes"""
        return {
            'contribuinte': 'Pessoa Física/Jurídica',
            'fisco': 'União/Estado/Município',
            'tributo': 'A identificar',
            'valor': 'R$ ...',
            'período': 'Ano/Mês de referência'
        }

    def _extrair_fatos(self, contexto: str) -> List[str]:
        """Extrai fatos tributariamente relevantes"""
        return [
            "Lançamento ou autuação fiscal",
            "Fato gerador do tributo",
            "Base de cálculo contestada",
            "Pagamento indevido ou a maior",
            "Fase do processo (administrativa/judicial)"
        ]

    def _identificar_tributos(self, contexto: str) -> List[str]:
        """Identifica tributos envolvidos"""
        contexto_lower = contexto.lower()

        tributos_mapa = {
            'IRPJ': ['irpj', 'imposto de renda pessoa jurídica'],
            'CSLL': ['csll', 'contribuição social lucro líquido'],
            'PIS': ['pis', 'programa integração social'],
            'COFINS': ['cofins'],
            'ICMS': ['icms', 'circulação de mercadorias'],
            'ISS': ['iss', 'imposto sobre serviços'],
            'IPI': ['ipi', 'produtos industrializados'],
            'Contribuições Previdenciárias': ['inss', 'previdência', 'contribuição previdenciária'],
            'ITBI': ['itbi', 'transmissão de bens'],
            'IPTU': ['iptu', 'predial territorial'],
            'IPVA': ['ipva', 'veículos']
        }

        tributos_identificados = []
        for tributo, palavras in tributos_mapa.items():
            if any(p in contexto_lower for p in palavras):
                tributos_identificados.append(tributo)

        return tributos_identificados if tributos_identificados else ['A identificar']

    def _identificar_fundamentos(self, contexto: str) -> List[str]:
        """Fundamentos jurídicos tributários"""
        return [
            "Código Tributário Nacional (CTN - Lei 5.172/66)",
            "Constituição Federal - Sistema Tributário Nacional (arts. 145-162)",
            "Princípios tributários: legalidade, anterioridade, irretroatividade, capacidade contributiva",
            "Jurisprudência consolidada do STF e STJ",
            "Súmulas vinculantes e de jurisprudência dominante",
            "Temas de repercussão geral"
        ]

    def _sugerir_pedidos(self, contexto: str, tipo_acao: str) -> List[str]:
        """Sugere pedidos para ações tributárias"""
        if 'mandado de segurança' in tipo_acao.lower():
            return [
                "Concessão da segurança para afastar a exigência do tributo",
                "Reconhecimento da ilegalidade do ato impugnado",
                "Suspensão da exigibilidade do crédito tributário",
                "Expedição de certidão positiva com efeitos de negativa"
            ]
        elif 'repetição' in tipo_acao.lower():
            return [
                "Restituição do indébito tributário",
                "Correção monetária pela SELIC",
                "Compensação com débitos futuros",
                "Reconhecimento do pagamento indevido"
            ]
        elif 'embargos' in tipo_acao.lower():
            return [
                "Extinção da execução fiscal",
                "Reconhecimento da nulidade da CDA",
                "Prescrição do crédito tributário",
                "Suspensão da exigibilidade (art. 151 CTN)"
            ]
        elif 'compensação' in tipo_acao.lower():
            return [
                "Homologação da compensação tributária",
                "Reconhecimento dos créditos a compensar",
                "Autorização para compensação",
                "Declaração de extinção do crédito tributário"
            ]
        else:
            return [
                "Reconhecimento do direito tributário pleiteado",
                "Aplicação dos princípios e garantias constitucionais"
            ]

    def _identificar_teses(self, contexto: str) -> List[str]:
        """Identifica teses tributárias aplicáveis"""
        teses_comuns = [
            "Exclusão do ICMS da base de cálculo do PIS/COFINS (Tema 69 STF)",
            "Não incidência de IRPJ/CSLL sobre SELIC de repetição de indébito",
            "Creditamento de PIS/COFINS sobre insumos (conceito amplo)",
            "Inconstitucionalidade de multa confiscatória (> 100%)",
            "Modulação de efeitos em julgamentos tributários",
            "Prescrição intercorrente em execuções fiscais",
            "Desconsideração da personalidade jurídica tributária"
        ]

        # Identificar qual tese se aplica ao contexto
        return ["Analisar teses aplicáveis ao caso concreto"]

    async def buscar_fundamentacao(self, analise: Dict) -> Dict:
        """Busca jurisprudências tributárias"""
        return {
            'jurisprudencias': [],
            'doutrinas': [],
            'súmulas': [],
            'temas_repercussão_geral': []
        }
