"""
Agente Filtro - Classifica a área jurídica do caso
"""
from crewai import Agent
from langchain_openai import ChatOpenAI
from typing import Dict


class AgenteFiltero:
    """Agente responsável por classificar a área jurídica do caso"""

    def __init__(self, llm):
        """
        Inicializa o agente filtro

        Args:
            llm: Modelo de linguagem a ser utilizado
        """
        self.llm = llm
        self.agent = self._criar_agente()

    def _criar_agente(self) -> Agent:
        """Cria o agente CrewAI"""
        return Agent(
            role='Especialista em Classificação Jurídica',
            goal='Analisar casos jurídicos e classificar corretamente a área do direito envolvida',
            backstory="""
            Você é um experiente advogado generalista com mais de 20 anos de experiência
            em diversas áreas do direito brasileiro. Sua especialidade é identificar
            rapidamente a área do direito envolvida em um caso, considerando todos os
            aspectos e nuances jurídicas.

            Você domina profundamente as seguintes áreas:
            - Direito Ambiental
            - Direito Civil
            - Direito Criminal
            - Direito Empresarial
            - Direito Agrário
            - Direito Tributário

            Sua análise é sempre precisa, considerando legislação, jurisprudência
            e a natureza dos fatos apresentados.
            """,
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

    def classificar_area(self, contexto: str) -> Dict:
        """
        Classifica a área do direito baseado no contexto fornecido

        Args:
            contexto: Texto descrevendo o caso jurídico

        Returns:
            Dicionário com área identificada e confiança
        """
        # TODO: Implementar lógica de classificação com o agente
        # Por enquanto, retorna uma implementação básica
        areas_keywords = {
            'Direito Ambiental': ['ambiental', 'meio ambiente', 'poluição', 'licenciamento', 'desmatamento'],
            'Direito Civil': ['contrato', 'indenização', 'danos morais', 'propriedade', 'família', 'herança'],
            'Direito Criminal': ['crime', 'penal', 'prisão', 'condenação', 'habeas corpus', 'réu'],
            'Direito Empresarial': ['sociedade', 'empresa', 'falência', 'recuperação judicial', 'sócio'],
            'Direito Agrário': ['terra', 'rural', 'agrícola', 'reforma agrária', 'propriedade rural'],
            'Direito Tributário': ['tributo', 'imposto', 'fiscal', 'icms', 'irpf', 'cofins']
        }

        contexto_lower = contexto.lower()
        scores = {}

        for area, keywords in areas_keywords.items():
            score = sum(1 for kw in keywords if kw in contexto_lower)
            if score > 0:
                scores[area] = score

        if scores:
            area_identificada = max(scores, key=scores.get)
            total_keywords = sum(scores.values())
            confianca = scores[area_identificada] / total_keywords
        else:
            area_identificada = 'Direito Civil'  # Padrão
            confianca = 0.3

        return {
            'area': area_identificada,
            'confianca': confianca,
            'scores': scores
        }


def criar_agente_filtro(llm=None) -> AgenteFiltero:
    """
    Factory function para criar o agente filtro

    Args:
        llm: Modelo de linguagem (opcional)

    Returns:
        Instância do AgenteFiltero
    """
    if llm is None:
        from config.config import OPENAI_API_KEY, LLM_MODEL
        llm = ChatOpenAI(
            model=LLM_MODEL,
            api_key=OPENAI_API_KEY,
            temperature=0.3
        )

    return AgenteFiltero(llm)
