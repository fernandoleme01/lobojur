"""Cliente para integração com Claude API."""

import logging
from typing import Dict, List, Optional, Any
from anthropic import Anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClaudeAnalyzer:
    """Cliente para análise de documentos usando Claude API."""

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        """
        Inicializa o cliente Claude.

        Args:
            api_key: Chave da API Anthropic
            model: Modelo Claude a ser usado
        """
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = 4096

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def analyze_text(
        self,
        text: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3
    ) -> str:
        """
        Analisa texto usando Claude.

        Args:
            text: Texto a ser analisado
            prompt: Prompt com instruções de análise
            system_prompt: Prompt de sistema (opcional)
            temperature: Temperatura para geração (0-1)

        Returns:
            Análise gerada pelo Claude
        """
        try:
            messages = [
                {
                    "role": "user",
                    "content": f"{prompt}\n\nTexto para análise:\n{text}"
                }
            ]

            kwargs = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "temperature": temperature,
                "messages": messages
            }

            if system_prompt:
                kwargs["system"] = system_prompt

            response = self.client.messages.create(**kwargs)

            return response.content[0].text

        except Exception as e:
            logger.error(f"Erro ao analisar texto com Claude: {str(e)}")
            raise

    def analyze_contract(
        self,
        contract_text: str,
        analysis_type: str = "comprehensive",
        custom_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analisa um contrato legal.

        Args:
            contract_text: Texto do contrato
            analysis_type: Tipo de análise (comprehensive, summary, risks)
            custom_instructions: Instruções personalizadas adicionais

        Returns:
            Dicionário com análise estruturada
        """
        prompts = {
            "comprehensive": """
Analise este contrato legal de forma abrangente e forneça:

1. PARTES ENVOLVIDAS
   - Identificação completa das partes
   - Qualificação jurídica

2. OBJETO DO CONTRATO
   - Descrição detalhada
   - Finalidade e escopo

3. CLÁUSULAS PRINCIPAIS
   - Obrigações de cada parte
   - Direitos e deveres
   - Prazos e condições

4. VALORES E CONDIÇÕES FINANCEIRAS
   - Valores envolvidos
   - Formas de pagamento
   - Reajustes e índices

5. PRAZOS E VIGÊNCIA
   - Prazo de vigência
   - Prorrogações
   - Rescisão

6. CLÁUSULAS DE ATENÇÃO
   - Multas e penalidades
   - Garantias exigidas
   - Condições especiais

7. RISCOS IDENTIFICADOS
   - Riscos jurídicos
   - Riscos financeiros
   - Riscos operacionais

8. PONTOS DE ATENÇÃO
   - Cláusulas ambíguas
   - Cláusulas abusivas
   - Recomendações
""",
            "summary": """
Forneça um resumo executivo deste contrato incluindo:
1. Partes envolvidas
2. Objeto principal
3. Valores e prazos
4. Principais obrigações
5. Pontos críticos de atenção
""",
            "risks": """
Analise os riscos deste contrato:
1. Riscos jurídicos
2. Riscos financeiros
3. Cláusulas potencialmente problemáticas
4. Recomendações de mitigação
"""
        }

        prompt = prompts.get(analysis_type, prompts["comprehensive"])

        if custom_instructions:
            prompt += f"\n\nInstruções adicionais:\n{custom_instructions}"

        system_prompt = """
Você é um especialista em análise de contratos legais com vasta experiência em direito contratual brasileiro.
Sua análise deve ser técnica, precisa e seguir as normas jurídicas brasileiras.
Identifique cláusulas de acordo com a legislação vigente (Código Civil, CDC, etc.).
Seja específico e cite os artigos da lei quando relevante.
"""

        analysis = self.analyze_text(
            text=contract_text,
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.2
        )

        return {
            "analysis_type": analysis_type,
            "analysis": analysis,
            "model_used": self.model
        }

    def extract_structured_data(
        self,
        text: str,
        fields: List[str]
    ) -> Dict[str, str]:
        """
        Extrai dados estruturados do texto.

        Args:
            text: Texto para extração
            fields: Lista de campos a extrair

        Returns:
            Dicionário com campos extraídos
        """
        fields_str = "\n".join([f"- {field}" for field in fields])

        prompt = f"""
Extraia as seguintes informações do texto fornecido:

{fields_str}

Para cada campo, forneça a informação encontrada ou "NÃO ENCONTRADO" se não estiver presente.
Formato de resposta:

CAMPO: valor encontrado
"""

        system_prompt = """
Você é um especialista em extração de informações de documentos legais.
Seja preciso e extraia exatamente o que foi solicitado.
"""

        response = self.analyze_text(
            text=text,
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.1
        )

        # Parse response
        extracted = {}
        for line in response.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                extracted[key.strip()] = value.strip()

        return extracted

    def generate_report_section(
        self,
        section_name: str,
        data: Dict[str, Any],
        template_instructions: Optional[str] = None
    ) -> str:
        """
        Gera uma seção de laudo técnico.

        Args:
            section_name: Nome da seção
            data: Dados para incluir na seção
            template_instructions: Instruções de template

        Returns:
            Texto da seção gerada
        """
        data_str = "\n".join([f"{k}: {v}" for k, v in data.items()])

        prompt = f"""
Gere a seção "{section_name}" de um laudo técnico jurídico com base nos seguintes dados:

{data_str}

{template_instructions or ''}

A seção deve ser:
- Formal e técnica
- Bem estruturada
- Clara e objetiva
- Em conformidade com padrões de laudos técnicos
"""

        system_prompt = """
Você é um perito técnico especializado em elaboração de laudos jurídicos.
Seus laudos devem seguir padrões técnicos rigorosos e linguagem jurídica apropriada.
"""

        return self.analyze_text(
            text="",
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3
        )

    def compare_documents(
        self,
        doc1_text: str,
        doc2_text: str,
        comparison_aspects: Optional[List[str]] = None
    ) -> str:
        """
        Compara dois documentos.

        Args:
            doc1_text: Texto do primeiro documento
            doc2_text: Texto do segundo documento
            comparison_aspects: Aspectos específicos para comparar

        Returns:
            Análise comparativa
        """
        aspects = comparison_aspects or [
            "Cláusulas diferentes",
            "Valores divergentes",
            "Prazos distintos",
            "Obrigações modificadas"
        ]

        aspects_str = "\n".join([f"- {aspect}" for aspect in aspects])

        prompt = f"""
Compare os dois documentos fornecidos e identifique:

{aspects_str}

Documento 1:
{doc1_text[:3000]}

---

Documento 2:
{doc2_text[:3000]}

Forneça uma análise detalhada das diferenças encontradas.
"""

        system_prompt = """
Você é um especialista em análise comparativa de documentos legais.
Identifique diferenças relevantes e explique suas implicações.
"""

        return self.analyze_text(
            text="",
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.2
        )
