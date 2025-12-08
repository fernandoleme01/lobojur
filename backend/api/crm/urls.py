"""
CRM URLs
"""
from django.urls import path
from . import views

app_name = 'crm'

urlpatterns = [
    path('clients/', views.ClientListCreateView.as_view(), name='clients-list'),
    path('clients/<int:pk>/', views.ClientDetailView.as_view(), name='client-detail'),
    path('clients/search/', views.ClientSearchView.as_view(), name='client-search'),
]
