"""
CRM API Views - IMPLEMENTAÇÃO COMPLETA
"""
from rest_framework import generics, views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import logging

from database.crm_models import (
    Cliente,
    buscar_clientes,
    buscar_cliente_por_id,
    criar_cliente_completo,
    atualizar_cliente,
    buscar_cliente_por_documento
)
from database.db_manager import DatabaseManager
from core.integration_layer import LoboJurCore
from .serializers import ClientSerializer, CreateClientSerializer

logger = logging.getLogger('lobojur.crm')


class ClientListCreateView(views.APIView):
    """
    Lista e cria clientes

    GET /api/v1/crm/clients/?search=joão&status=ativo
    POST /api/v1/crm/clients/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Lista clientes com filtros"""
        try:
            db = DatabaseManager()

            # Construir filtros
            filtros = {}
            if request.query_params.get('search'):
                filtros['nome'] = request.query_params['search']
            if request.query_params.get('cpf'):
                filtros['cpf'] = request.query_params['cpf']
            if request.query_params.get('status'):
                filtros['status'] = request.query_params['status']

            # Paginação
            limit = int(request.query_params.get('limit', 50))
            offset = int(request.query_params.get('offset', 0))

            with db.get_session() as session:
                clientes = buscar_clientes(session, filtros=filtros, limit=limit, offset=offset)
                results = [c.to_dict() for c in clientes]

                return Response({
                    'count': len(results),
                    'results': results
                }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Erro ao listar clientes: {e}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """Cria novo cliente"""
        serializer = CreateClientSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            db = DatabaseManager()
            lobojur = LoboJurCore(config=settings.LOBOJUR_CONFIG)

            with db.get_session() as session:
                cliente = criar_cliente_completo(
                    session,
                    dados=serializer.validated_data,
                    asaas_client=lobojur.asaas if lobojur.asaas else None
                )

                logger.info(f"Cliente criado: {cliente.nome} (ID: {cliente.id})")
                return Response(cliente.to_dict(), status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Erro ao criar cliente: {e}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ClientDetailView(views.APIView):
    """
    Detalhes, atualização e exclusão de cliente

    GET /api/v1/crm/clients/123/
    PUT /api/v1/crm/clients/123/
    DELETE /api/v1/crm/clients/123/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """Busca cliente por ID"""
        try:
            db = DatabaseManager()
            with db.get_session() as session:
                cliente = buscar_cliente_por_id(session, pk)
                if not cliente:
                    return Response({'error': 'Cliente não encontrado'}, status=status.HTTP_404_NOT_FOUND)
                return Response(cliente.to_dict(), status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Erro ao buscar cliente: {e}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        """Atualiza cliente"""
        try:
            db = DatabaseManager()
            with db.get_session() as session:
                cliente = atualizar_cliente(session, cliente_id=pk, dados=request.data)
                logger.info(f"Cliente atualizado: {cliente.nome} (ID: {pk})")
                return Response(cliente.to_dict(), status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Erro ao atualizar cliente: {e}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        """Deleta cliente (soft delete)"""
        try:
            db = DatabaseManager()
            with db.get_session() as session:
                from database.crm_models import StatusCliente
                atualizar_cliente(session, cliente_id=pk, dados={'status': StatusCliente.INATIVO})
                return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Erro ao deletar cliente: {e}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ClientSearchView(views.APIView):
    """
    Busca clientes por nome, CPF ou CNPJ

    GET /api/v1/crm/clients/search/?q=joão
    GET /api/v1/crm/clients/search/?cpf=12345678900
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '')
        cpf = request.query_params.get('cpf', '')
        cnpj = request.query_params.get('cnpj', '')

        if not any([query, cpf, cnpj]):
            return Response({
                'error': 'Forneça pelo menos um parâmetro de busca (q, cpf ou cnpj)'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            db = DatabaseManager()
            with db.get_session() as session:
                if cpf or cnpj:
                    cliente = buscar_cliente_por_documento(session, cpf=cpf, cnpj=cnpj)
                    results = [cliente.to_dict()] if cliente else []
                else:
                    clientes = buscar_clientes(session, filtros={'nome': query}, limit=20)
                    results = [c.to_dict() for c in clientes]

                return Response({
                    'results': results,
                    'count': len(results)
                }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Erro na busca de clientes: {e}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
