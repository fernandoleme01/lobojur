# LoboJur Backend API

API Django REST Framework completa para o sistema LoboJur.

## 🚀 Funcionalidades

### ✅ Implementado

- **Autenticação JWT** - Login seguro com tokens
- **Petições** - Geração automática com IA multi-LLM
- **WhatsApp** - Webhook e envio de mensagens
- **CRM** - Gestão de clientes (estrutura)
- **Financeiro** - Integração Asaas (pagamentos, PIX, assinaturas)
- **Pesquisa Jurídica** - RAG + Escavador
- **Kanban** - Gerenciamento de tarefas (estrutura)
- **Agenda** - Calendário e agendamentos (estrutura)
- **Documentos** - Upload e processamento (estrutura)
- **Swagger/OpenAPI** - Documentação automática

## 📋 Pré-requisitos

- Python 3.10+
- Redis (para Celery)
- PostgreSQL (opcional - SQLite por padrão)

## 🔧 Instalação

### 1. Criar ambiente virtual

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente

```bash
cp .env.example .env
# Editar .env com suas chaves
```

### 4. Executar migrações

```bash
python manage.py migrate
```

### 5. Criar superusuário

```bash
python manage.py createsuperuser
```

### 6. Executar servidor

```bash
python manage.py runserver
```

API disponível em: http://localhost:8000

## 📚 Documentação da API

Após iniciar o servidor, acesse:

- **Swagger UI**: http://localhost:8000/swagger/
- **ReDoc**: http://localhost:8000/redoc/
- **Admin**: http://localhost:8000/admin/

## 🔐 Autenticação

### Obter token JWT

```bash
POST /api/v1/auth/token/
{
    "username": "usuario",
    "password": "senha"
}

# Resposta
{
    "refresh": "eyJ0eXAiOiJKV1QiLC...",
    "access": "eyJ0eXAiOiJKV1QiLC..."
}
```

### Usar token nas requisições

```bash
Authorization: Bearer eyJ0eXAiOiJKV1QiLC...
```

## 📡 Endpoints Principais

### Petições

```bash
# Gerar petição
POST /api/v1/petitions/generate/
{
    "area_direito": "Direito Civil",
    "contexto": "Cliente sofreu danos morais...",
    "cliente_id": 123
}

# Listar petições
GET /api/v1/petitions/

# Exportar PDF
GET /api/v1/petitions/123/export/pdf/
```

### WhatsApp (Webhook)

```bash
# Webhook (público - chamado pela Evolution API)
POST /api/v1/whatsapp/webhook/
{
    "event": "messages.upsert",
    "data": {...}
}

# Enviar mensagem (autenticado)
POST /api/v1/whatsapp/send/text/
{
    "phone": "5511999999999",
    "message": "Sua petição está pronta!"
}
```

### Financeiro (Asaas)

```bash
# Criar cobrança PIX
POST /api/v1/financial/pix/create/
{
    "customer_id": "cus_123",
    "valor": 100.00,
    "descricao": "Honorários advocatícios"
}

# Webhook Asaas (público)
POST /api/v1/financial/webhook/asaas/
```

### Pesquisa Jurídica

```bash
# Buscar jurisprudências
GET /api/v1/research/jurisprudence/?query=dano+moral&tribunal=STJ

# Buscar processo (Escavador)
GET /api/v1/research/process/0001234-56.2020.4.01.3800/

# Busca híbrida (RAG)
POST /api/v1/research/hybrid/
{
    "query": "responsabilidade civil por danos morais",
    "collections": ["jurisprudencias", "doutrinas"],
    "n_results_per_collection": 3
}
```

## 🔄 Celery (Tarefas Assíncronas)

### Iniciar worker

```bash
celery -A lobojur_api worker -l info
```

### Iniciar beat (tarefas agendadas)

```bash
celery -A lobojur_api beat -l info
```

## 🧪 Testes

```bash
pytest
```

## 🐳 Docker (Futuro)

```bash
docker-compose up
```

## 📦 Estrutura do Projeto

```
backend/
├── lobojur_api/          # Configuração Django
│   ├── settings.py      # Settings completas
│   ├── urls.py          # URL principal
│   └── wsgi.py          # WSGI
├── api/                  # Apps da API
│   ├── authentication/  # JWT, login, registro
│   ├── petitions/       # Geração de petições
│   ├── whatsapp/        # Integração WhatsApp
│   ├── crm/             # CRM de clientes
│   ├── financial/       # Asaas - Financeiro
│   ├── research/        # Pesquisa jurídica
│   ├── kanban/          # Gerenciamento tarefas
│   ├── agenda/          # Calendário
│   └── documents/       # Documentos
├── manage.py            # Django CLI
└── requirements.txt     # Dependências
```

## 🛠️ Desenvolvimento

### Adicionar nova app

```bash
python manage.py startapp nome_app api/
```

### Criar migrações

```bash
python manage.py makemigrations
python manage.py migrate
```

### Coletar arquivos estáticos

```bash
python manage.py collectstatic
```

## 🚀 Deploy

### Gunicorn

```bash
pip install gunicorn
gunicorn lobojur_api.wsgi:application
```

### Variáveis de produção

```bash
DEBUG=False
ALLOWED_HOSTS=api.lobojur.com
DJANGO_SECRET_KEY=... # Gerar nova chave
```

## 📝 TODO

- [ ] Implementar queries completas (CRM, Kanban, Agenda)
- [ ] Adicionar testes unitários
- [ ] Implementar cache (Redis)
- [ ] Adicionar rate limiting
- [ ] Implementar pagination customizada
- [ ] Adicionar monitoring (Sentry)
- [ ] Dockerizar aplicação
- [ ] CI/CD pipeline

## 📄 Licença

MIT License
