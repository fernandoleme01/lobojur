"""
Financial URLs
"""
from django.urls import path
from . import views

app_name = 'financial'

urlpatterns = [
    # Cobranças
    path('charges/', views.ChargeListCreateView.as_view(), name='charges-list'),
    path('charges/<str:charge_id>/', views.ChargeDetailView.as_view(), name='charge-detail'),

    # PIX
    path('pix/create/', views.CreatePixChargeView.as_view(), name='pix-create'),

    # Assinaturas
    path('subscriptions/', views.SubscriptionListView.as_view(), name='subscriptions-list'),
    path('subscriptions/create/', views.CreateSubscriptionView.as_view(), name='subscription-create'),

    # Webhook Asaas
    path('webhook/asaas/', views.AsaasWebhookView.as_view(), name='asaas-webhook'),
]
