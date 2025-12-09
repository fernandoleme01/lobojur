"""
WhatsApp URLs
"""
from django.urls import path
from . import views

app_name = 'whatsapp'

urlpatterns = [
    # Webhook - Recebe mensagens da Evolution API
    path('webhook/', views.WhatsAppWebhookView.as_view(), name='webhook'),

    # Envio de mensagens (Admin)
    path('send/text/', views.SendTextView.as_view(), name='send-text'),
    path('send/document/', views.SendDocumentView.as_view(), name='send-document'),
    path('send/image/', views.SendImageView.as_view(), name='send-image'),

    # Status da instância
    path('status/', views.InstanceStatusView.as_view(), name='status'),

    # Histórico de conversas
    path('conversations/', views.ConversationListView.as_view(), name='conversations'),
    path('conversations/<str:phone>/', views.ConversationDetailView.as_view(), name='conversation-detail'),
]
