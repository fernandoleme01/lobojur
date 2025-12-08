"""
Research Serializers
"""
from rest_framework import serializers


class JurisprudenceSearchSerializer(serializers.Serializer):
    """Serializer para busca de jurisprudências"""
    query = serializers.CharField(required=True)
    area = serializers.CharField(required=False, allow_blank=True)
    tribunal = serializers.CharField(required=False, allow_blank=True)
    limit = serializers.IntegerField(required=False, default=5, min_value=1, max_value=20)


class AddJurisprudenceSerializer(serializers.Serializer):
    """Serializer para adicionar jurisprudência"""
    texto = serializers.CharField(required=True)
    tribunal = serializers.CharField(required=False, allow_blank=True)
    numero_processo = serializers.CharField(required=False, allow_blank=True)
    area_direito = serializers.CharField(required=False, allow_blank=True)


class AddDoctrineSerializer(serializers.Serializer):
    """Serializer para adicionar doutrina"""
    texto = serializers.CharField(required=True)
    autor = serializers.CharField(required=False, allow_blank=True)
    obra = serializers.CharField(required=False, allow_blank=True)
    area_direito = serializers.CharField(required=False, allow_blank=True)


class HybridSearchSerializer(serializers.Serializer):
    """Serializer para busca híbrida"""
    query = serializers.CharField(required=True)
    collections = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=['jurisprudencias', 'doutrinas', 'legislacao']
    )
    n_results_per_collection = serializers.IntegerField(
        required=False,
        default=3,
        min_value=1,
        max_value=10
    )
