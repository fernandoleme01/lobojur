"""
Agente Especialista em Direito Agrário
"""
from typing import Dict, List


class AgenteDireitoAgrario:
    """Agente especializado em Direito Agrário e Fundiário"""

    def __init__(self, llm, jurisprudencia_service, doutrina_service):
        self.llm = llm
        self.jurisprudencia_service = jurisprudencia_service
        self.doutrina_service = doutrina_service

        self.backstory = """
        Você é um advogado especialista em Direito Agrário e Fundiário:
        - Reforma agrária
        - Desapropriação para fins de reforma agrária
        - Usucapião rural (pro labore)
        - Contratos agrários (arrendamento, parceria, comodato rural)
        - Regularização fundiária rural
        - Demarcação de terras
        - Questões indígenas e quilombolas
        - Política agrícola
        - Crédito rural
        - ITR - Imposto Territorial Rural

        Legislação principal:
        - Constituição Federal (arts. 184 a 191)
        - Estatuto da Terra (Lei 4.504/64)
        - Lei 8.629/93 (Reforma Agrária)
        - Lei 13.465/17 (Regularização Fundiária)
        - Decreto 59.566/66 (Contratos Agrários)
        - Lei 11.326/06 (Agricultura Familiar)

        Doutrinadores:
        - Benedito Ferreira Marques
        - Paulo Torminn Borges
        - Raymundo Laranjeira
        """

    async def analisar_caso(self, contexto: str) -> Dict:
        """Analisa caso agrário"""
        tipo_acao = self._identificar_tipo_acao(contexto)
        partes = self._identificar_partes(contexto)
        fatos = self._extrair_fatos(contexto)
        fundamentos = self._identificar_fundamentos(contexto)
        pedidos = self._sugerir_pedidos(contexto, tipo_acao)
        imovel = self._analisar_imovel_rural(contexto)

        return {
            'tipo_acao': tipo_acao,
            'partes': partes,
            'fatos': fatos,
            'fundamentos': fundamentos,
            'pedidos': pedidos,
            'caracteristicas_imovel': imovel
        }

    def _identificar_tipo_acao(self, contexto: str) -> str:
        """Identifica tipo de ação agrária"""
        contexto_lower = contexto.lower()

        tipos = {
            'usucapião rural (pro labore)': ['usucapião', 'posse agrária', 'cultura efetiva'],
            'desapropriação agrária': ['desapropriação', 'improdutiva', 'reforma agrária'],
            'ação de despejo agrário': ['despejo', 'comodato rural', 'arrendamento'],
            'reintegração de posse rural': ['reintegração', 'esbulho', 'invasão'],
            'ação de nunciação de obra nova rural': ['obra nova', 'construção irregular'],
            'ação de cobrança rural': ['arrendamento', 'parceria agrícola', 'inadimplência'],
            'regularização fundiária': ['regularização', 'titulação', 'terra devoluta'],
            'demarcatória de terras': ['demarcação', 'limites', 'divisas']
        }

        for tipo, palavras_chave in tipos.items():
            if any(palavra in contexto_lower for palavra em palavras_chave):
                return tipo

        return 'ação agrária'

    def _identificar_partes(self, contexto: str) -> Dict:
        """Identifica partes da ação agrária"""
        return {
            'proprietário/posseiro': 'A identificar',
            'trabalhador_rural': 'A identificar',
            'órgão_fundiário': 'INCRA/órgão estadual',
            'tipo_posse': 'mansa e pacífica / contestada'
        }

    def _extrair_fatos(self, contexto: str) -> List[str]:
        """Extrai fatos agrariamente relevantes"""
        return [
            "Características do imóvel rural (área, localização)",
            "Forma de ocupação/posse",
            "Exploração/produtividade da terra",
            "Cumprimento da função social",
            "Documentação existente (matrícula, CAR, ITR)"
        ]

    def _identificar_fundamentos(self, contexto: str) -> List[str]:
        """Fundamentos jurídicos agrários"""
        return [
            "Constituição Federal - arts. 184-191 (Política Agrícola e Fundiária)",
            "Estatuto da Terra (Lei 4.504/64)",
            "Princípio da função social da propriedade rural",
            "Lei 8.629/93 (Reforma Agrária)",
            "Lei 13.465/17 (Regularização Fundiária)",
            "Jurisprudência agrária do STJ e TRFs"
        ]

    def _sugerir_pedidos(self, contexto: str, tipo_acao: str) -> List[str]:
        """Sugere pedidos para ações agrárias"""
        if 'usucapião' in tipo_acao.lower():
            return [
                "Reconhecimento da posse agrária qualificada",
                "Declaração de domínio por usucapião rural (art. 191 CF)",
                "Registro imobiliário da área",
                "Cancelamento de eventuais ônus sobre o imóvel"
            ]
        elif 'desapropriação' in tipo_acao.lower():
            return [
                "Declaração de nulidade do decreto expropriatório (se defesa)",
                "Justa e prévia indenização em TDA",
                "Comprovação da produtividade do imóvel",
                "Exclusão da área da reforma agrária"
            ]
        elif 'regularização' in tipo_acao.lower():
            return [
                "Regularização fundiária do imóvel rural",
                "Emissão de título de domínio",
                "Registro no CAR (Cadastro Ambiental Rural)",
                "Retificação de matrícula"
            ]
        else:
            return [
                "Reconhecimento do direito agrário pleiteado",
                "Aplicação da legislação fundiária"
            ]

    def _analisar_imovel_rural(self, contexto: str) -> Dict:
        """Analisa características do imóvel rural"""
        return {
            'área_total': 'A mensurar (hectares)',
            'exploração_economica': 'agricultura/pecuária/mista',
            'produtividade': 'produtiva/improdutiva',
            'função_social': 'cumpre/não cumpre',
            'módulos_fiscais': 'Calcular conforme município',
            'cadastros': ['CAR', 'ITR', 'CCIR - INCRA'],
            'averbações_ambientais': 'Reserva Legal/APP'
        }

    async def buscar_fundamentacao(self, analise: Dict) -> Dict:
        """Busca jurisprudências agrárias"""
        return {
            'jurisprudencias': [],
            'doutrinas': [],
            'precedentes_trf': []
        }
