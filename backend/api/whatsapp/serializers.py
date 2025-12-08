"""
WhatsApp Serializers
"""
from rest_framework import serializers


class SendTextSerializer(serializers.Serializer):
    """Serializer para envio de texto"""
    phone = serializers.CharField(
        required=True,
        help_text="Número com DDI (ex: 5511999999999)"
    )
    message = serializers.CharField(required=True)


class SendDocumentSerializer(serializers.Serializer):
    """Serializer para envio de documento"""
    phone = serializers.CharField(required=True)
    document = serializers.URLField(
        required=True,
        help_text="URL do documento ou base64"
    )
    filename = serializers.CharField(required=True)
    caption = serializers.CharField(required=False, allow_blank=True)


class SendImageSerializer(serializers.Serializer):
    """Serializer para envio de imagem"""
    phone = serializers.CharField(required=True)
    image_url = serializers.URLField(required=True)
    caption = serializers.CharField(required=False, allow_blank=True)


class WebhookMessageSerializer(serializers.Serializer):
    """Serializer para mensagens recebidas via webhook"""
    event = serializers.CharField()
    instance = serializers.CharField()
    data = serializers.JSONField()
