"""
Agenda URLs
"""
from django.urls import path
from . import views

app_name = 'agenda'

urlpatterns = [
    # Eventos
    path('events/', views.EventListCreateView.as_view(), name='events-list'),
    path('events/<int:pk>/', views.EventDetailView.as_view(), name='event-detail'),
    path('events/<int:pk>/cancel/', views.CancelEventView.as_view(), name='event-cancel'),

    # Disponibilidade
    path('availability/', views.CheckAvailabilityView.as_view(), name='check-availability'),
    path('availability/suggest/', views.SuggestTimesView.as_view(), name='suggest-times'),

    # Calendários
    path('calendars/', views.CalendarListView.as_view(), name='calendars-list'),
]
