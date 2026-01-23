"""Orquestrador principal que conecta todas as APIs (Claude, Gemini, Perplexity)."""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .claude_analyzer import ClaudeAnalyzer
from .gemini_analyzer import GeminiAnalyzer
from .perplexity_researcher import PerplexityResearcher
from .contract_analyzer import ContractAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class APIKeys:
    """Chaves de API necessárias."""
    claude_api_key: str
    gemini_api_key: str
    perplexity_api_key: str


class ReportOrchestrator:
    """
    Orquestrador que coordena todas as APIs para geração de laudos.

    - Perplexity: Pesquisas e scraping de informações atualizadas
    - Gemini: Análise profunda de documentos
    - Claude: Escrita de laudos e conexão das análises
    """

    def __init__(self, api_keys: APIKeys):
        """
        Inicializa orquestrador.

        Args:
            api_keys: Chaves de API
        """
        self.claude = ClaudeAnalyzer(api_keys.claude_api_key)
        self.gemini = GeminiAnalyzer(api_keys.gemini_api_key)
        self.perplexity = PerplexityResearcher(api_keys.perplexity_api_key)
        self.contract_analyzer = ContractAnalyzer(self.claude)

    async def generate_complete_report(
        self,
        contract_text: str,
        contract_metadata: Optional[Dict] = None,
        enable_web_research: bool = True,
        research_topics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Gera laudo completo usando todas as APIs em conjunto.

        Workflow:
        1. Gemini: Análise inicial e extração de dados estruturados
        2. Perplexity: Pesquisa de legislação, jurisprudência e validações
        3. Claude (Multi-agente): Análise detalhada do contrato
        4. Claude: Escrita do laudo final conectando todas as análises

        Args:
            contract_text: Texto do contrato
            contract_metadata: Metadados adicionais
            enable_web_research: Ativar pesquisas web
            research_topics: Tópicos específicos para pesquisar

        Returns:
            Laudo completo com todas as análises
        """
        logger.info("=" * 70)
        logger.info("INICIANDO GERAÇÃO DE LAUDO COMPLETO")
        logger.info("=" * 70)

        # ETAPA 1: Análise inicial com Gemini
        logger.info("\n[ETAPA 1] Análise inicial com Gemini...")
        gemini_analysis = self.gemini.analyze_document(
            contract_text,
            analysis_focus="comprehensive"
        )

        # Extração de dados estruturados
        logger.info("[ETAPA 1] Extraindo dados estruturados...")
        extracted_fields = self.gemini.extract_structured_information(
            contract_text,
            fields=[
                "Tipo de contrato",
                "Data de assinatura",
                "Partes contratantes",
                "Objeto do contrato",
                "Valor total",
                "Prazo de vigência",
                "Forma de pagamento",
                "Cláusulas de rescisão",
                "Foro",
                "Principais obrigações"
            ]
        )

        # ETAPA 2: Pesquisas com Perplexity (se habilitado)
        web_research_data = {}
        if enable_web_research:
            logger.info("\n[ETAPA 2] Pesquisas em tempo real com Perplexity...")

            # Determinar tópicos de pesquisa
            topics = research_topics or self._identify_research_topics(extracted_fields)

            # Executar pesquisas em paralelo
            research_tasks = []

            for topic in topics:
                research_tasks.append(
                    self.perplexity.research_legal_topic(topic, context=contract_text[:1000])
                )

            # Pesquisa de legislação aplicável
            contract_type = extracted_fields.get("Tipo de contrato", "")
            if contract_type:
                research_tasks.append(
                    self.perplexity.search(
                        f"Legislação brasileira aplicável a {contract_type}"
                    )
                )

            # Executar todas as pesquisas
            research_results = await asyncio.gather(*research_tasks, return_exceptions=True)

            web_research_data = {
                "topics_researched": topics,
                "results": [
                    r for r in research_results
                    if not isinstance(r, Exception)
                ]
            }

            logger.info(f"[ETAPA 2] Concluídas {len(web_research_data['results'])} pesquisas")

        # ETAPA 3: Análise multi-agente com Claude
        logger.info("\n[ETAPA 3] Análise multi-agente com Claude...")
        contract_analysis = self.contract_analyzer.analyze_contract(
            contract_text=contract_text,
            additional_context=contract_metadata,
            web_research_data=web_research_data
        )

        # ETAPA 4: Síntese e escrita do laudo final com Claude
        logger.info("\n[ETAPA 4] Escrita do laudo final com Claude...")
        final_report = await self._write_final_report(
            gemini_analysis=gemini_analysis,
            extracted_data=extracted_fields,
            web_research=web_research_data,
            contract_analysis=contract_analysis,
            contract_text=contract_text
        )

        logger.info("\n" + "=" * 70)
        logger.info("LAUDO COMPLETO GERADO COM SUCESSO")
        logger.info("=" * 70)

        return {
            "final_report": final_report,
            "gemini_analysis": gemini_analysis,
            "extracted_data": extracted_fields,
            "web_research": web_research_data,
            "contract_analysis": contract_analysis,
            "metadata": {
                "timestamp": str(asyncio.get_event_loop().time()),
                "apis_used": ["Gemini", "Perplexity", "Claude"],
                "research_enabled": enable_web_research
            }
        }

    async def _write_final_report(
        self,
        gemini_analysis: Dict,
        extracted_data: Dict,
        web_research: Dict,
        contract_analysis: Any,
        contract_text: str
    ) -> str:
        """
        Escreve laudo final usando Claude.

        Args:
            gemini_analysis: Análise do Gemini
            extracted_data: Dados estruturados extraídos
            web_research: Resultados de pesquisas
            contract_analysis: Análise multi-agente
            contract_text: Texto original do contrato

        Returns:
            Laudo técnico completo
        """
        prompt = f"""
Você é um perito técnico judicial especializado em elaboração de laudos.
Com base em todas as análises realizadas, elabore um LAUDO TÉCNICO PERICIAL completo,
formal e estruturado.

═══════════════════════════════════════════════════════════════
DADOS DISPONÍVEIS PARA O LAUDO
═══════════════════════════════════════════════════════════════

1. ANÁLISE INICIAL (Gemini):
{gemini_analysis.get('analysis', '')}

2. DADOS ESTRUTURADOS EXTRAÍDOS:
{self._format_dict(extracted_data)}

3. PESQUISAS WEB REALIZADAS:
{self._format_web_research(web_research)}

4. ANÁLISE ESTRUTURAL DO CONTRATO:
{contract_analysis.contract_summary}

5. ANÁLISE DAS PARTES:
{contract_analysis.parties_analysis}

6. ANÁLISE FINANCEIRA:
{contract_analysis.financial_analysis}

7. ANÁLISE JURÍDICA E RISCOS:
{contract_analysis.legal_risks}

8. RECOMENDAÇÕES:
{contract_analysis.recommendations}

═══════════════════════════════════════════════════════════════
TAREFA
═══════════════════════════════════════════════════════════════

Elabore um LAUDO TÉCNICO PERICIAL COMPLETO seguindo a estrutura:

1. IDENTIFICAÇÃO
   - Número do laudo
   - Data
   - Partes envolvidas

2. PREÂMBULO
   - Objetivo
   - Metodologia

3. ANÁLISE TÉCNICA
   - Caracterização do contrato
   - Análise de cláusulas
   - Obrigações das partes

4. ASPECTOS JURÍDICOS
   - Conformidade legal
   - Base legal aplicável
   - Riscos jurídicos

5. ASPECTOS FINANCEIROS
   - Valores e condições
   - Projeções
   - Riscos financeiros

6. AVALIAÇÃO DE RISCOS
   - Matriz de riscos
   - Detalhamento
   - Mitigações

7. CONCLUSÃO
   - Síntese
   - Parecer técnico
   - Recomendações

IMPORTANTE:
- Use linguagem técnica e formal
- Cite legislação específica quando relevante
- Integre harmoniosamente todas as análises fornecidas
- Seja preciso e objetivo
- Mantenha estrutura clara e profissional
- O laudo deve estar completo e pronto para uso judicial
"""

        system_prompt = """
Você é um perito técnico judicial com 20 anos de experiência em elaboração de laudos.
Seus laudos são reconhecidos por sua qualidade técnica, precisão e conformidade com
normas processuais brasileiras.

Escreva o laudo de forma impecável, integrando todas as informações fornecidas
em um documento coeso, técnico e profissional.
"""

        final_report = self.claude.analyze_text(
            text=prompt,
            prompt="Elabore o laudo técnico pericial completo conforme solicitado acima.",
            system_prompt=system_prompt,
            temperature=0.3
        )

        return final_report

    def _identify_research_topics(self, extracted_data: Dict) -> List[str]:
        """Identifica tópicos para pesquisa baseado nos dados extraídos."""
        topics = []

        contract_type = extracted_data.get("Tipo de contrato", "")
        if contract_type:
            topics.append(f"Legislação aplicável a {contract_type}")
            topics.append(f"Jurisprudência recente sobre {contract_type}")

        object_contract = extracted_data.get("Objeto do contrato", "")
        if object_contract:
            topics.append(f"Regulamentação sobre {object_contract}")

        return topics[:5]  # Limitar a 5 tópicos

    def _format_dict(self, data: Dict) -> str:
        """Formata dicionário para texto."""
        return "\n".join([f"- {k}: {v}" for k, v in data.items()])

    def _format_web_research(self, research: Dict) -> str:
        """Formata resultados de pesquisa."""
        if not research:
            return "Pesquisas web não realizadas."

        formatted = f"Tópicos pesquisados: {', '.join(research.get('topics_researched', []))}\n\n"

        for idx, result in enumerate(research.get('results', []), 1):
            formatted += f"\nPesquisa {idx}:\n"
            formatted += f"Resposta: {result.get('answer', '')[:500]}...\n"
            formatted += f"Fontes: {len(result.get('citations', []))} citações\n"

        return formatted

    async def quick_analysis(
        self,
        contract_text: str
    ) -> Dict[str, Any]:
        """
        Análise rápida sem pesquisas web.

        Args:
            contract_text: Texto do contrato

        Returns:
            Análise básica
        """
        logger.info("Executando análise rápida...")

        # Usar apenas Gemini e Claude
        gemini_summary = self.gemini.generate_summary(contract_text, "executive")

        claude_analysis = self.claude.analyze_contract(
            contract_text,
            analysis_type="summary"
        )

        return {
            "gemini_summary": gemini_summary,
            "claude_analysis": claude_analysis,
            "type": "quick_analysis"
        }

    async def research_only(
        self,
        topics: List[str],
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Apenas pesquisas web sem análise de contrato.

        Args:
            topics: Tópicos para pesquisar
            context: Contexto adicional

        Returns:
            Resultados das pesquisas
        """
        logger.info(f"Pesquisando {len(topics)} tópicos...")

        research_tasks = [
            self.perplexity.research_legal_topic(topic, context)
            for topic in topics
        ]

        results = await asyncio.gather(*research_tasks, return_exceptions=True)

        return {
            "topics": topics,
            "results": [r for r in results if not isinstance(r, Exception)],
            "type": "research_only"
        }
