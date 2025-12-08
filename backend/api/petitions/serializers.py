"""
Petitions Serializers
"""
from rest_framework import serializers
from database.models import AreaDireito, PeticaoGerada, TemplatePeticao


class AreaDireitoSerializer(serializers.Serializer):
    """Serializer para áreas do direito"""
    id = serializers.IntegerField(read_only=True)
    nome = serializers.CharField()
    descricao = serializers.CharField()
    icone = serializers.CharField()
    cor = serializers.CharField()


class GeneratePetitionSerializer(serializers.Serializer):
    """Serializer para requisição de geração de petição"""
    area_direito = serializers.CharField(
        required=True,
        help_text="Nome da área do direito (ex: 'Direito Civil')"
    )
    contexto = serializers.CharField(
        required=True,
        help_text="Contexto do caso - fatos, partes envolvidas, etc"
    )
    cliente_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="ID do cliente (opcional)"
    )

    def validate_area_direito(self, value):
        """Valida se a área do direito existe"""
        areas_validas = [
            'Direito Ambiental',
            'Direito Civil',
            'Direito Criminal',
            'Direito Empresarial',
            'Direito Agrário',
            'Direito Tributário'
        ]
        if value not in areas_validas:
            raise serializers.ValidationError(
                f"Área inválida. Use uma das: {', '.join(areas_validas)}"
            )
        return value


class PeticaoGeradaSerializer(serializers.Serializer):
    """Serializer para petições geradas"""
    id = serializers.IntegerField(read_only=True)
    area = AreaDireitoSerializer(source='area_id', read_only=True)
    titulo = serializers.CharField()
    conteudo = serializers.CharField()
    contexto_usuario = serializers.CharField()
    jurisprudencias_utilizadas = serializers.JSONField()
    doutrinas_utilizadas = serializers.JSONField()
    criado_em = serializers.DateTimeField(read_only=True)


class TemplatePeticaoSerializer(serializers.Serializer):
    """Serializer para templates de petições"""
    id = serializers.IntegerField(read_only=True)
    area = AreaDireitoSerializer(source='area_id', read_only=True)
    nome = serializers.CharField()
    tipo_peticao = serializers.CharField()
    conteudo = serializers.CharField()
    variaveis = serializers.JSONField()
    criado_em = serializers.DateTimeField(read_only=True)
