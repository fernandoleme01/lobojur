"""
Custom exception handler for Django REST Framework
"""
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger('lobojur.api')


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides more detailed error messages
    """
    # Call DRF's default exception handler first
    response = drf_exception_handler(exc, context)

    # Log the exception
    logger.error(f"API Exception: {exc}", exc_info=True, extra={
        'context': context,
        'view': context.get('view').__class__.__name__ if context.get('view') else None,
        'request': context.get('request').path if context.get('request') else None,
    })

    if response is not None:
        # Customize response format
        custom_response_data = {
            'error': True,
            'status_code': response.status_code,
            'message': str(exc),
            'details': response.data if response.data else None
        }
        response.data = custom_response_data
    else:
        # Handle non-DRF exceptions
        custom_response_data = {
            'error': True,
            'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'message': 'Erro interno do servidor',
            'details': str(exc) if logger.level == logging.DEBUG else None
        }
        response = Response(custom_response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response
