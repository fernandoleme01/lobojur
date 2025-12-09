"""
Serviço de busca de doutrinas usando Browser Use
"""
import asyncio
from typing import List, Dict, Optional
from datetime import datetime


class DoutrinaService:
    """Serviço para buscar doutrinas e artigos jurídicos"""

    def __init__(self, db_manager):
        """
        Inicializa o serviço de doutrinas

        Args:
            db_manager: Instância do gerenciador de banco de dados
        """
        self.db = db_manager
        self.fontes = {
            'GOOGLE_SCHOLAR': self._buscar_google_scholar,
            'SCIELO': self._buscar_scielo,
            'REPOSITORIOS': self._buscar_repositorios
        }

    async def buscar_doutrinas(
        self,
        query: str,
        area_direito: str,
        fontes: List[str] = None,
        max_resultados: int = 3
    ) -> List[Dict]:
        """
        Busca doutrinas relevantes

        Args:
            query: Termo de busca
            area_direito: Área do direito para filtrar
            fontes: Lista de fontes para buscar (None = todas)
            max_resultados: Número máximo de resultados

        Returns:
            Lista de doutrinas encontradas
        """
        # Primeiro, buscar no cache local
        cache_results = self.db.buscar_doutrinas(
            area_direito=area_direito,
            palavras_chave=query.split(),
            limit=max_resultados
        )

        if len(cache_results) >= max_resultados:
            return self._format_doutrinas(cache_results)

        # Se não houver resultados suficientes no cache, buscar online
        fontes_buscar = fontes or ['GOOGLE_SCHOLAR', 'SCIELO']
        todas_doutrinas = []

        for fonte in fontes_buscar:
            if fonte in self.fontes:
                try:
                    resultados = await self.fontes[fonte](query, area_direito)
                    todas_doutrinas.extend(resultados)

                    # Salvar no cache
                    for doutrina in resultados:
                        doutrina['area_direito'] = area_direito
                        self.db.salvar_doutrina(doutrina)

                except Exception as e:
                    print(f"Erro ao buscar em {fonte}: {str(e)}")
                    continue

        # Ordenar por relevância e retornar
        todas_doutrinas.sort(
            key=lambda x: x.get('relevancia_score', 0),
            reverse=True
        )

        return todas_doutrinas[:max_resultados]

    async def _buscar_google_scholar(self, query: str, area_direito: str) -> List[Dict]:
        """
        Busca artigos no Google Scholar
        Nota: Esta é uma implementação simulada. Na versão real, usaria Browser Use
        """
        # TODO: Implementar busca real com Browser Use
        return []

    async def _buscar_scielo(self, query: str, area_direito: str) -> List[Dict]:
        """Busca artigos no SciELO"""
        # TODO: Implementar com Browser Use
        return []

    async def _buscar_repositorios(self, query: str, area_direito: str) -> List[Dict]:
        """Busca em repositórios universitários"""
        # TODO: Implementar com Browser Use
        return []

    def _format_doutrinas(self, doutrinas) -> List[Dict]:
        """Formata doutrinas do banco para dict"""
        return [
            {
                'id': d.id,
                'titulo': d.titulo,
                'autor': d.autor,
                'ano': d.ano,
                'fonte': d.fonte,
                'editora': d.editora,
                'resumo': d.resumo,
                'citacao_abnt': d.citacao_abnt,
                'relevancia_score': d.relevancia_score,
                'url_fonte': d.url_fonte
            }
            for d in doutrinas
        ]

    def criar_citacao_abnt(self, doutrina: Dict) -> str:
        """
        Cria citação ABNT de uma doutrina

        Args:
            doutrina: Dicionário com dados da doutrina

        Returns:
            Citação formatada em ABNT
        """
        autor = doutrina.get('autor', '').upper()
        titulo = doutrina.get('titulo', '')
        fonte = doutrina.get('fonte', '')
        editora = doutrina.get('editora', '')
        ano = doutrina.get('ano', '')

        # Formato básico ABNT
        citacao = f"{autor}. {titulo}"

        if fonte:
            citacao += f". {fonte}"
        if editora:
            citacao += f". {editora}"
        if ano:
            citacao += f", {ano}"

        citacao += "."

        return citacao
