"""
Petitions API Views
"""
from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.http import FileResponse
import asyncio
import logging

from database.models import AreaDireito, PeticaoGerada, TemplatePeticao
from core.integration_layer import LoboJurCore
from .serializers import (
    AreaDireitoSerializer,
    PeticaoGeradaSerializer,
    GeneratePetitionSerializer,
    TemplatePeticaoSerializer,
)

logger = logging.getLogger(__name__)


class AreasListView(generics.ListAPIView):
    """
    Lista todas as áreas do direito disponíveis

    GET /api/v1/petitions/areas/
    """
    queryset = AreaDireito.query.all()
    serializer_class = AreaDireitoSerializer
    permission_classes = [IsAuthenticated]


class GeneratePetitionView(views.APIView):
    """
    Gera petição completa com IA

    POST /api/v1/petitions/generate/
    {
        "area_direito": "Direito Civil",
        "contexto": "Cliente sofreu danos morais...",
        "cliente_id": 123
    }

    Retorna:
    {
        "id": 456,
        "texto": "EXCELENTÍSSIMO SENHOR...",
        "fundamentacao": {
            "jurisprudencias": [...],
            "doutrinas": [...]
        },
        "created_at": "2025-12-08T10:30:00Z"
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = GeneratePetitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # Inicializar LoboJur Core
            lobojur = LoboJurCore(config=settings.LOBOJUR_CONFIG)

            # Gerar petição (async)
            resultado = asyncio.run(
                lobojur.gerar_peticao_completa(
                    area_direito=serializer.validated_data['area_direito'],
                    contexto=serializer.validated_data['contexto'],
                    cliente_id=serializer.validated_data.get('cliente_id')
                )
            )

            # Retornar petição gerada
            return Response({
                'id': resultado['id'],
                'texto': resultado['texto'],
                'fundamentacao': resultado['fundamentacao'],
                'message': 'Petição gerada com sucesso'
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Erro ao gerar petição: {e}", exc_info=True)
            return Response({
                'error': 'Erro ao gerar petição',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PetitionListView(generics.ListAPIView):
    """
    Lista todas as petições geradas

    GET /api/v1/petitions/
    Filtros: ?area=1&search=dano+moral
    """
    serializer_class = PeticaoGeradaSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['area_id', 'criado_em']
    search_fields = ['titulo', 'conteudo', 'contexto_usuario']
    ordering_fields = ['criado_em', 'titulo']
    ordering = ['-criado_em']

    def get_queryset(self):
        # Filtrar por usuário se não for admin
        if self.request.user.is_staff:
            return PeticaoGerada.query.all()
        else:
            # TODO: Adicionar campo user_id em PeticaoGerada
            return PeticaoGerada.query.all()


class PetitionDetailView(generics.RetrieveAPIView):
    """
    Detalhes de uma petição específica

    GET /api/v1/petitions/123/
    """
    queryset = PeticaoGerada.query.all()
    serializer_class = PeticaoGeradaSerializer
    permission_classes = [IsAuthenticated]


class ExportPDFView(views.APIView):
    """
    Exporta petição como PDF

    GET /api/v1/petitions/123/export/pdf/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            peticao = PeticaoGerada.query.get(pk)
            if not peticao:
                return Response({
                    'error': 'Petição não encontrada'
                }, status=status.HTTP_404_NOT_FOUND)

            # TODO: Implementar geração de PDF
            # from utils.pdf_generator import gerar_pdf
            # pdf_bytes = gerar_pdf(peticao.conteudo)

            return Response({
                'message': 'Exportação PDF em desenvolvimento'
            }, status=status.HTTP_501_NOT_IMPLEMENTED)

        except Exception as e:
            logger.error(f"Erro ao exportar PDF: {e}", exc_info=True)
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExportDOCXView(views.APIView):
    """
    Exporta petição como DOCX

    GET /api/v1/petitions/123/export/docx/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            peticao = PeticaoGerada.query.get(pk)
            if not peticao:
                return Response({
                    'error': 'Petição não encontrada'
                }, status=status.HTTP_404_NOT_FOUND)

            # TODO: Implementar geração de DOCX
            return Response({
                'message': 'Exportação DOCX em desenvolvimento'
            }, status=status.HTTP_501_NOT_IMPLEMENTED)

        except Exception as e:
            logger.error(f"Erro ao exportar DOCX: {e}", exc_info=True)
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TemplateListView(generics.ListAPIView):
    """
    Lista templates de petições disponíveis

    GET /api/v1/petitions/templates/?area=1
    """
    queryset = TemplatePeticao.query.all()
    serializer_class = TemplatePeticaoSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['area_id', 'tipo_peticao']


class TemplateDetailView(generics.RetrieveAPIView):
    """
    Detalhes de um template específico

    GET /api/v1/petitions/templates/123/
    """
    queryset = TemplatePeticao.query.all()
    serializer_class = TemplatePeticaoSerializer
    permission_classes = [IsAuthenticated]
