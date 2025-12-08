"""
Serviço de busca de jurisprudências usando Browser Use
"""
import asyncio
from typing import List, Dict, Optional
from datetime import datetime
import re


class JurisprudenciaService:
    """Serviço para buscar jurisprudências em tribunais brasileiros"""

    def __init__(self, db_manager):
        """
        Inicializa o serviço de jurisprudências

        Args:
            db_manager: Instância do gerenciador de banco de dados
        """
        self.db = db_manager
        self.tribunais = {
            'STF': self._buscar_stf,
            'STJ': self._buscar_stj,
            'TST': self._buscar_tst,
            'JUSBRASIL': self._buscar_jusbrasil
        }

    async def buscar_jurisprudencias(
        self,
        query: str,
        area_direito: str,
        tribunais: List[str] = None,
        max_resultados: int = 5
    ) -> List[Dict]:
        """
        Busca jurisprudências relevantes

        Args:
            query: Termo de busca
            area_direito: Área do direito para filtrar
            tribunais: Lista de tribunais para buscar (None = todos)
            max_resultados: Número máximo de resultados

        Returns:
            Lista de jurisprudências encontradas
        """
        # Primeiro, buscar no cache local
        cache_results = self.db.buscar_jurisprudencias(
            area_direito=area_direito,
            palavras_chave=query.split(),
            limit=max_resultados
        )

        if len(cache_results) >= max_resultados:
            return self._format_jurisprudencias(cache_results)

        # Se não houver resultados suficientes no cache, buscar online
        tribunais_buscar = tribunais or ['JUSBRASIL', 'STJ', 'STF']
        todas_jurisprudencias = []

        for tribunal in tribunais_buscar:
            if tribunal in self.tribunais:
                try:
                    resultados = await self.tribunais[tribunal](query, area_direito)
                    todas_jurisprudencias.extend(resultados)

                    # Salvar no cache
                    for jurisp in resultados:
                        jurisp['area_direito'] = area_direito
                        self.db.salvar_jurisprudencia(jurisp)

                except Exception as e:
                    print(f"Erro ao buscar em {tribunal}: {str(e)}")
                    continue

        # Ordenar por relevância e retornar
        todas_jurisprudencias.sort(
            key=lambda x: x.get('relevancia_score', 0),
            reverse=True
        )

        return todas_jurisprudencias[:max_resultados]

    async def _buscar_jusbrasil(self, query: str, area_direito: str) -> List[Dict]:
        """
        Busca jurisprudências no JusBrasil
        Nota: Esta é uma implementação simulada. Na versão real, usaria Browser Use
        """
        # TODO: Implementar busca real com Browser Use
        # Por enquanto, retorna dados simulados
        return []

    async def _buscar_stj(self, query: str, area_direito: str) -> List[Dict]:
        """Busca jurisprudências no STJ"""
        # TODO: Implementar com Browser Use
        return []

    async def _buscar_stf(self, query: str, area_direito: str) -> List[Dict]:
        """Busca jurisprudências no STF"""
        # TODO: Implementar com Browser Use
        return []

    async def _buscar_tst(self, query: str, area_direito: str) -> List[Dict]:
        """Busca jurisprudências no TST"""
        # TODO: Implementar com Browser Use
        return []

    def _format_jurisprudencias(self, jurisprudencias) -> List[Dict]:
        """Formata jurisprudências do banco para dict"""
        return [
            {
                'id': j.id,
                'tribunal': j.tribunal,
                'numero_processo': j.numero_processo,
                'ementa': j.ementa,
                'decisao': j.decisao,
                'relator': j.relator,
                'data_julgamento': j.data_julgamento,
                'relevancia_score': j.relevancia_score,
                'url_fonte': j.url_fonte
            }
            for j in jurisprudencias
        ]

    def criar_citacao_jurisprudencia(self, jurisprudencia: Dict) -> str:
        """
        Cria citação formatada de uma jurisprudência

        Args:
            jurisprudencia: Dicionário com dados da jurisprudência

        Returns:
            Citação formatada segundo normas jurídicas
        """
        tribunal = jurisprudencia.get('tribunal', '')
        numero = jurisprudencia.get('numero_processo', '')
        relator = jurisprudencia.get('relator', '')
        data = jurisprudencia.get('data_julgamento', '')

        if isinstance(data, datetime):
            data_fmt = data.strftime('%d/%m/%Y')
        else:
            data_fmt = str(data) if data else ''

        citacao = f"{tribunal}"
        if numero:
            citacao += f", {numero}"
        if relator:
            citacao += f", Rel. Min. {relator}"
        if data_fmt:
            citacao += f", j. {data_fmt}"

        return citacao
