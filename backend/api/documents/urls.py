"""
Documents URLs
"""
from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    # Upload e processamento
    path('upload/', views.UploadDocumentView.as_view(), name='upload'),
    path('', views.DocumentListView.as_view(), name='list'),
    path('<int:pk>/', views.DocumentDetailView.as_view(), name='detail'),

    # Geração de documentos
    path('generate/procuracao/', views.GenerateProcuracaoView.as_view(), name='generate-procuracao'),
    path('generate/contrato/', views.GenerateContratoView.as_view(), name='generate-contrato'),
]
