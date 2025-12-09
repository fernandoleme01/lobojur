"""
URL Configuration for LoboJur API
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger/OpenAPI Schema
schema_view = get_schema_view(
    openapi.Info(
        title="LoboJur API",
        default_version='v1',
        description="""
        API completa para sistema jurídico LoboJur

        **Recursos**:
        - Geração automática de petições com IA
        - CRM de clientes
        - Gestão financeira (Asaas)
        - Pesquisa processual (Escavador)
        - Kanban de tarefas
        - Agenda e calendário
        - Integração WhatsApp
        - RAG jurídico (jurisprudências, doutrinas, legislação)

        **Autenticação**: JWT Bearer Token
        """,
        terms_of_service="https://lobojur.com/terms/",
        contact=openapi.Contact(email="contato@lobojur.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API v1
    path('api/v1/', include('api.urls')),

    # Authentication
    path('api/v1/auth/', include('api.authentication.urls')),

    # Swagger/OpenAPI Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
