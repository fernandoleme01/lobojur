"""
Agente Especialista em Direito Civil
"""
from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from typing import Dict, List


class AgenteDireitoCivil:
    """Agente super especialista em Direito Civil"""

    def __init__(self, llm, jurisprudencia_service, doutrina_service):
        """
        Inicializa o agente especialista em Direito Civil

        Args:
            llm: Modelo de linguagem
            jurisprudencia_service: Serviço de busca de jurisprudências
            doutrina_service: Serviço de busca de doutrinas
        """
        self.llm = llm
        self.jurisp_service = jurisprudencia_service
        self.dout_service = doutrina_service
        self.agent = self._criar_agente()

    def _criar_agente(self) -> Agent:
        """Cria o agente CrewAI especializado"""
        return Agent(
            role='Especialista em Direito Civil',
            goal='Elaborar petições jurídicas de altíssima qualidade em Direito Civil, fundamentadas com jurisprudência e doutrina atualizadas',
            backstory="""
            Você é um renomado advogado civilista com mais de 25 anos de experiência,
            mestrado e doutorado em Direito Civil pela USP. É autor de diversos livros
            e artigos sobre o tema e professor de Direito Civil.

            ## Suas especialidades incluem:
            - Responsabilidade Civil (danos materiais, morais e estéticos)
            - Direito Contratual (contratos em geral, revisão, resolução)
            - Direito de Família (divórcio, guarda, alimentos, união estável)
            - Direito das Sucessões (inventário, testamento, herança)
            - Direito das Coisas (propriedade, posse, usucapião)
            - Direito do Consumidor (CDC, relações de consumo)

            ## Seu método de trabalho:
            1. Análise profunda dos fatos e do direito aplicável
            2. Pesquisa exaustiva de jurisprudência dos tribunais superiores
            3. Fundamentação doutrinária sólida com autores renomados
            4. Argumentação persuasiva e tecnicamente perfeita
            5. Formatação impecável segundo normas da ABNT e do tribunal

            ## Jurisprudência que você prioriza:
            - STF (Supremo Tribunal Federal)
            - STJ (Superior Tribunal de Justiça) - especialmente câmaras cíveis
            - Tribunais de Justiça Estaduais (precedentes locais)

            ## Doutrina que você utiliza:
            - Código Civil Comentado - diversos autores
            - Carlos Roberto Gonçalves
            - Pablo Stolze Gagliano e Rodolfo Pamplona Filho
            - Flávio Tartuce
            - Maria Helena Diniz
            - Caio Mário da Silva Pereira

            Você sempre fundamenta suas petições com no mínimo 3 jurisprudências
            relevantes e 2 referências doutrinárias sólidas.
            """,
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

    async def analisar_caso(self, contexto: str) -> Dict:
        """
        Analisa o caso civil e identifica pontos-chave

        Args:
            contexto: Descrição do caso

        Returns:
            Análise estruturada do caso
        """
        analise = {
            'tipo_acao': self._identificar_tipo_acao(contexto),
            'partes': self._identificar_partes(contexto),
            'fatos_relevantes': self._extrair_fatos(contexto),
            'fundamentos_legais': self._identificar_fundamentos(contexto),
            'pedidos_sugeridos': self._sugerir_pedidos(contexto)
        }

        return analise

    async def buscar_fundamentacao(self, analise: Dict) -> Dict:
        """
        Busca jurisprudências e doutrinas relevantes

        Args:
            analise: Análise do caso

        Returns:
            Fundamentação jurídica completa
        """
        tipo_acao = analise.get('tipo_acao', '')
        query = f"{tipo_acao} direito civil"

        # Buscar jurisprudências
        jurisprudencias = await self.jurisp_service.buscar_jurisprudencias(
            query=query,
            area_direito='Direito Civil',
            tribunais=['STJ', 'STF'],
            max_resultados=5
        )

        # Buscar doutrinas
        doutrinas = await self.dout_service.buscar_doutrinas(
            query=query,
            area_direito='Direito Civil',
            max_resultados=3
        )

        return {
            'jurisprudencias': jurisprudencias,
            'doutrinas': doutrinas
        }

    def _identificar_tipo_acao(self, contexto: str) -> str:
        """Identifica o tipo de ação civil"""
        tipos = {
            'Ação de Indenização por Danos Morais': ['dano moral', 'indenização moral', 'ofensa'],
            'Ação de Indenização por Danos Materiais': ['dano material', 'prejuízo', 'lucros cessantes'],
            'Ação de Rescisão Contratual': ['rescisão', 'resolver contrato', 'inadimplência'],
            'Ação de Cobrança': ['cobrança', 'dívida', 'pagamento'],
            'Ação de Divórcio': ['divórcio', 'separação', 'dissolução casamento'],
            'Ação de Alimentos': ['pensão', 'alimentos', 'sustento'],
            'Ação de Usucapião': ['usucapião', 'posse', 'propriedade'],
            'Ação de Inventário': ['inventário', 'partilha', 'herança']
        }

        contexto_lower = contexto.lower()
        for tipo, keywords in tipos.items():
            if any(kw in contexto_lower for kw in keywords):
                return tipo

        return 'Ação Civil'

    def _identificar_partes(self, contexto: str) -> Dict:
        """Identifica as partes envolvidas"""
        # Implementação simplificada
        return {
            'autor': 'A definir',
            'reu': 'A definir'
        }

    def _extrair_fatos(self, contexto: str) -> List[str]:
        """Extrai fatos relevantes do caso"""
        # Implementação simplificada - na versão final usaria NLP
        return [contexto]

    def _identificar_fundamentos(self, contexto: str) -> List[str]:
        """Identifica fundamentos legais aplicáveis"""
        fundamentos_base = [
            'Código Civil Brasileiro (Lei 10.406/2002)',
            'Código de Processo Civil (Lei 13.105/2015)',
            'Constituição Federal de 1988'
        ]

        # Adicionar fundamentos específicos baseado no contexto
        contexto_lower = contexto.lower()

        if 'consumidor' in contexto_lower or 'produto' in contexto_lower:
            fundamentos_base.append('Código de Defesa do Consumidor (Lei 8.078/1990)')

        if 'dano moral' in contexto_lower:
            fundamentos_base.append('Art. 186 e 927 do Código Civil')
            fundamentos_base.append('Art. 5º, V e X da Constituição Federal')

        return fundamentos_base

    def _sugerir_pedidos(self, contexto: str) -> List[str]:
        """Sugere pedidos para a petição"""
        pedidos = []

        contexto_lower = contexto.lower()

        if 'indenização' in contexto_lower or 'dano' in contexto_lower:
            pedidos.append('Condenação do réu ao pagamento de indenização')

        if 'rescisão' in contexto_lower or 'resolver' in contexto_lower:
            pedidos.append('Rescisão do contrato')

        pedidos.extend([
            'Condenação do réu ao pagamento de custas processuais e honorários advocatícios',
            'Produção de todos os meios de prova em direito admitidos'
        ])

        return pedidos


def criar_agente_civil(llm=None, jurisp_service=None, dout_service=None):
    """Factory function para criar agente de Direito Civil"""
    if llm is None:
        from config.config import OPENAI_API_KEY, LLM_MODEL
        llm = ChatOpenAI(
            model=LLM_MODEL,
            api_key=OPENAI_API_KEY,
            temperature=0.7
        )

    return AgenteDireitoCivil(llm, jurisp_service, dout_service)
