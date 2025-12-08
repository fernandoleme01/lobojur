"""
Kanban API Views
"""
from rest_framework import generics, views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class BoardListCreateView(generics.ListCreateAPIView):
    """
    GET /api/v1/kanban/boards/
    POST /api/v1/kanban/boards/
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # TODO: Implementar com modelos Django
        return []


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/v1/kanban/boards/123/
    PUT /api/v1/kanban/boards/123/
    DELETE /api/v1/kanban/boards/123/
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # TODO: Implementar com modelos Django
        return []


class ColumnListCreateView(generics.ListCreateAPIView):
    """
    GET /api/v1/kanban/boards/123/columns/
    POST /api/v1/kanban/boards/123/columns/
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # TODO: Implementar com modelos Django
        return []


class CardListView(generics.ListAPIView):
    """
    GET /api/v1/kanban/cards/?board=123
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # TODO: Implementar com modelos Django
        return []


class CardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/v1/kanban/cards/123/
    PUT /api/v1/kanban/cards/123/
    DELETE /api/v1/kanban/cards/123/
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # TODO: Implementar com modelos Django
        return []


class MoveCardView(views.APIView):
    """
    POST /api/v1/kanban/cards/123/move/
    {
        "column_id": 456,
        "position": 2
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        # TODO: Implementar lógica de movimentação
        return Response({
            'message': 'Card movido com sucesso'
        }, status=status.HTTP_200_OK)
