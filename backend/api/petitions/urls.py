"""
Petitions URLs
"""
from django.urls import path
from . import views

app_name = 'petitions'

urlpatterns = [
    # Áreas do direito
    path('areas/', views.AreasListView.as_view(), name='areas-list'),

    # Geração de petições
    path('generate/', views.GeneratePetitionView.as_view(), name='generate'),
    path('', views.PetitionListView.as_view(), name='list'),
    path('<int:pk>/', views.PetitionDetailView.as_view(), name='detail'),
    path('<int:pk>/export/pdf/', views.ExportPDFView.as_view(), name='export-pdf'),
    path('<int:pk>/export/docx/', views.ExportDOCXView.as_view(), name='export-docx'),

    # Templates
    path('templates/', views.TemplateListView.as_view(), name='templates-list'),
    path('templates/<int:pk>/', views.TemplateDetailView.as_view(), name='template-detail'),
]
