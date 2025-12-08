"""
CRM Serializers
"""
from rest_framework import serializers


class ClientSerializer(serializers.Serializer):
    """Serializer para clientes"""
    id = serializers.IntegerField(read_only=True)
    nome = serializers.CharField(required=True)
    cpf = serializers.CharField(required=False, allow_blank=True)
    cnpj = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    telefone = serializers.CharField(required=False, allow_blank=True)
    endereco = serializers.CharField(required=False, allow_blank=True)
    criado_em = serializers.DateTimeField(read_only=True)
