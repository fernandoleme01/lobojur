"""Analisador de contratos usando sistema multi-agente com CrewAI."""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """Resultado da análise de contrato."""
    contract_summary: str
    parties_analysis: str
    financial_analysis: str
    legal_risks: str
    recommendations: str
    technical_report: str
    full_analysis: Dict[str, Any]


class ContractAnalyzer:
    """
    Analisador de contratos usando sistema multi-agente.

    Orquestra diferentes agentes especializados para análise completa.
    """

    def __init__(self, llm_client):
        """
        Inicializa o analisador.

        Args:
            llm_client: Cliente LLM (Claude, OpenAI, etc.)
        """
        self.llm = llm_client
        self.agents_config = self._setup_agents()

    def _setup_agents(self) -> Dict[str, Dict[str, str]]:
        """Configura os agentes especializados."""
        return {
            "contract_reader": {
                "role": "Analista de Contratos",
                "goal": "Ler e compreender a estrutura completa do contrato",
                "backstory": """Você é um especialista em leitura e interpretação de contratos
                legais com 15 anos de experiência. Você identifica rapidamente a estrutura,
                partes envolvidas e cláusulas principais."""
            },
            "legal_expert": {
                "role": "Advogado Especialista",
                "goal": "Identificar riscos jurídicos e conformidade legal",
                "backstory": """Você é um advogado sênior especializado em direito contratual
                brasileiro, com expertise em identificar cláusulas abusivas, riscos legais e
                questões de conformidade com Código Civil e CDC."""
            },
            "financial_analyst": {
                "role": "Analista Financeiro",
                "goal": "Analisar aspectos financeiros e econômicos do contrato",
                "backstory": """Você é um analista financeiro com foco em contratos, especializado
                em identificar valores, condições de pagamento, reajustes e impactos econômicos."""
            },
            "risk_assessor": {
                "role": "Assessor de Riscos",
                "goal": "Avaliar e quantificar riscos do contrato",
                "backstory": """Você é um especialista em gestão de riscos contratuais, capaz de
                identificar, classificar e propor mitigações para riscos jurídicos, financeiros e
                operacionais."""
            },
            "technical_writer": {
                "role": "Perito Técnico",
                "goal": "Elaborar laudo técnico formal e estruturado",
                "backstory": """Você é um perito técnico judicial com vasta experiência em
                elaboração de laudos técnicos jurídicos, seguindo rigorosamente os padrões
                técnicos e normas processuais."""
            }
        }

    def analyze_contract(
        self,
        contract_text: str,
        additional_context: Optional[Dict[str, Any]] = None,
        web_research_data: Optional[Dict[str, Any]] = None
    ) -> AnalysisResult:
        """
        Analisa contrato usando equipe de agentes especializados.

        Args:
            contract_text: Texto do contrato extraído
            additional_context: Contexto adicional (ex: jurisprudências)
            web_research_data: Dados de pesquisa web (scraping)

        Returns:
            Resultado completo da análise
        """
        logger.info("Iniciando análise multi-agente do contrato...")

        # Etapa 1: Análise estrutural pelo Contract Reader
        logger.info("Agente 1: Análise estrutural...")
        contract_summary = self._run_agent_task(
            agent="contract_reader",
            task=f"""
Analise a estrutura deste contrato e forneça:

1. Tipo de contrato
2. Partes envolvidas (identificação completa)
3. Objeto do contrato
4. Principais cláusulas identificadas
5. Estrutura geral do documento

Contrato:
{contract_text}
"""
        )

        # Etapa 2: Análise das partes
        logger.info("Agente 2: Análise das partes envolvidas...")
        parties_analysis = self._run_agent_task(
            agent="contract_reader",
            task=f"""
Com base na análise inicial:

{contract_summary}

Extraia e analise detalhadamente:
1. Qualificação completa de cada parte
2. Capacidade jurídica
3. Representantes legais
4. Endereços e contatos
5. CNPJ/CPF quando disponível

Contrato:
{contract_text[:2000]}
"""
        )

        # Etapa 3: Análise financeira
        logger.info("Agente 3: Análise financeira...")
        financial_analysis = self._run_agent_task(
            agent="financial_analyst",
            task=f"""
Analise os aspectos financeiros do contrato:

1. Valores totais e parciais
2. Formas de pagamento
3. Prazos de pagamento
4. Índices de reajuste
5. Multas e penalidades financeiras
6. Garantias financeiras
7. Projeção de custos totais

Contexto do contrato:
{contract_summary}

Contrato completo:
{contract_text}
"""
        )

        # Etapa 4: Análise jurídica e riscos
        logger.info("Agente 4: Análise jurídica e identificação de riscos...")
        legal_risks = self._run_agent_task(
            agent="legal_expert",
            task=f"""
Realize análise jurídica completa:

1. Conformidade com legislação brasileira
2. Cláusulas potencialmente abusivas
3. Riscos jurídicos identificados
4. Questões de CDC (se aplicável)
5. Cláusulas de foro e jurisdição
6. Aspectos de rescisão contratual
7. Prazos prescricionais relevantes

Análise inicial:
{contract_summary}

Análise financeira:
{financial_analysis}

{f"Dados de pesquisa web: {web_research_data}" if web_research_data else ""}

Contrato:
{contract_text}
"""
        )

        # Etapa 5: Avaliação de riscos consolidada
        logger.info("Agente 5: Avaliação consolidada de riscos...")
        risk_assessment = self._run_agent_task(
            agent="risk_assessor",
            task=f"""
Com base em todas as análises anteriores, elabore uma avaliação de riscos consolidada:

ANÁLISE ESTRUTURAL:
{contract_summary}

ANÁLISE FINANCEIRA:
{financial_analysis}

ANÁLISE JURÍDICA:
{legal_risks}

Forneça:
1. Matriz de riscos (Alto/Médio/Baixo)
2. Quantificação de riscos financeiros
3. Probabilidade de litígio
4. Recomendações de mitigação específicas
5. Plano de ação sugerido
"""
        )

        # Etapa 6: Geração do laudo técnico
        logger.info("Agente 6: Elaboração do laudo técnico...")
        technical_report = self._run_agent_task(
            agent="technical_writer",
            task=f"""
Elabore um LAUDO TÉCNICO PERICIAL completo e formal com base em todas as análises:

ANÁLISE ESTRUTURAL:
{contract_summary}

PARTES ENVOLVIDAS:
{parties_analysis}

ANÁLISE FINANCEIRA:
{financial_analysis}

ANÁLISE JURÍDICA:
{legal_risks}

AVALIAÇÃO DE RISCOS:
{risk_assessment}

O laudo deve conter:

1. IDENTIFICAÇÃO
   - Número do laudo
   - Data
   - Perito responsável
   - Partes envolvidas

2. PREÂMBULO
   - Objetivo do laudo
   - Quesitos a responder
   - Metodologia utilizada

3. ANÁLISE TÉCNICA
   - Documentos analisados
   - Constatações técnicas
   - Análise detalhada do contrato

4. ASPECTOS JURÍDICOS
   - Conformidade legal
   - Riscos identificados
   - Base legal aplicável

5. ASPECTOS FINANCEIROS
   - Valores e condições
   - Projeções
   - Impactos econômicos

6. RESPOSTAS AOS QUESITOS
   - Resposta técnica fundamentada

7. CONCLUSÃO
   - Síntese da análise
   - Parecer técnico

8. ENCERRAMENTO
   - Local e data
   - Assinatura (campo)

Utilize linguagem técnica, formal e objetiva.
"""
        )

        return AnalysisResult(
            contract_summary=contract_summary,
            parties_analysis=parties_analysis,
            financial_analysis=financial_analysis,
            legal_risks=legal_risks,
            recommendations=risk_assessment,
            technical_report=technical_report,
            full_analysis={
                "structural": contract_summary,
                "parties": parties_analysis,
                "financial": financial_analysis,
                "legal": legal_risks,
                "risks": risk_assessment,
                "report": technical_report
            }
        )

    def _run_agent_task(self, agent: str, task: str) -> str:
        """
        Executa uma tarefa por um agente específico.

        Args:
            agent: Nome do agente
            task: Descrição da tarefa

        Returns:
            Resultado da tarefa
        """
        agent_config = self.agents_config[agent]

        system_prompt = f"""
Você é o {agent_config['role']}.
Objetivo: {agent_config['goal']}
Contexto: {agent_config['backstory']}

Execute a tarefa com excelência, utilizando todo seu conhecimento especializado.
"""

        try:
            result = self.llm.analyze_text(
                text=task,
                prompt="Execute a tarefa descrita acima com máxima qualidade e precisão técnica.",
                system_prompt=system_prompt,
                temperature=0.3
            )

            return result

        except Exception as e:
            logger.error(f"Erro ao executar tarefa do agente {agent}: {str(e)}")
            return f"Erro na execução: {str(e)}"

    def generate_comparative_analysis(
        self,
        contract1_text: str,
        contract2_text: str
    ) -> str:
        """
        Gera análise comparativa entre dois contratos.

        Args:
            contract1_text: Primeiro contrato
            contract2_text: Segundo contrato

        Returns:
            Análise comparativa detalhada
        """
        logger.info("Iniciando análise comparativa...")

        return self._run_agent_task(
            agent="legal_expert",
            task=f"""
Compare os dois contratos abaixo e identifique:

1. Diferenças estruturais
2. Diferenças em cláusulas essenciais
3. Variações financeiras
4. Mudanças em obrigações
5. Alterações em prazos e condições
6. Impacto das diferenças
7. Recomendações

CONTRATO 1:
{contract1_text[:3000]}

---

CONTRATO 2:
{contract2_text[:3000]}
"""
        )
