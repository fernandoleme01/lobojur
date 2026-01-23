"""Cliente Perplexity para pesquisas em tempo real."""

import logging
import httpx
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerplexityResearcher:
    """
    Cliente Perplexity AI para pesquisas em tempo real.

    Usa a API Perplexity para buscar informações atualizadas na web.
    """

    def __init__(self, api_key: str, model: str = "sonar-pro"):
        """
        Inicializa cliente Perplexity.

        Args:
            api_key: Chave API Perplexity
            model: Modelo Perplexity (sonar, sonar-pro, etc.)
        """
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.perplexity.ai"

    async def search(
        self,
        query: str,
        search_domain: Optional[str] = None,
        search_recency: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Realiza pesquisa usando Perplexity.

        Args:
            query: Query de pesquisa
            search_domain: Domínio específico para buscar
            search_recency: Filtro de recência (day, week, month, year)

        Returns:
            Resultados da pesquisa com fontes
        """
        try:
            logger.info(f"Pesquisando com Perplexity: {query}")

            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "Você é um assistente especializado em pesquisa jurídica brasileira. Forneça informações precisas e atualizadas com fontes confiáveis."
                        },
                        {
                            "role": "user",
                            "content": query
                        }
                    ],
                    "search_domain_filter": [search_domain] if search_domain else None,
                    "search_recency_filter": search_recency,
                    "return_citations": True,
                    "return_images": False
                }

                # Remover campos None
                payload = {k: v for k, v in payload.items() if v is not None}

                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )

                response.raise_for_status()
                data = response.json()

                return {
                    "answer": data["choices"][0]["message"]["content"],
                    "citations": data.get("citations", []),
                    "model": data["model"],
                    "usage": data.get("usage", {})
                }

        except Exception as e:
            logger.error(f"Erro na pesquisa Perplexity: {str(e)}")
            return {
                "answer": "",
                "citations": [],
                "error": str(e)
            }

    async def research_legal_topic(
        self,
        topic: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Pesquisa tópico jurídico específico.

        Args:
            topic: Tópico jurídico
            context: Contexto adicional

        Returns:
            Pesquisa detalhada com fontes
        """
        query = f"""
Pesquise sobre o seguinte tópico jurídico brasileiro:

TÓPICO: {topic}

{f"CONTEXTO: {context}" if context else ""}

Forneça:
1. Legislação aplicável atual
2. Jurisprudências recentes dos tribunais superiores
3. Doutrina relevante
4. Mudanças legislativas recentes (se houver)
5. Entendimento consolidado dos tribunais

Cite todas as fontes.
"""
        return await self.search(query, search_recency="month")

    async def search_jurisprudence(
        self,
        keywords: List[str],
        court: str = "STJ"
    ) -> Dict[str, Any]:
        """
        Busca jurisprudências específicas.

        Args:
            keywords: Palavras-chave
            court: Tribunal (STJ, STF, TST, etc.)

        Returns:
            Jurisprudências encontradas
        """
        keywords_str = ", ".join(keywords)
        query = f"""
Busque jurisprudências recentes do {court} sobre: {keywords_str}

Forneça:
1. Principais decisões recentes
2. Teses firmadas
3. Súmulas aplicáveis
4. Entendimento atual do tribunal
5. Links para as decisões

Priorize decisões de 2023-2024.
"""
        return await self.search(query, search_recency="year")

    async def verify_legislation(
        self,
        lei_numero: str,
        check_updates: bool = True
    ) -> Dict[str, Any]:
        """
        Verifica legislação e alterações.

        Args:
            lei_numero: Número da lei
            check_updates: Se deve verificar atualizações

        Returns:
            Informações sobre a legislação
        """
        query = f"""
Forneça informações atualizadas sobre a Lei {lei_numero}:

1. Ementa completa
2. Status atual (vigente, revogada, etc.)
3. Alterações recentes (se houver)
4. Regulamentações relacionadas
5. Interpretação dos tribunais
6. Link oficial do Planalto

{"Verifique se houve mudanças nos últimos 12 meses." if check_updates else ""}
"""
        return await self.search(query, search_recency="year")

    async def research_company(
        self,
        cnpj: str,
        include_legal_issues: bool = True
    ) -> Dict[str, Any]:
        """
        Pesquisa informações sobre empresa.

        Args:
            cnpj: CNPJ da empresa
            include_legal_issues: Incluir questões legais

        Returns:
            Informações da empresa
        """
        query = f"""
Pesquise informações públicas sobre a empresa CNPJ {cnpj}:

1. Razão social e nome fantasia
2. Situação cadastral atual
3. Atividades principais
4. Sócios e capital social

{'''5. Processos judiciais relevantes
6. Questões regulatórias
7. Histórico de compliance''' if include_legal_issues else ''}

Use apenas fontes oficiais (Receita Federal, tribunais, etc.).
"""
        return await self.search(query)

    async def check_contract_validity(
        self,
        contract_type: str,
        clauses_summary: str
    ) -> Dict[str, Any]:
        """
        Verifica validade de tipo de contrato e cláusulas.

        Args:
            contract_type: Tipo de contrato
            clauses_summary: Resumo das cláusulas principais

        Returns:
            Análise de validade
        """
        query = f"""
Analise a validade jurídica do seguinte tipo de contrato:

TIPO: {contract_type}

CLÁUSULAS PRINCIPAIS:
{clauses_summary}

Verifique:
1. Conformidade com legislação brasileira atual
2. Cláusulas potencialmente abusivas segundo CDC
3. Requisitos legais que podem estar faltando
4. Jurisprudência relevante
5. Recomendações de adequação

Base: Código Civil, CDC, e legislação específica aplicável.
"""
        return await self.search(query, search_recency="year")
