"""
Webhook FastAPI para receber mensagens do Evolution API.

Execute com: uvicorn src.api.webhook:app --host 0.0.0.0 --port 8000
"""

import os
import logging
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from ..whatsapp.evolution_client import EvolutionClient
from ..whatsapp.whatsapp_handler import WhatsAppHandler
from ..llm.orchestrator import APIKeys

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="LoboLab WhatsApp API",
    description="Webhook para Evolution API - Análise de Contratos",
    version="1.0.0"
)

# Global handler (será inicializado no startup)
whatsapp_handler: Optional[WhatsAppHandler] = None


class WebhookMessage(BaseModel):
    """Modelo de mensagem do webhook."""
    event: str
    instance: str
    data: Dict[str, Any]


@app.on_event("startup")
async def startup_event():
    """Inicializa handler no startup."""
    global whatsapp_handler

    try:
        # Configurar Evolution API
        evolution_url = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
        evolution_key = os.getenv("EVOLUTION_API_KEY")
        evolution_instance = os.getenv("EVOLUTION_INSTANCE_NAME")

        if not evolution_key or not evolution_instance:
            logger.warning("Evolution API não configurada completamente")
            return

        evolution_client = EvolutionClient(
            api_url=evolution_url,
            api_key=evolution_key,
            instance_name=evolution_instance
        )

        # Configurar API keys
        api_keys = APIKeys(
            claude_api_key=os.getenv("CLAUDE_API_KEY"),
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            perplexity_api_key=os.getenv("PERPLEXITY_API_KEY")
        )

        # Números autorizados (opcional)
        admin_numbers_str = os.getenv("WHATSAPP_ADMIN_NUMBERS", "")
        admin_numbers = [n.strip() for n in admin_numbers_str.split(",") if n.strip()]

        # Inicializar handler
        whatsapp_handler = WhatsAppHandler(
            evolution_client=evolution_client,
            api_keys=api_keys,
            admin_numbers=admin_numbers if admin_numbers else None
        )

        logger.info("✅ WhatsApp Handler inicializado com sucesso")
        logger.info(f"Evolution URL: {evolution_url}")
        logger.info(f"Instance: {evolution_instance}")
        logger.info(f"Admin numbers: {len(admin_numbers)} configurados")

    except Exception as e:
        logger.error(f"Erro ao inicializar handler: {str(e)}")


@app.get("/")
async def root():
    """Endpoint raiz."""
    return {
        "service": "LoboLab WhatsApp API",
        "version": "1.0.0",
        "status": "online",
        "description": "Webhook para Evolution API - Análise de Contratos com Multi-IA"
    }


@app.get("/health")
async def health():
    """Health check."""
    return {
        "status": "healthy",
        "handler_initialized": whatsapp_handler is not None
    }


@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Webhook para receber mensagens do Evolution API.

    O Evolution API deve ser configurado para enviar eventos para esta URL.
    """
    try:
        # Obter dados do webhook
        data = await request.json()

        logger.info(f"Webhook recebido: {data.get('event')}")

        # Verificar se handler está inicializado
        if not whatsapp_handler:
            logger.error("Handler não inicializado")
            raise HTTPException(status_code=500, detail="Handler não inicializado")

        # Processar apenas eventos de mensagem
        event = data.get('event')

        if event in ['messages.upsert', 'messages.update']:
            # Obter dados da mensagem
            message_data = data.get('data', {})

            # Processar em background para não bloquear o webhook
            background_tasks.add_task(
                whatsapp_handler.handle_message,
                message_data
            )

            return {"status": "processing", "message": "Mensagem em processamento"}

        return {"status": "ignored", "event": event}

    except Exception as e:
        logger.error(f"Erro no webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/send-test")
async def send_test(phone: str, message: str):
    """
    Endpoint de teste para enviar mensagem.

    Args:
        phone: Número com DDI (ex: 5511999999999)
        message: Mensagem a enviar
    """
    try:
        if not whatsapp_handler:
            raise HTTPException(status_code=500, detail="Handler não inicializado")

        result = await whatsapp_handler.evolution.send_text(phone, message)

        return {
            "status": "sent",
            "result": result
        }

    except Exception as e:
        logger.error(f"Erro ao enviar teste: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def get_status():
    """Obtém status da instância WhatsApp."""
    try:
        if not whatsapp_handler:
            return {"error": "Handler não inicializado"}

        status = await whatsapp_handler.evolution.get_instance_status()

        return {
            "evolution_status": status,
            "handler_ready": True
        }

    except Exception as e:
        logger.error(f"Erro ao obter status: {str(e)}")
        return {"error": str(e)}


# Middleware para log de requisições
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log de todas as requisições."""
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
