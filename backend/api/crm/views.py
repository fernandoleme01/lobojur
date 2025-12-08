"""
CRM API Views
"""
from rest_framework import generics, views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import ClientSerializer


class ClientListCreateView(generics.ListCreateAPIView):
    """
    Lista e cria clientes

    GET /api/v1/crm/clients/
    POST /api/v1/crm/clients/
    {
        "nome": "João Silva",
        "cpf": "12345678900",
        "email": "joao@email.com",
        "telefone": "5511999999999"
    }
    """
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # TODO: Implementar com CRMService
        return []


class ClientDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Detalhes, atualização e exclusão de cliente

    GET /api/v1/crm/clients/123/
    PUT /api/v1/crm/clients/123/
    DELETE /api/v1/crm/clients/123/
    """
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # TODO: Implementar com CRMService
        return []


class ClientSearchView(views.APIView):
    """
    Busca clientes por nome, CPF ou telefone

    GET /api/v1/crm/clients/search/?q=joão
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '')

        if not query:
            return Response({
                'error': 'Parâmetro "q" é obrigatório'
            }, status=status.HTTP_400_BAD_REQUEST)

        # TODO: Implementar busca com CRMService
        return Response({
            'results': [],
            'count': 0
        }, status=status.HTTP_200_OK)
