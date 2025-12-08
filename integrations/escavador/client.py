"""
Integração com Escavador - Pesquisa Processual e Jurisprudência
"""
import requests
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class EscavadorClient:
    """Cliente para integração com API do Escavador"""

    def __init__(self, api_key: str):
        """
        Inicializa cliente Escavador

        Args:
            api_key: Chave API do Escavador
        """
        self.api_key = api_key
        self.base_url = "https://api.escavador.com/api/v2"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def _request(self, method: str, endpoint: str, params: Dict = None) -> Dict:
        """Faz requisição à API"""
        url = f"{self.base_url}/{endpoint}"

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição Escavador: {str(e)}")
            raise

    # ==================== BUSCA DE PROCESSOS ====================

    def buscar_processos_por_numero(self, numero_processo: str) -> Dict:
        """
        Busca processo por número

        Args:
            numero_processo: Número do processo (ex: 0000000-00.0000.0.00.0000)

        Returns:
            Dados do processo incluindo:
            - número
            - tribunal
            - vara
            - partes
            - movimentações
            - valor da causa
        """
        return self._request("GET", f"processos/{numero_processo}")

    def buscar_processos_por_parte(
        self,
        nome: str,
        tipo: str = "TODOS",  # AUTOR, REU, TODOS
        tribunal: str = None,
        page: int = 1,
        per_page: int = 20
    ) -> List[Dict]:
        """
        Busca processos por nome de parte

        Args:
            nome: Nome da parte
            tipo: AUTOR, REU, TODOS
            tribunal: Sigla do tribunal (ex: TJSP, STF)
            page: Página
            per_page: Resultados por página
        """
        params = {
            "q": nome,
            "tipo_parte": tipo,
            "page": page,
            "per_page": per_page
        }

        if tribunal:
            params["tribunal"] = tribunal

        return self._request("GET", "processos/search", params)

    def buscar_processos_por_advogado(
        self,
        nome_advogado: str,
        oab: str = None,
        page: int = 1
    ) -> List[Dict]:
        """
        Busca processos por advogado

        Args:
            nome_advogado: Nome do advogado
            oab: Número da OAB (opcional)
            page: Página
        """
        params = {
            "q": nome_advogado,
            "page": page
        }

        if oab:
            params["oab"] = oab

        return self._request("GET", "advogados/processos", params)

    def monitorar_processo(self, numero_processo: str) -> Dict:
        """
        Ativa monitoramento de processo
        Receberá webhooks quando houver movimentações
        """
        data = {"numero_processo": numero_processo}
        return self._request("POST", "monitoramento/processos", data)

    def obter_movimentacoes(
        self,
        numero_processo: str,
        data_inicio: str = None,
        data_fim: str = None
    ) -> List[Dict]:
        """
        Obtém movimentações de um processo

        Args:
            numero_processo: Número do processo
            data_inicio: Data início filtro (YYYY-MM-DD)
            data_fim: Data fim filtro (YYYY-MM-DD)
        """
        params = {}
        if data_inicio:
            params["data_inicio"] = data_inicio
        if data_fim:
            params["data_fim"] = data_fim

        return self._request(
            "GET",
            f"processos/{numero_processo}/movimentacoes",
            params
        )

    # ==================== JURISPRUDÊNCIA ====================

    def buscar_jurisprudencia(
        self,
        query: str,
        tribunal: str = None,
        tipo_decisao: str = None,  # ACORDAO, SENTENCA, DESPACHO
        data_inicio: str = None,
        data_fim: str = None,
        page: int = 1,
        per_page: int = 20
    ) -> List[Dict]:
        """
        Busca jurisprudências

        Args:
            query: Termo de busca
            tribunal: STF, STJ, TST, TJSP, etc
            tipo_decisao: ACORDAO, SENTENCA, DESPACHO
            data_inicio: Data início (YYYY-MM-DD)
            data_fim: Data fim (YYYY-MM-DD)
        """
        params = {
            "q": query,
            "page": page,
            "per_page": per_page
        }

        if tribunal:
            params["tribunal"] = tribunal
        if tipo_decisao:
            params["tipo"] = tipo_decisao
        if data_inicio:
            params["data_inicio"] = data_inicio
        if data_fim:
            params["data_fim"] = data_fim

        return self._request("GET", "jurisprudencia/search", params)

    def obter_inteiro_teor(self, jurisprudencia_id: str) -> Dict:
        """
        Obtém inteiro teor de uma jurisprudência

        Returns:
            Dict com texto completo da decisão
        """
        return self._request("GET", f"jurisprudencia/{jurisprudencia_id}/inteiro-teor")

    # ==================== DIÁRIOS OFICIAIS ====================

    def buscar_diarios(
        self,
        tribunal: str,
        data: str,
        termo: str = None
    ) -> List[Dict]:
        """
        Busca publicações em diários oficiais

        Args:
            tribunal: Sigla do tribunal
            data: Data do diário (YYYY-MM-DD)
            termo: Termo de busca (opcional)
        """
        params = {
            "tribunal": tribunal,
            "data": data
        }

        if termo:
            params["q"] = termo

        return self._request("GET", "diarios", params)

    def monitorar_diario(
        self,
        tribunal: str,
        termos: List[str]
    ) -> Dict:
        """
        Monitora diários oficiais por termos
        Envia notificação quando encontrar

        Args:
            tribunal: Sigla do tribunal
            termos: Lista de termos para monitorar
        """
        data = {
            "tribunal": tribunal,
            "termos": termos
        }
        return self._request("POST", "monitoramento/diarios", data)

    # ==================== PESSOAS ====================

    def buscar_pessoa(
        self,
        nome: str = None,
        cpf: str = None,
        incluir_processos: bool = True
    ) -> Dict:
        """
        Busca informações sobre pessoa

        Returns:
            - Dados pessoais
            - Processos como parte
            - Empresas relacionadas
        """
        params = {}
        if nome:
            params["nome"] = nome
        if cpf:
            params["cpf"] = cpf
        if incluir_processos:
            params["incluir_processos"] = "true"

        return self._request("GET", "pessoas/search", params)

    def buscar_advogado(
        self,
        nome: str = None,
        oab: str = None,
        uf: str = None
    ) -> Dict:
        """
        Busca informações sobre advogado

        Returns:
            - Dados da OAB
            - Processos que atuou
            - Especialidades
            - Tribunais que mais atua
        """
        params = {}
        if nome:
            params["nome"] = nome
        if oab:
            params["oab"] = oab
        if uf:
            params["uf"] = uf

        return self._request("GET", "advogados/search", params)

    # ==================== EMPRESAS ====================

    def buscar_empresa(
        self,
        razao_social: str = None,
        cnpj: str = None,
        incluir_processos: bool = True
    ) -> Dict:
        """
        Busca informações sobre empresa

        Returns:
            - Dados cadastrais
            - Processos
            - Sócios
        """
        params = {}
        if razao_social:
            params["razao_social"] = razao_social
        if cnpj:
            params["cnpj"] = cnpj
        if incluir_processos:
            params["incluir_processos"] = "true"

        return self._request("GET", "empresas/search", params)

    # ==================== TRIBUNAIS ====================

    def listar_tribunais(self) -> List[Dict]:
        """Lista todos os tribunais disponíveis"""
        return self._request("GET", "tribunais")

    def obter_estatisticas_tribunal(self, tribunal: str) -> Dict:
        """
        Obtém estatísticas de um tribunal

        Returns:
            - Total de processos
            - Média de duração
            - Taxa de congestionamento
        """
        return self._request("GET", f"tribunais/{tribunal}/estatisticas")


# ==================== EXEMPLOS DE USO ====================

def exemplo_pesquisa_completa():
    """Exemplo de pesquisa processual completa"""

    escavador = EscavadorClient(api_key="SEU_API_KEY")

    # 1. Buscar processo por número
    processo = escavador.buscar_processos_por_numero("0000000-00.0000.0.00.0000")
    print(f"Processo: {processo['numero']}")
    print(f"Tribunal: {processo['tribunal']}")
    print(f"Valor da causa: R$ {processo['valor_causa']}")

    # 2. Monitorar processo (recebe webhooks de movimentações)
    escavador.monitorar_processo("0000000-00.0000.0.00.0000")

    # 3. Buscar jurisprudências sobre tema
    jurisprudencias = escavador.buscar_jurisprudencia(
        query="dano moral indenização",
        tribunal="STJ",
        tipo_decisao="ACORDAO",
        page=1,
        per_page=10
    )

    for jurisp in jurisprudencias:
        print(f"\n{jurisp['titulo']}")
        print(f"Relator: {jurisp['relator']}")
        print(f"Data: {jurisp['data_julgamento']}")

    # 4. Buscar processos por cliente
    processos_cliente = escavador.buscar_processos_por_parte(
        nome="João Silva",
        tipo="TODOS",
        tribunal="TJSP"
    )

    print(f"\nTotal de processos: {len(processos_cliente)}")

    # 5. Pesquisar advogado concorrente
    advogado = escavador.buscar_advogado(
        nome="Maria Santos",
        uf="SP"
    )

    print(f"\nAdvogado: {advogado['nome']}")
    print(f"OAB: {advogado['oab']}")
    print(f"Total de processos: {advogado['total_processos']}")
    print(f"Especialidades: {', '.join(advogado['especialidades'])}")

    # 6. Monitorar diário oficial
    escavador.monitorar_diario(
        tribunal="TJSP",
        termos=["ESCRITORIO SILVA & SANTOS", "João Silva", "Processo 1234"]
    )

    print("\nMonitoramento de diários ativado!")
