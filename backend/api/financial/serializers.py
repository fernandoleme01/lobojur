"""
Financial Serializers
"""
from rest_framework import serializers


class CreateChargeSerializer(serializers.Serializer):
    """Serializer para criação de cobrança"""
    customer_id = serializers.CharField(required=True)
    valor = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    vencimento = serializers.DateField(required=True)
    forma_pagamento = serializers.ChoiceField(
        choices=['BOLETO', 'CREDIT_CARD', 'PIX'],
        required=True
    )


class CreatePixSerializer(serializers.Serializer):
    """Serializer para criação de PIX"""
    customer_id = serializers.CharField(required=True)
    valor = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    descricao = serializers.CharField(required=False, allow_blank=True)


class CreateSubscriptionSerializer(serializers.Serializer):
    """Serializer para criação de assinatura"""
    customer_id = serializers.CharField(required=True)
    valor = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    ciclo = serializers.ChoiceField(
        choices=['WEEKLY', 'BIWEEKLY', 'MONTHLY', 'QUARTERLY', 'SEMIANNUALLY', 'YEARLY'],
        default='MONTHLY'
    )
