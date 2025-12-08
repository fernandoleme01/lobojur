"""
Agenda API Views
"""
from rest_framework import generics, views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class EventListCreateView(generics.ListCreateAPIView):
    """
    GET /api/v1/agenda/events/
    POST /api/v1/agenda/events/
    {
        "titulo": "Audiência",
        "data_inicio": "2025-12-10T14:00:00Z",
        "data_fim": "2025-12-10T16:00:00Z",
        "local": "Fórum Central"
    }
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # TODO: Implementar com modelos Django
        return []


class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/v1/agenda/events/123/
    PUT /api/v1/agenda/events/123/
    DELETE /api/v1/agenda/events/123/
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # TODO: Implementar com modelos Django
        return []


class CancelEventView(views.APIView):
    """
    POST /api/v1/agenda/events/123/cancel/
    {
        "motivo": "Cliente desmarcou"
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        # TODO: Implementar cancelamento
        return Response({
            'message': 'Evento cancelado com sucesso'
        }, status=status.HTTP_200_OK)


class CheckAvailabilityView(views.APIView):
    """
    POST /api/v1/agenda/availability/
    {
        "data_inicio": "2025-12-10T14:00:00Z",
        "data_fim": "2025-12-10T16:00:00Z"
    }

    Retorna se o horário está disponível
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # TODO: Implementar verificação de disponibilidade
        return Response({
            'disponivel': True,
            'message': 'Horário disponível'
        }, status=status.HTTP_200_OK)


class SuggestTimesView(views.APIView):
    """
    GET /api/v1/agenda/availability/suggest/?data=2025-12-10&duracao=60

    Sugere horários disponíveis para uma data
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # TODO: Implementar sugestão de horários
        return Response({
            'horarios': [],
            'count': 0
        }, status=status.HTTP_200_OK)


class CalendarListView(generics.ListAPIView):
    """
    GET /api/v1/agenda/calendars/
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # TODO: Implementar com modelos Django
        return []
