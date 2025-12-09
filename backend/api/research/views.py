"""
Research API Views - Pesquisa Jurídica
"""
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import logging

from core.integration_layer import LoboJurCore
from .serializers import (
    JurisprudenceSearchSerializer,
    AddJurisprudenceSerializer,
    AddDoctrineSerializer,
    HybridSearchSerializer,
)

logger = logging.getLogger('lobojur.research')


class JurisprudenceSearchView(views.APIView):
    """
    Busca jurisprudências no RAG local

    GET /api/v1/research/jurisprudence/?query=dano+moral&area=Civil&tribunal=STJ
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = JurisprudenceSearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        try:
            lobojur = LoboJurCore(config=settings.LOBOJUR_CONFIG)

            resultados = lobojur.rag.search_jurisprudencias(
                query=serializer.validated_data['query'],
                area_direito=serializer.validated_data.get('area'),
                tribunal=serializer.validated_data.get('tribunal'),
                n_results=serializer.validated_data.get('limit', 5)
            )

            return Response({
                'results': resultados,
                'count': len(resultados)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Erro ao buscar jurisprudências: {e}", exc_info=True)
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AddJurisprudenceView(views.APIView):
    """
    Adiciona jurisprudência ao RAG

    POST /api/v1/research/jurisprudence/add/
    {
        "texto": "Ementa da decisão...",
        "tribunal": "STJ",
        "numero_processo": "REsp 1234567",
        "area_direito": "Direito Civil"
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddJurisprudenceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            lobojur = LoboJurCore(config=settings.LOBOJUR_CONFIG)

            lobojur.rag.add_jurisprudencia(
                texto=serializer.validated_data['texto'],
                metadata={
                    'tribunal': serializer.validated_data.get('tribunal', ''),
                    'numero_processo': serializer.validated_data.get('numero_processo', ''),
                    'area_direito': serializer.validated_data.get('area_direito', ''),
                }
            )

            return Response({
                'message': 'Jurisprudência adicionada com sucesso'
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Erro ao adicionar jurisprudência: {e}", exc_info=True)
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DoctrineSearchView(views.APIView):
    """
    Busca doutrinas no RAG

    GET /api/v1/research/doctrine/?query=responsabilidade+civil&area=Civil
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            lobojur = LoboJurCore(config=settings.LOBOJUR_CONFIG)

            query = request.query_params.get('query', '')
            area = request.query_params.get('area', '')

            if not query:
                return Response({
                    'error': 'Parâmetro "query" é obrigatório'
                }, status=status.HTTP_400_BAD_REQUEST)

            resultados = lobojur.rag.search_doutrinas(
                query=query,
                area_direito=area,
                n_results=int(request.query_params.get('limit', 5))
            )

            return Response({
                'results': resultados,
                'count': len(resultados)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Erro ao buscar doutrinas: {e}", exc_info=True)
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AddDoctrineView(views.APIView):
    """
    Adiciona doutrina ao RAG

    POST /api/v1/research/doctrine/add/
    {
        "texto": "Texto da doutrina...",
        "autor": "Carlos Roberto Gonçalves",
        "obra": "Responsabilidade Civil",
        "area_direito": "Direito Civil"
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddDoctrineSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            lobojur = LoboJurCore(config=settings.LOBOJUR_CONFIG)

            lobojur.rag.add_doutrina(
                texto=serializer.validated_data['texto'],
                metadata={
                    'autor': serializer.validated_data.get('autor', ''),
                    'obra': serializer.validated_data.get('obra', ''),
                    'area_direito': serializer.validated_data.get('area_direito', ''),
                }
            )

            return Response({
                'message': 'Doutrina adicionada com sucesso'
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Erro ao adicionar doutrina: {e}", exc_info=True)
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LegislationSearchView(views.APIView):
    """
    Busca legislação no RAG

    GET /api/v1/research/legislation/?query=art+186+código+civil
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            lobojur = LoboJurCore(config=settings.LOBOJUR_CONFIG)

            query = request.query_params.get('query', '')

            if not query:
                return Response({
                    'error': 'Parâmetro "query" é obrigatório'
                }, status=status.HTTP_400_BAD_REQUEST)

            resultados = lobojur.rag.search_legislacao(
                query=query,
                n_results=int(request.query_params.get('limit', 5))
            )

            return Response({
                'results': resultados,
                'count': len(resultados)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Erro ao buscar legislação: {e}", exc_info=True)
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProcessSearchView(views.APIView):
    """
    Busca processo no Escavador

    GET /api/v1/research/process/0001234-56.2020.4.01.3800/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, numero):
        try:
            lobojur = LoboJurCore(config=settings.LOBOJUR_CONFIG)

            if not lobojur.escavador:
                return Response({
                    'error': 'Escavador não configurado'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            processo = lobojur.escavador.buscar_processos_por_numero(numero)

            return Response(processo, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Erro ao buscar processo: {e}", exc_info=True)
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MonitorProcessView(views.APIView):
    """
    Monitora processo no Escavador (webhook)

    POST /api/v1/research/process/0001234-56.2020.4.01.3800/monitor/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, numero):
        try:
            lobojur = LoboJurCore(config=settings.LOBOJUR_CONFIG)

            if not lobojur.escavador:
                return Response({
                    'error': 'Escavador não configurado'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            resultado = lobojur.escavador.monitorar_processo(numero)

            return Response({
                'message': 'Monitoramento ativado',
                'result': resultado
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Erro ao monitorar processo: {e}", exc_info=True)
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HybridSearchView(views.APIView):
    """
    Busca híbrida em todas as coleções do RAG

    POST /api/v1/research/hybrid/
    {
        "query": "responsabilidade civil por danos morais",
        "collections": ["jurisprudencias", "doutrinas", "legislacao"],
        "n_results_per_collection": 3
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = HybridSearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            lobojur = LoboJurCore(config=settings.LOBOJUR_CONFIG)

            resultados = lobojur.rag.hybrid_search(
                query=serializer.validated_data['query'],
                collections=serializer.validated_data.get('collections', [
                    'jurisprudencias', 'doutrinas', 'legislacao'
                ]),
                n_results_per_collection=serializer.validated_data.get('n_results_per_collection', 3)
            )

            return Response(resultados, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Erro na busca híbrida: {e}", exc_info=True)
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
