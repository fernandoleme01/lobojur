"""Cliente Gemini para análise de documentos."""

import logging
import google.generativeai as genai
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeminiAnalyzer:
    """
    Cliente Gemini para análise profunda de documentos.

    Usa Google Gemini para análise detalhada de contratos.
    """

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash-exp"):
        """
        Inicializa cliente Gemini.

        Args:
            api_key: Chave API Google
            model: Modelo Gemini
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.model_name = model

    def analyze_document(
        self,
        document_text: str,
        analysis_focus: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Analisa documento completo.

        Args:
            document_text: Texto do documento
            analysis_focus: Foco da análise

        Returns:
            Análise detalhada
        """
        try:
            logger.info(f"Analisando documento com Gemini (foco: {analysis_focus})")

            prompts = {
                "comprehensive": """
Analise este contrato de forma abrangente e detalhada:

1. ESTRUTURA DO DOCUMENTO
   - Tipo de contrato
   - Organização das cláusulas
   - Completude do documento

2. PARTES CONTRATANTES
   - Identificação completa
   - Qualificação
   - Capacidade jurídica

3. OBJETO E FINALIDADE
   - Descrição detalhada
   - Escopo e limitações
   - Viabilidade

4. OBRIGAÇÕES E DIREITOS
   - De cada parte
   - Balanceamento
   - Exequibilidade

5. ASPECTOS FINANCEIROS
   - Valores e cálculos
   - Condições de pagamento
   - Penalidades financeiras

6. PRAZOS E VIGÊNCIA
   - Análise de todos os prazos
   - Compatibilidade
   - Razoabilidade

7. RISCOS E VULNERABILIDADES
   - Jurídicos
   - Financeiros
   - Operacionais

8. CONFORMIDADE LEGAL
   - Com legislação brasileira
   - Requisitos formais
   - Cláusulas questionáveis

Seja extremamente detalhado e técnico.
""",
                "legal_compliance": """
Analise a conformidade legal deste contrato:

1. Requisitos formais
2. Conformidade com Código Civil
3. Conformidade com CDC (se aplicável)
4. Cláusulas potencialmente abusivas
5. Riscos de nulidade
6. Recomendações de adequação
""",
                "risk_analysis": """
Realize análise profunda de riscos:

1. Identifique todos os riscos jurídicos
2. Identifique riscos financeiros
3. Identifique riscos operacionais
4. Quantifique quando possível
5. Priorize por gravidade
6. Sugira mitigações específicas
"""
            }

            prompt = prompts.get(analysis_focus, prompts["comprehensive"])
            full_prompt = f"{prompt}\n\nCONTRATO:\n{document_text}"

            response = self.model.generate_content(full_prompt)

            return {
                "analysis": response.text,
                "model": self.model_name,
                "focus": analysis_focus
            }

        except Exception as e:
            logger.error(f"Erro na análise Gemini: {str(e)}")
            return {
                "analysis": "",
                "error": str(e)
            }

    def extract_structured_information(
        self,
        document_text: str,
        fields: List[str]
    ) -> Dict[str, str]:
        """
        Extrai informações estruturadas do documento.

        Args:
            document_text: Texto do documento
            fields: Campos a extrair

        Returns:
            Dicionário com campos extraídos
        """
        try:
            fields_list = "\n".join([f"- {field}" for field in fields])

            prompt = f"""
Extraia as seguintes informações do contrato de forma precisa e estruturada:

{fields_list}

Para cada campo:
1. Extraia a informação exata do texto
2. Se não encontrar, indique "NÃO ENCONTRADO"
3. Se houver múltiplas ocorrências, liste todas

Formato de resposta:
CAMPO: informação extraída

CONTRATO:
{document_text}
"""

            response = self.model.generate_content(prompt)

            # Parse response
            extracted = {}
            for line in response.text.split('\n'):
                if ':' in line and not line.startswith('#'):
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        extracted[parts[0].strip()] = parts[1].strip()

            return extracted

        except Exception as e:
            logger.error(f"Erro na extração Gemini: {str(e)}")
            return {}

    def compare_versions(
        self,
        version1: str,
        version2: str
    ) -> Dict[str, Any]:
        """
        Compara duas versões de documento.

        Args:
            version1: Primeira versão
            version2: Segunda versão

        Returns:
            Análise comparativa detalhada
        """
        try:
            logger.info("Comparando versões com Gemini")

            prompt = f"""
Compare estas duas versões de contrato e identifique:

1. DIFERENÇAS TEXTUAIS
   - Cláusulas adicionadas
   - Cláusulas removidas
   - Cláusulas modificadas

2. DIFERENÇAS FINANCEIRAS
   - Mudanças em valores
   - Alterações em condições de pagamento

3. DIFERENÇAS EM OBRIGAÇÕES
   - Novas obrigações
   - Obrigações removidas
   - Obrigações alteradas

4. IMPACTO DAS MUDANÇAS
   - Para cada parte
   - Riscos introduzidos ou removidos
   - Recomendações

Seja específico e cite as cláusulas.

VERSÃO 1:
{version1[:5000]}

---

VERSÃO 2:
{version2[:5000]}
"""

            response = self.model.generate_content(prompt)

            return {
                "comparison": response.text,
                "model": self.model_name
            }

        except Exception as e:
            logger.error(f"Erro na comparação Gemini: {str(e)}")
            return {"comparison": "", "error": str(e)}

    def validate_clauses(
        self,
        clauses: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Valida cláusulas contratuais.

        Args:
            clauses: Lista de cláusulas {"title": "", "text": ""}

        Returns:
            Validação de cada cláusula
        """
        try:
            logger.info(f"Validando {len(clauses)} cláusulas com Gemini")

            validations = []

            for clause in clauses:
                prompt = f"""
Valide esta cláusula contratual segundo a legislação brasileira:

TÍTULO: {clause.get('title', 'Sem título')}
TEXTO: {clause.get('text', '')}

Analise:
1. Legalidade (conforme Código Civil e CDC)
2. Clareza e precisão
3. Exequibilidade
4. Riscos identificados
5. Recomendações de melhoria

Seja técnico e cite artigos da lei quando relevante.
"""

                response = self.model.generate_content(prompt)

                validations.append({
                    "clause_title": clause.get('title'),
                    "validation": response.text,
                    "status": "analyzed"
                })

            return validations

        except Exception as e:
            logger.error(f"Erro na validação de cláusulas: {str(e)}")
            return []

    def generate_summary(
        self,
        document_text: str,
        summary_type: str = "executive"
    ) -> str:
        """
        Gera resumo do documento.

        Args:
            document_text: Texto do documento
            summary_type: Tipo de resumo (executive, technical, brief)

        Returns:
            Resumo gerado
        """
        try:
            prompts = {
                "executive": "Crie um resumo executivo deste contrato para tomada de decisão (máx 500 palavras)",
                "technical": "Crie um resumo técnico detalhado para análise jurídica (máx 1000 palavras)",
                "brief": "Crie um resumo breve dos pontos principais (máx 200 palavras)"
            }

            prompt = f"""
{prompts.get(summary_type, prompts['executive'])}

CONTRATO:
{document_text[:8000]}
"""

            response = self.model.generate_content(prompt)
            return response.text

        except Exception as e:
            logger.error(f"Erro ao gerar resumo: {str(e)}")
            return ""

    def identify_parties(
        self,
        document_text: str
    ) -> List[Dict[str, str]]:
        """
        Identifica partes do contrato.

        Args:
            document_text: Texto do documento

        Returns:
            Lista de partes identificadas
        """
        try:
            prompt = f"""
Identifique todas as partes deste contrato e extraia:

1. Nome/Razão Social
2. CPF/CNPJ
3. Endereço completo
4. Representante legal (se houver)
5. Qualificação jurídica
6. Papel no contrato (contratante, contratada, etc.)

Retorne em formato estruturado.

CONTRATO:
{document_text[:5000]}
"""

            response = self.model.generate_content(prompt)

            # TODO: Parsear resposta estruturada
            return [{"raw_response": response.text}]

        except Exception as e:
            logger.error(f"Erro ao identificar partes: {str(e)}")
            return []
