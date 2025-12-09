"""
Agente Especialista em Direito Criminal
"""
from typing import Dict, List


class AgenteDireitoCriminal:
    """Agente especializado em Direito Criminal"""

    def __init__(self, llm, jurisprudencia_service, doutrina_service):
        self.llm = llm
        self.jurisprudencia_service = jurisprudencia_service
        self.doutrina_service = doutrina_service

        self.backstory = """
        Você é um advogado criminalista experiente, especializado em:
        - Crimes contra a pessoa (homicídio, lesão corporal)
        - Crimes contra o patrimônio (furto, roubo, estelionato)
        - Crimes de trânsito
        - Tráfico de drogas e Lei 11.343/06
        - Crimes tributários e contra ordem econômica
        - Processo penal e medidas cautelares
        - Tribunal do Júri
        - Habeas Corpus e recursos criminais

        Legislação principal:
        - Código Penal (Decreto-Lei 2.848/1940)
        - Código de Processo Penal (Decreto-Lei 3.689/1941)
        - Lei 11.343/06 (Lei de Drogas)
        - Lei 9.099/95 (Juizados Especiais)
        - Lei 12.850/13 (Organização Criminosa)

        Doutrinadores:
        - Guilherme de Souza Nucci
        - Fernando Capez
        - Rogério Sanches Cunha
        - Cleber Masson
        - Renato Brasileiro
        """

    async def analisar_caso(self, contexto: str) -> Dict:
        """
        Analisa caso criminal

        Returns:
            {
                'tipo_acao': str,
                'partes': dict,
                'fatos': list,
                'tipificacao': list,
                'fundamentos': list,
                'pedidos': list,
                'medidas_cautelares': list
            }
        """
        tipo_acao = self._identificar_tipo_acao(contexto)
        partes = self._identificar_partes(contexto)
        fatos = self._extrair_fatos(contexto)
        tipificacao = self._identificar_tipificacao(contexto)
        fundamentos = self._identificar_fundamentos(contexto)
        pedidos = self._sugerir_pedidos(contexto, tipo_acao)
        medidas = self._sugerir_medidas_cautelares(contexto)

        return {
            'tipo_acao': tipo_acao,
            'partes': partes,
            'fatos': fatos,
            'tipificacao': tipificacao,
            'fundamentos': fundamentos,
            'pedidos': pedidos,
            'medidas_cautelares': medidas
        }

    def _identificar_tipo_acao(self, contexto: str) -> str:
        """Identifica tipo de ação criminal"""
        contexto_lower = contexto.lower()

        tipos = {
            'habeas corpus': ['habeas', 'prisão ilegal', 'constrangimento'],
            'queixa-crime': ['queixa', 'ação penal privada'],
            'denúncia': ['denúncia', 'ação penal pública'],
            'defesa prévia': ['defesa prévia', 'resposta à acusação'],
            'alegações finais': ['alegações finais', 'memoriais'],
            'recurso em sentido estrito': ['recurso em sentido estrito'],
            'apelação criminal': ['apelação', 'sentença condenatória'],
            'revisão criminal': ['revisão criminal'],
            'execução penal': ['execução', 'livramento condicional', 'progressão']
        }

        for tipo, palavras_chave in tipos.items():
            if any(palavra in contexto_lower for palavra in palavras_chave):
                return tipo

        return 'ação penal'

    def _identificar_partes(self, contexto: str) -> Dict:
        """Identifica partes do processo criminal"""
        # Simplificado - usar LLM para extração real
        return {
            'réu/acusado': 'A identificar',
            'vítima': 'A identificar',
            'autoridade coatora': 'A identificar (se HC)',
            'tipo_acao_penal': 'pública incondicionada'  # ou privada, pública condicionada
        }

    def _extrair_fatos(self, contexto: str) -> List[str]:
        """Extrai fatos criminalmente relevantes"""
        # Usar LLM para extração
        return [
            "Fato 1: [Descrever conduta típica]",
            "Fato 2: [Contexto do crime]",
            "Fato 3: [Circunstâncias]"
        ]

    def _identificar_tipificacao(self, contexto: str) -> List[str]:
        """Identifica possível tipificação criminal"""
        contexto_lower = contexto.lower()

        crimes_comuns = {
            'homicídio': ['matar', 'morte', 'homicídio', 'matou'],
            'furto (art. 155 CP)': ['furto', 'subtraiu', 'subtração'],
            'roubo (art. 157 CP)': ['roubo', 'grave ameaça', 'violência'],
            'estelionato (art. 171 CP)': ['estelionato', 'fraude', 'artifício'],
            'tráfico de drogas (art. 33 Lei 11.343)': ['tráfico', 'droga', 'entorpecente'],
            'lesão corporal (art. 129 CP)': ['lesão', 'agressão', 'ferimento'],
            'injúria (art. 140 CP)': ['injúria', 'ofensa à honra'],
            'difamação (art. 139 CP)': ['difamação', 'fato ofensivo'],
            'calúnia (art. 138 CP)': ['calúnia', 'falso crime']
        }

        tipificacoes = []
        for crime, palavras in crimes_comuns.items():
            if any(p in contexto_lower for p in palavras):
                tipificacoes.append(crime)

        return tipificacoes if tipificacoes else ['A ser definida conforme análise']

    def _identificar_fundamentos(self, contexto: str) -> List[str]:
        """Fundamentos jurídicos para defesa ou acusação"""
        return [
            "Código Penal - artigos aplicáveis",
            "Código de Processo Penal",
            "Jurisprudência do STF e STJ",
            "Princípios constitucionais (presunção de inocência, ampla defesa)",
            "Súmulas aplicáveis"
        ]

    def _sugerir_pedidos(self, contexto: str, tipo_acao: str) -> List[str]:
        """Sugere pedidos conforme tipo de ação"""
        if 'habeas corpus' in tipo_acao.lower():
            return [
                "Concessão da ordem de Habeas Corpus",
                "Revogação da prisão preventiva",
                "Concessão de liberdade provisória",
                "Aplicação de medidas cautelares alternativas"
            ]
        elif 'defesa' in tipo_acao.lower():
            return [
                "Absolvição do réu",
                "Subsidiariamente, desclassificação do crime",
                "Reconhecimento de atenuantes",
                "Aplicação do regime aberto"
            ]
        elif 'execução' in tipo_acao.lower():
            return [
                "Progressão de regime",
                "Livramento condicional",
                "Remição da pena",
                "Indulto ou comutação"
            ]
        else:
            return [
                "Aplicação da lei penal conforme os fatos",
                "Observância do devido processo legal"
            ]

    def _sugerir_medidas_cautelares(self, contexto: str) -> List[str]:
        """Sugere medidas cautelares (art. 319 CPP)"""
        return [
            "Comparecimento periódico em juízo",
            "Proibição de acesso ou frequência a determinados lugares",
            "Proibição de contato com vítima ou testemunhas",
            "Proibição de ausentar-se da comarca",
            "Recolhimento domiciliar no período noturno",
            "Suspensão do exercício de função pública",
            "Monitoramento eletrônico"
        ]

    async def buscar_fundamentacao(self, analise: Dict) -> Dict:
        """Busca jurisprudências e doutrinas criminais"""
        # Usar serviços de busca
        jurisprudencias = []
        doutrinas = []

        # Buscar baseado na tipificação
        for crime in analise.get('tipificacao', []):
            # Implementar busca real
            pass

        return {
            'jurisprudencias': jurisprudencias,
            'doutrinas': doutrinas
        }
