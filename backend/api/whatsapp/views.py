"""
WhatsApp API Views
"""
from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import asyncio
import logging

from core.integration_layer import LoboJurCore
from integrations.whatsapp.evolution_api_client import EvolutionWebhookHandler
from .serializers import (
    SendTextSerializer,
    SendDocumentSerializer,
    SendImageSerializer,
    WebhookMessageSerializer,
)

logger = logging.getLogger('lobojur.whatsapp')


@method_decorator(csrf_exempt, name='dispatch')
class WhatsAppWebhookView(views.APIView):
    """
    Webhook para receber mensagens do WhatsApp via Evolution API

    POST /api/v1/whatsapp/webhook/
    {
        "event": "messages.upsert",
        "instance": "lobojur",
        "data": {
            "key": {"remoteJid": "5511999999999@s.whatsapp.net"},
            "message": {"conversation": "Olá, quero cadastrar um cliente"},
            "messageType": "conversation",
            "pushName": "João Silva"
        }
    }

    Este endpoint é PÚBLICO (chamado pela Evolution API)
    """
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            # Processar payload do webhook
            processed = EvolutionWebhookHandler.process_webhook(request.data)

            if not processed:
                return Response({
                    'status': 'ignored',
                    'message': 'Evento ignorado (não é mensagem nova)'
                }, status=status.HTTP_200_OK)

            logger.info(f"Mensagem WhatsApp recebida de {processed['phone']}: {processed['message'][:50]}")

            # Inicializar LoboJur Core
            lobojur = LoboJurCore(config=settings.LOBOJUR_CONFIG)

            # Processar mensagem de forma assíncrona
            resposta = asyncio.run(
                lobojur.processar_mensagem_whatsapp(
                    phone=processed['phone'],
                    message=processed['message'],
                    media=processed.get('media')
                )
            )

            logger.info(f"Resposta enviada para {processed['phone']}: {resposta[:50]}")

            return Response({
                'status': 'processed',
                'response_sent': resposta,
                'phone': processed['phone']
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Erro ao processar webhook WhatsApp: {e}", exc_info=True)
            return Response({
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SendTextView(views.APIView):
    """
    Envia mensagem de texto via WhatsApp (Admin)

    POST /api/v1/whatsapp/send/text/
    {
        "phone": "5511999999999",
        "message": "Sua petição está pronta!"
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SendTextSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            lobojur = LoboJurCore(config=settings.LOBOJUR_CONFIG)

            if not lobojur.whatsapp:
                return Response({
                    'error': 'WhatsApp não configurado'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            resultado = lobojur.whatsapp.send_text(
                phone=serializer.validated_data['phone'],
                message=serializer.validated_data['message']
            )

            return Response({
                'status': 'sent',
                'result': resultado
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}", exc_info=True)
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SendDocumentView(views.APIView):
    """
    Envia documento via WhatsApp

    POST /api/v1/whatsapp/send/document/
    {
        "phone": "5511999999999",
        "document": "https://...",
        "filename": "peticao.pdf",
        "caption": "Sua petição"
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SendDocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            lobojur = LoboJurCore(config=settings.LOBOJUR_CONFIG)

            if not lobojur.whatsapp:
                return Response({
                    'error': 'WhatsApp não configurado'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            resultado = lobojur.whatsapp.send_document(
                phone=serializer.validated_data['phone'],
                document=serializer.validated_data['document'],
                filename=serializer.validated_data['filename'],
                caption=serializer.validated_data.get('caption', '')
            )

            return Response({
                'status': 'sent',
                'result': resultado
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Erro ao enviar documento: {e}", exc_info=True)
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SendImageView(views.APIView):
    """
    Envia imagem via WhatsApp

    POST /api/v1/whatsapp/send/image/
    {
        "phone": "5511999999999",
        "image_url": "https://...",
        "caption": "QR Code do PIX"
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SendImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            lobojur = LoboJurCore(config=settings.LOBOJUR_CONFIG)

            if not lobojur.whatsapp:
                return Response({
                    'error': 'WhatsApp não configurado'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            resultado = lobojur.whatsapp.send_image(
                phone=serializer.validated_data['phone'],
                image_url=serializer.validated_data['image_url'],
                caption=serializer.validated_data.get('caption', '')
            )

            return Response({
                'status': 'sent',
                'result': resultado
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Erro ao enviar imagem: {e}", exc_info=True)
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InstanceStatusView(views.APIView):
    """
    Verifica status da instância WhatsApp

    GET /api/v1/whatsapp/status/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            lobojur = LoboJurCore(config=settings.LOBOJUR_CONFIG)

            if not lobojur.whatsapp:
                return Response({
                    'error': 'WhatsApp não configurado'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            status_info = lobojur.whatsapp.check_instance_status()

            return Response(status_info, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Erro ao verificar status: {e}", exc_info=True)
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConversationListView(views.APIView):
    """
    Lista conversas do WhatsApp

    GET /api/v1/whatsapp/conversations/

    TODO: Implementar armazenamento de histórico no BD
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'message': 'Em desenvolvimento'
        }, status=status.HTTP_501_NOT_IMPLEMENTED)


class ConversationDetailView(views.APIView):
    """
    Detalhes de uma conversa específica

    GET /api/v1/whatsapp/conversations/5511999999999/

    TODO: Implementar armazenamento de histórico no BD
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, phone):
        return Response({
            'message': 'Em desenvolvimento',
            'phone': phone
        }, status=status.HTTP_501_NOT_IMPLEMENTED)
