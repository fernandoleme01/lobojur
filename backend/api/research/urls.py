"""
Research URLs
"""
from django.urls import path
from . import views

app_name = 'research'

urlpatterns = [
    # Jurisprudências
    path('jurisprudence/', views.JurisprudenceSearchView.as_view(), name='jurisprudence-search'),
    path('jurisprudence/add/', views.AddJurisprudenceView.as_view(), name='jurisprudence-add'),

    # Doutrinas
    path('doctrine/', views.DoctrineSearchView.as_view(), name='doctrine-search'),
    path('doctrine/add/', views.AddDoctrineView.as_view(), name='doctrine-add'),

    # Legislação
    path('legislation/', views.LegislationSearchView.as_view(), name='legislation-search'),

    # Processos (Escavador)
    path('process/<str:numero>/', views.ProcessSearchView.as_view(), name='process-search'),
    path('process/<str:numero>/monitor/', views.MonitorProcessView.as_view(), name='process-monitor'),

    # Busca híbrida
    path('hybrid/', views.HybridSearchView.as_view(), name='hybrid-search'),
]
