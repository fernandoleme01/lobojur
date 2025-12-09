"""
Financial API Views
"""
from rest_framework import generics, views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging

from core.integration_layer import LoboJurCore
from .serializers import (
    CreateChargeSerializer,
    CreatePixSerializer,
    CreateSubscriptionSerializer,
)

logger = logging.getLogger('lobojur.financial')


class ChargeListCreateView(views.APIView):
    """
    Lista e cria cobranças

    GET /api/v1/financial/charges/
    POST /api/v1/financial/charges/
    {
        "customer_id": "cus_123",
        "valor": 100.00,
        "vencimento": "2025-12-15",
        "forma_pagamento": "BOLETO"
    }
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # TODO: Listar cobranças do Asaas
        return Response({
            'charges': [],
            'count': 0
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CreateChargeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            lobojur = LoboJurCore(config=settings.LOBOJUR_CONFIG)

            if not lobojur.asaas:
                return Response({
                    'error': 'Asaas não configurado'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            cobranca = lobojur.asaas.criar_cobranca(
                customer_id=serializer.validated_data['customer_id'],
                valor=serializer.validated_data['valor'],
                vencimento=serializer.validated_data['vencimento'],
                forma_pagamento=serializer.validated_data['forma_pagamento']
            )

            return Response(cobranca, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Erro ao criar cobrança: {e}", exc_info=True)
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChargeDetailView(views.APIView):
    """
    Detalhes de uma cobrança

    GET /api/v1/financial/charges/pay_123/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, charge_id):
        try:
            lobojur = LoboJurCore(config=settings.LOBOJUR_CONFIG)

            if not lobojur.asaas:
                return Response({
                    'error': 'Asaas não configurado'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            cobranca = lobojur.asaas.buscar_cobranca(charge_id)
            return Response(cobranca, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Erro ao buscar cobrança: {e}", exc_info=True)
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreatePixChargeView(views.APIView):
    """
    Cria cobrança PIX com QR Code

    POST /api/v1/financial/pix/create/
    {
        "customer_id": "cus_123",
        "valor": 100.00,
        "descricao": "Honorários advocatícios"
    }

    Retorna QR Code e PIX copia-e-cola
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreatePixSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            lobojur = LoboJurCore(config=settings.LOBOJUR_CONFIG)

            if not lobojur.asaas:
                return Response({
                    'error': 'Asaas não configurado'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            pix_data = lobojur.asaas.criar_cobranca_pix(
                customer_id=serializer.validated_data['customer_id'],
                valor=serializer.validated_data['valor'],
                descricao=serializer.validated_data.get('descricao', '')
            )

            return Response(pix_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Erro ao criar PIX: {e}", exc_info=True)
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SubscriptionListView(views.APIView):
    """
    Lista assinaturas

    GET /api/v1/financial/subscriptions/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # TODO: Listar assinaturas do Asaas
        return Response({
            'subscriptions': [],
            'count': 0
        }, status=status.HTTP_200_OK)


class CreateSubscriptionView(views.APIView):
    """
    Cria assinatura recorrente

    POST /api/v1/financial/subscriptions/create/
    {
        "customer_id": "cus_123",
        "valor": 500.00,
        "ciclo": "MONTHLY"
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateSubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            lobojur = LoboJurCore(config=settings.LOBOJUR_CONFIG)

            if not lobojur.asaas:
                return Response({
                    'error': 'Asaas não configurado'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            assinatura = lobojur.asaas.criar_assinatura(
                customer_id=serializer.validated_data['customer_id'],
                valor=serializer.validated_data['valor'],
                ciclo=serializer.validated_data['ciclo']
            )

            return Response(assinatura, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Erro ao criar assinatura: {e}", exc_info=True)
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class AsaasWebhookView(views.APIView):
    """
    Webhook do Asaas - Recebe notificações de pagamento

    POST /api/v1/financial/webhook/asaas/
    {
        "event": "PAYMENT_RECEIVED",
        "payment": {...}
    }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            lobojur = LoboJurCore(config=settings.LOBOJUR_CONFIG)

            if not lobojur.asaas:
                return Response({
                    'error': 'Asaas não configurado'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            resultado = lobojur.asaas.processar_webhook(request.data)

            logger.info(f"Webhook Asaas processado: {resultado}")

            return Response({
                'status': 'processed',
                'event': resultado.get('event')
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Erro ao processar webhook Asaas: {e}", exc_info=True)
            return Response({
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
