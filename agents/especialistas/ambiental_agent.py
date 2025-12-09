"""
Agente Especialista em Direito Ambiental
"""
from typing import Dict, List


class AgenteDireitoAmbiental:
    """Agente especializado em Direito Ambiental"""

    def __init__(self, llm, jurisprudencia_service, doutrina_service):
        self.llm = llm
        self.jurisprudencia_service = jurisprudencia_service
        self.doutrina_service = doutrina_service

        self.backstory = """
        Você é um advogado ambientalista, especializado em:
        - Licenciamento ambiental
        - Crimes ambientais (Lei 9.605/98)
        - Áreas de preservação permanente (APP)
        - Reserva legal
        - Código Florestal (Lei 12.651/12)
        - Política Nacional do Meio Ambiente
        - Política Nacional de Resíduos Sólidos
        - Unidades de conservação
        - Responsabilidade civil ambiental
        - TAC - Termo de Ajustamento de Conduta

        Legislação principal:
        - Constituição Federal (art. 225)
        - Lei 6.938/81 (Política Nacional do Meio Ambiente)
        - Lei 9.605/98 (Crimes Ambientais)
        - Lei 12.651/12 (Código Florestal)
        - Lei 12.305/10 (Resíduos Sólidos)
        - Resoluções CONAMA

        Doutrinadores:
        - Paulo Affonso Leme Machado
        - Édis Milaré
        - José Afonso da Silva
        - Frederico Amado
        """

    async def analisar_caso(self, contexto: str) -> Dict:
        """Analisa caso ambiental"""
        tipo_acao = self._identificar_tipo_acao(contexto)
        partes = self._identificar_partes(contexto)
        fatos = self._extrair_fatos(contexto)
        infraes = self._identificar_infracoes(contexto)
        fundamentos = self._identificar_fundamentos(contexto)
        pedidos = self._sugerir_pedidos(contexto, tipo_acao)

        return {
            'tipo_acao': tipo_acao,
            'partes': partes,
            'fatos': fatos,
            'infracoes_ambientais': infraes,
            'fundamentos': fundamentos,
            'pedidos': pedidos,
            'licencas_necessarias': self._identificar_licencas(contexto)
        }

    def _identificar_tipo_acao(self, contexto: str) -> str:
        """Identifica tipo de ação ambiental"""
        contexto_lower = contexto.lower()

        tipos = {
            'ação civil pública ambiental': ['acp', 'ação civil pública', 'dano ambiental coletivo'],
            'ação popular ambiental': ['ação popular', 'cidadão'],
            'mandado de segurança ambiental': ['mandado de segurança', 'licença negada'],
            'defesa em crime ambiental': ['crime ambiental', 'lei 9.605'],
            'TAC - Termo de Ajustamento de Conduta': ['tac', 'termo de ajustamento'],
            'recuperação de área degradada': ['recuperação', 'área degradada', 'degradação'],
            'licenciamento ambiental': ['licença', 'licenciamento', 'lp', 'li', 'lo']
        }

        for tipo, palavras_chave in tipos.items():
            if any(palavra in contexto_lower for palavra in palavras_chave):
                return tipo

        return 'ação ambiental'

    def _identificar_partes(self, contexto: str) -> Dict:
        """Identifica partes"""
        return {
            'autor/interessado': 'A identificar',
            'réu/infrator': 'A identificar',
            'órgão ambiental': 'IBAMA/ICMBio/Órgão Estadual',
            'ministério_público': 'Se ACP'
        }

    def _extrair_fatos(self, contexto: str) -> List[str]:
        """Extrai fatos ambientalmente relevantes"""
        return [
            "Descrição do dano ou risco ambiental",
            "Localização e área afetada",
            "Recursos naturais impactados",
            "Existência de licenças ou autorizações"
        ]

    def _identificar_infracoes(self, contexto: str) -> List[str]:
        """Identifica possíveis infrações ambientais"""
        contexto_lower = contexto.lower()

        infracoes = {
            'Desmatamento ilegal (art. 38 Lei 9.605)': ['desmatamento', 'derrubada', 'corte de árvores'],
            'Poluição hídrica (art. 54 Lei 9.605)': ['poluição', 'contaminação água', 'rio'],
            'Maus-tratos a animais (art. 32 Lei 9.605)': ['animal', 'maus-tratos', 'crueldade'],
            'Queimada irregular (art. 41 Lei 9.605)': ['queimada', 'fogo', 'incêndio'],
            'Obra sem licença (art. 60 Lei 9.605)': ['obra', 'construção', 'sem licença'],
            'Pesca ilegal (art. 34 Lei 9.605)': ['pesca', 'período defeso'],
            'Comércio de fauna silvestre (art. 29 Lei 9.605)': ['tráfico', 'comércio animais']
        }

        resultado = []
        for infracao, palavras in infracoes.items():
            if any(p in contexto_lower for p in palavras):
                resultado.append(infracao)

        return resultado if resultado else ['A ser analisada']

    def _identificar_fundamentos(self, contexto: str) -> List[str]:
        """Fundamentos jurídicos ambientais"""
        return [
            "Constituição Federal, art. 225 (direito ao meio ambiente ecologicamente equilibrado)",
            "Lei 6.938/81 (Política Nacional do Meio Ambiente)",
            "Lei 9.605/98 (Crimes Ambientais)",
            "Lei 12.651/12 (Código Florestal)",
            "Princípios: poluidor-pagador, precaução, prevenção, desenvolvimento sustentável",
            "Responsabilidade objetiva em matéria ambiental",
            "Jurisprudência do STJ e Tribunais Regionais"
        ]

    def _sugerir_pedidos(self, contexto: str, tipo_acao: str) -> List[str]:
        """Sugere pedidos para ações ambientais"""
        if 'crime' in tipo_acao.lower():
            return [
                "Trancamento da ação penal (se caso)",
                "Absolvição por atipicidade",
                "Reconhecimento de excludentes de ilicitude",
                "Suspensão condicional do processo (art. 89 Lei 9.099/95)"
            ]
        elif 'licença' in tipo_acao.lower() or 'licenciamento' in tipo_acao.lower():
            return [
                "Concessão de licença prévia (LP)",
                "Concessão de licença de instalação (LI)",
                "Concessão de licença de operação (LO)",
                "Renovação de licença ambiental"
            ]
        elif 'dano' in contexto.lower():
            return [
                "Condenação do réu à recuperação da área degradada",
                "Indenização por danos ambientais",
                "Obrigação de fazer (medidas de mitigação)",
                "Aplicação do princípio do poluidor-pagador"
            ]
        else:
            return [
                "Reconhecimento do direito pleiteado",
                "Aplicação da legislação ambiental",
                "Tutela do meio ambiente"
            ]

    def _identificar_licencas(self, contexto: str) -> List[str]:
        """Identifica licenças ambientais necessárias"""
        return [
            "LP - Licença Prévia (viabilidade)",
            "LI - Licença de Instalação (construção)",
            "LO - Licença de Operação (funcionamento)",
            "Autorização de Supressão Vegetal",
            "Outorga de Uso de Recursos Hídricos"
        ]

    async def buscar_fundamentacao(self, analise: Dict) -> Dict:
        """Busca jurisprudências ambientais"""
        return {
            'jurisprudencias': [],
            'doutrinas': [],
            'resoluções_conama': []
        }
