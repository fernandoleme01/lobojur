# 📱 Configuração WhatsApp - LoboLab

Guia completo para integrar o LoboLab com WhatsApp usando Evolution API.

---

## 🎯 Visão Geral

Com a integração WhatsApp, seus clientes podem:

✅ Enviar contratos em PDF pelo WhatsApp
✅ Receber laudos técnicos completos automaticamente
✅ Fazer perguntas sobre contratos
✅ Obter análises em 3-5 minutos

---

## 🛠️ Pré-requisitos

1. **Servidor/VPS** com Docker (recomendado)
2. **Evolution API** instalado e funcionando
3. **Número WhatsApp Business** (recomendado, mas não obrigatório)
4. **API Keys**: Claude, Gemini, Perplexity

---

## 📦 Instalação Evolution API

### Opção 1: Docker Compose (Recomendado)

1. Crie o arquivo `docker-compose.yml`:

```yaml
version: '3.3'

services:
  evolution-api:
    image: atendai/evolution-api:latest
    ports:
      - "8080:8080"
    environment:
      # Servidor
      - SERVER_URL=http://localhost:8080
      - SERVER_PORT=8080

      # API
      - AUTHENTICATION_API_KEY=SUA_CHAVE_API_AQUI

      # Database
      - DATABASE_ENABLED=true
      - DATABASE_CONNECTION_URI=mongodb://mongo:27017/evolution
      - DATABASE_CONNECTION_DB_PREFIX_NAME=evolution

      # Webhook (URL do seu servidor LoboLab)
      - WEBHOOK_GLOBAL_URL=http://seu-servidor:8000/webhook
      - WEBHOOK_GLOBAL_ENABLED=true
      - WEBHOOK_GLOBAL_WEBHOOK_BY_EVENTS=true
      - WEBHOOK_EVENTS_APPLICATION_STARTUP=false
      - WEBHOOK_EVENTS_QRCODE_UPDATED=false
      - WEBHOOK_EVENTS_MESSAGES_SET=true
      - WEBHOOK_EVENTS_MESSAGES_UPSERT=true
      - WEBHOOK_EVENTS_MESSAGES_UPDATE=true

      # Logs
      - LOG_LEVEL=info
      - LOG_COLOR=true

      # Storage
      - STORE_MESSAGES=true
      - STORE_MESSAGE_UP=true
      - STORE_CONTACTS=true
      - STORE_CHATS=true

    depends_on:
      - mongo

    networks:
      - evolution-network

  mongo:
    image: mongo:6.0
    command: --quiet
    ports:
      - "27017:27017"
    environment:
      - MONGO_INITDB_ROOT_USERNAME=root
      - MONGO_INITDB_ROOT_PASSWORD=root
    volumes:
      - mongo_data:/data/db
    networks:
      - evolution-network

networks:
  evolution-network:
    driver: bridge

volumes:
  mongo_data:
```

2. Inicie os containers:

```bash
docker-compose up -d
```

3. Aguarde alguns segundos e verifique:

```bash
# Ver logs
docker-compose logs -f evolution-api

# Testar API
curl http://localhost:8080
```

### Opção 2: NPM (Desenvolvimento)

```bash
# Instalar
npm install -g evolution-api

# Executar
evolution-api start
```

---

## 🔑 Configuração do LoboLab

### 1. Atualizar `.env`

Edite o arquivo `.env` e adicione:

```bash
# Evolution API
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=SUA_CHAVE_API_AQUI
EVOLUTION_INSTANCE_NAME=lobolab

# WhatsApp Admin (números autorizados, separados por vírgula)
# Deixe vazio para permitir todos
WHATSAPP_ADMIN_NUMBERS=5511999999999,5511888888888

# API Keys (já configuradas)
CLAUDE_API_KEY=sk-ant-...
GEMINI_API_KEY=AIza...
PERPLEXITY_API_KEY=pplx-...
```

### 2. Instalar Dependências

```bash
pip install -r requirements.txt
```

---

## 📱 Conectar WhatsApp

### 1. Criar Instância

```bash
curl -X POST 'http://localhost:8080/instance/create' \
-H 'apikey: SUA_CHAVE_API_AQUI' \
-H 'Content-Type: application/json' \
-d '{
  "instanceName": "lobolab",
  "qrcode": true,
  "integration": "WHATSAPP-BAILEYS"
}'
```

### 2. Obter QR Code

```bash
curl -X GET 'http://localhost:8080/instance/connect/lobolab' \
-H 'apikey: SUA_CHAVE_API_AQUI'
```

Ou acesse no navegador:
```
http://localhost:8080/instance/qrcode/lobolab
```

### 3. Escanear QR Code

1. Abra WhatsApp no celular
2. Menu (⋮) → Dispositivos conectados
3. Conectar dispositivo
4. Escaneie o QR Code

✅ **Pronto!** WhatsApp conectado.

### 4. Verificar Conexão

```bash
curl -X GET 'http://localhost:8080/instance/connectionState/lobolab' \
-H 'apikey: SUA_CHAVE_API_AQUI'
```

Deve retornar: `"state": "open"`

---

## 🚀 Iniciar LoboLab WhatsApp

### 1. Iniciar Servidor Webhook

```bash
# Terminal 1: API Webhook
uvicorn src.api.webhook:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Interface Web (Opcional)

```bash
# Terminal 2: Interface Streamlit
streamlit run app.py
```

---

## 📞 Testar Sistema

### 1. Teste Manual

Envie mensagem para o número conectado:

```
/start
```

Resposta esperada:
```
🐺 Bem-vindo ao LoboLab!
[...]
```

### 2. Teste com PDF

1. Envie um PDF de contrato
2. Aguarde 3-5 minutos
3. Receba o laudo técnico!

### 3. Teste via API

```bash
curl -X POST 'http://localhost:8000/send-test' \
-H 'Content-Type: application/json' \
-d '{
  "phone": "5511999999999",
  "message": "🤖 Teste do LoboLab!"
}'
```

---

## 🔄 Fluxo Completo

```
1. 📱 Usuário envia PDF pelo WhatsApp
        ↓
2. 📨 Evolution API recebe mensagem
        ↓
3. 🔔 Webhook notifica LoboLab
        ↓
4. 📥 LoboLab baixa o PDF
        ↓
5. 🔍 Extração OCR do texto
        ↓
6. 🤖 Análise Multi-IA:
   ├─ Perplexity: Pesquisas
   ├─ Gemini: Análise estrutural
   └─ Claude: Geração do laudo
        ↓
7. 📄 Gera laudo em DOCX
        ↓
8. 📤 Envia laudo via WhatsApp
        ↓
9. ✅ Usuário recebe resultado!
```

---

## 💬 Comandos Disponíveis

### Para Usuários

| Comando | Descrição |
|---------|-----------|
| `/start` ou `/menu` | Menu principal |
| `/ajuda` ou `/help` | Ajuda completa |
| `/status` | Status do sistema |
| Enviar PDF | Iniciar análise |

### Respostas Automáticas

- ✅ Confirmação de recebimento
- 👍 Reação na mensagem
- 🔄 Atualizações de progresso
- 📊 Resumo da análise
- 📄 Laudo completo em DOCX

---

## 🔒 Segurança

### Números Autorizados

Configure `WHATSAPP_ADMIN_NUMBERS` para restringir acesso:

```bash
# Apenas estes números podem usar
WHATSAPP_ADMIN_NUMBERS=5511999999999,5521888888888

# Todos podem usar (deixe vazio)
WHATSAPP_ADMIN_NUMBERS=
```

### Proteção de API

1. Use chaves API fortes
2. Configure firewall no servidor
3. Use HTTPS em produção
4. Monitore logs de acesso

---

## 🌐 Deploy em Produção

### 1. Servidor VPS (Recomendado)

Requisitos mínimos:
- **CPU**: 2 cores
- **RAM**: 4GB
- **Disco**: 20GB SSD
- **Largura de banda**: Ilimitada
- **SO**: Ubuntu 22.04 LTS

Providers recomendados:
- DigitalOcean (Droplet $12/mês)
- AWS EC2 (t3.medium)
- Google Cloud (e2-medium)
- Contabo VPS

### 2. Configurar Domínio

```nginx
# /etc/nginx/sites-available/lobolab
server {
    listen 80;
    server_name api.lobolab.com.br;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 3. SSL (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.lobolab.com.br
```

### 4. Process Manager (PM2)

```bash
# Instalar PM2
npm install -g pm2

# Iniciar API
pm2 start "uvicorn src.api.webhook:app --host 0.0.0.0 --port 8000" --name lobolab-api

# Auto-start
pm2 startup
pm2 save
```

### 5. Monitoramento

```bash
# Logs em tempo real
pm2 logs lobolab-api

# Status
pm2 status

# Métricas
pm2 monit
```

---

## 📊 Custos

### Infraestrutura

| Item | Custo Mensal |
|------|--------------|
| VPS (4GB RAM) | $10-20 |
| Domínio | $1-2 |
| SSL (Let's Encrypt) | Grátis |
| **Total Infra** | **$11-22** |

### APIs (por análise)

| API | Custo |
|-----|-------|
| Claude | $0.50-2.00 |
| Gemini | $0.10-0.50 |
| Perplexity | $0.20-0.80 |
| **Total/análise** | **$0.80-3.30** |

### Exemplo de Uso

100 análises/mês:
- Infraestrutura: $20
- APIs (100 × $2): $200
- **Total**: ~$220/mês

Preço de venda sugerido: $10-50 por análise
**Margem**: 500-2500% 🚀

---

## 🐛 Troubleshooting

### Erro: "Handler não inicializado"

**Solução:**
```bash
# Verificar variáveis de ambiente
cat .env

# Verificar logs
pm2 logs lobolab-api
```

### Erro: "Evolution API não responde"

**Solução:**
```bash
# Verificar status do container
docker-compose ps

# Reiniciar
docker-compose restart evolution-api
```

### WhatsApp desconecta

**Solução:**
- Verifique conexão com internet
- Não use WhatsApp Web simultaneamente
- Reconecte escaneando QR Code novamente

### Mensagens não chegam

**Solução:**
1. Verificar webhook configurado:
```bash
curl http://localhost:8080/webhook/lobolab \
  -H 'apikey: SUA_CHAVE'
```

2. Verificar logs do Evolution:
```bash
docker-compose logs -f evolution-api
```

3. Testar manualmente:
```bash
curl http://localhost:8000/health
```

---

## 📝 Logs e Debug

### Evolution API Logs

```bash
# Docker
docker-compose logs -f evolution-api

# Ver últimas 100 linhas
docker-compose logs --tail=100 evolution-api
```

### LoboLab Logs

```bash
# PM2
pm2 logs lobolab-api

# Python logging
tail -f lobolab.log
```

### Debug Mode

```bash
# Ativar debug
export LOG_LEVEL=DEBUG

# Rodar em foreground
uvicorn src.api.webhook:app --host 0.0.0.0 --port 8000 --log-level debug
```

---

## 🚀 Recursos Avançados

### 1. Múltiplas Instâncias

Configure várias instâncias WhatsApp para diferentes departamentos:

```bash
# Comercial
EVOLUTION_INSTANCE_NAME=lobolab-comercial

# Suporte
EVOLUTION_INSTANCE_NAME=lobolab-suporte
```

### 2. Respostas Customizadas

Edite `src/whatsapp/whatsapp_handler.py` para personalizar mensagens.

### 3. Integração com CRM

Use webhooks para notificar seu CRM:

```python
# Em whatsapp_handler.py
async def handle_document(...):
    # ... análise ...

    # Notificar CRM
    await self.notify_crm(phone, result)
```

### 4. Métricas e Analytics

```python
# Salvar métricas
from prometheus_client import Counter

analyses_counter = Counter('lobolab_analyses_total', 'Total de análises')

# ... ao processar ...
analyses_counter.inc()
```

---

## ✅ Checklist de Deploy

- [ ] Evolution API instalado e funcionando
- [ ] WhatsApp conectado via QR Code
- [ ] Variáveis de ambiente configuradas
- [ ] Webhook configurado corretamente
- [ ] SSL/HTTPS em produção
- [ ] PM2 configurado para auto-start
- [ ] Logs funcionando corretamente
- [ ] Testes manuais realizados
- [ ] Monitoramento configurado
- [ ] Backup configurado

---

## 📞 Suporte

- **Issues**: https://github.com/fernandoleme01/lobojur/issues
- **Documentação Evolution**: https://doc.evolution-api.com/
- **Discord Evolution**: https://evolution-api.com/discord

---

**🐺 LoboLab - WhatsApp Integration**

*Análise de contratos diretamente no WhatsApp!*

Versão: 1.0.0
Atualizado: 2024
