"""
Documents API Views
"""
from rest_framework import generics, views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser


class UploadDocumentView(views.APIView):
    """
    Upload de documentos (PDF, DOCX, imagens)

    POST /api/v1/documents/upload/
    Content-Type: multipart/form-data

    Processa com Vision AI se for imagem
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file_obj = request.FILES.get('file')

        if not file_obj:
            return Response({
                'error': 'Nenhum arquivo enviado'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # TODO: Processar documento com DocumentService
            # - Extrair texto
            # - Se for imagem, usar Vision AI
            # - Salvar no banco

            return Response({
                'id': 1,
                'filename': file_obj.name,
                'size': file_obj.size,
                'content_type': file_obj.content_type,
                'message': 'Documento enviado com sucesso'
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DocumentListView(generics.ListAPIView):
    """
    GET /api/v1/documents/
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # TODO: Implementar listagem de documentos
        return []


class DocumentDetailView(generics.RetrieveDestroyAPIView):
    """
    GET /api/v1/documents/123/
    DELETE /api/v1/documents/123/
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # TODO: Implementar detalhes de documento
        return []


class GenerateProcuracaoView(views.APIView):
    """
    Gera procuração automaticamente

    POST /api/v1/documents/generate/procuracao/
    {
        "outorgante": {...},
        "outorgado": {...},
        "poderes": ["representar em juízo", ...]
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # TODO: Gerar procuração com template
        return Response({
            'message': 'Geração de procuração em desenvolvimento'
        }, status=status.HTTP_501_NOT_IMPLEMENTED)


class GenerateContratoView(views.APIView):
    """
    Gera contrato automaticamente

    POST /api/v1/documents/generate/contrato/
    {
        "tipo": "prestacao_servicos",
        "partes": [...],
        "clausulas": [...]
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # TODO: Gerar contrato com template
        return Response({
            'message': 'Geração de contrato em desenvolvimento'
        }, status=status.HTTP_501_NOT_IMPLEMENTED)
