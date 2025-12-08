"""
API v1 URL Configuration
"""
from django.urls import path, include

app_name = 'api'

urlpatterns = [
    # CRM
    path('crm/', include('api.crm.urls')),

    # Petições
    path('petitions/', include('api.petitions.urls')),

    # Financeiro
    path('financial/', include('api.financial.urls')),

    # Kanban
    path('kanban/', include('api.kanban.urls')),

    # Agenda
    path('agenda/', include('api.agenda.urls')),

    # Documentos
    path('documents/', include('api.documents.urls')),

    # WhatsApp
    path('whatsapp/', include('api.whatsapp.urls')),

    # RAG / Pesquisa Jurídica
    path('research/', include('api.research.urls')),
]
