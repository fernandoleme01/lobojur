"""
CRM Serializers - IMPLEMENTAÇÃO COMPLETA
"""
from rest_framework import serializers


class ClientSerializer(serializers.Serializer):
    """Serializer para leitura de clientes"""
    id = serializers.IntegerField(read_only=True)
    nome = serializers.CharField()
    tipo_pessoa = serializers.CharField()
    cpf = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    cnpj = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    telefone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    whatsapp = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    status = serializers.CharField(required=False)
    asaas_customer_id = serializers.CharField(read_only=True, required=False)
    criado_em = serializers.DateTimeField(read_only=True, required=False)


class CreateClientSerializer(serializers.Serializer):
    """Serializer para criação de clientes"""
    nome = serializers.CharField(required=True, max_length=200)
    tipo_pessoa = serializers.ChoiceField(choices=['fisica', 'juridica'], default='fisica')
    cpf = serializers.CharField(max_length=11, required=False, allow_blank=True)
    cnpj = serializers.CharField(max_length=14, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    telefone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    celular = serializers.CharField(max_length=20, required=False, allow_blank=True)
    whatsapp = serializers.CharField(max_length=20, required=False, allow_blank=True)
    cep = serializers.CharField(max_length=8, required=False, allow_blank=True)
    logradouro = serializers.CharField(max_length=200, required=False, allow_blank=True)
    numero = serializers.CharField(max_length=20, required=False, allow_blank=True)
    cidade = serializers.CharField(max_length=100, required=False, allow_blank=True)
    estado = serializers.CharField(max_length=2, required=False, allow_blank=True)
    observacoes = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        """Validações customizadas"""
        tipo_pessoa = attrs.get('tipo_pessoa', 'fisica')
        if tipo_pessoa == 'fisica' and not attrs.get('cpf'):
            raise serializers.ValidationError({'cpf': 'CPF é obrigatório para pessoa física'})
        if tipo_pessoa == 'juridica' and not attrs.get('cnpj'):
            raise serializers.ValidationError({'cnpj': 'CNPJ é obrigatório para pessoa jurídica'})
        return attrs
