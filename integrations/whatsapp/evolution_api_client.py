"""
Cliente para Evolution API - WhatsApp Business
"""
import requests
import json
from typing import Dict, List, Optional
import base64
import logging

logger = logging.getLogger(__name__)


class EvolutionAPIClient:
    """Cliente para integração com Evolution API"""

    def __init__(
        self,
        api_url: str,
        api_key: str,
        instance_name: str
    ):
        """
        Inicializa cliente Evolution API

        Args:
            api_url: URL base da API (ex: https://api.evolution.com)
            api_key: Chave de API
            instance_name: Nome da instância WhatsApp
        """
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.instance_name = instance_name
        self.headers = {
            'apikey': api_key,
            'Content-Type': 'application/json'
        }

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Dict = None,
        files: Dict = None
    ) -> Dict:
        """Faz requisição à API"""
        url = f"{self.api_url}/{endpoint}"

        headers = self.headers.copy()
        if files:
            del headers['Content-Type']  # Deixar requests definir

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data if not files else None,
                files=files,
                timeout=30
            )
            response.raise_for_status()
            return response.json() if response.text else {}
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro Evolution API: {str(e)}")
            raise

    # ==================== MENSAGENS ====================

    def send_text(
        self,
        phone: str,
        message: str
    ) -> Dict:
        """
        Envia mensagem de texto

        Args:
            phone: Número com DDI (ex: 5511999999999)
            message: Texto da mensagem

        Returns:
            Dados da mensagem enviada
        """
        data = {
            "number": phone,
            "text": message
        }

        return self._request(
            "POST",
            f"message/sendText/{self.instance_name}",
            data
        )

    def send_image(
        self,
        phone: str,
        image_url: str = None,
        image_base64: str = None,
        caption: str = None
    ) -> Dict:
        """
        Envia imagem

        Args:
            phone: Número
            image_url: URL da imagem
            image_base64: Imagem em base64
            caption: Legenda

        Returns:
            Dados da mensagem
        """
        data = {
            "number": phone,
            "caption": caption or ""
        }

        if image_url:
            data["image"] = image_url
        elif image_base64:
            data["image"] = image_base64

        return self._request(
            "POST",
            f"message/sendMedia/{self.instance_name}",
            data
        )

    def send_document(
        self,
        phone: str,
        document: bytes = None,
        document_url: str = None,
        filename: str = "documento.pdf",
        caption: str = None
    ) -> Dict:
        """
        Envia documento

        Args:
            phone: Número
            document: Bytes do documento
            document_url: URL do documento
            filename: Nome do arquivo
            caption: Legenda
        """
        data = {
            "number": phone,
            "fileName": filename,
            "caption": caption or ""
        }

        if document_url:
            data["document"] = document_url
        elif document:
            # Converter para base64
            data["document"] = base64.b64encode(document).decode('utf-8')

        return self._request(
            "POST",
            f"message/sendMedia/{self.instance_name}",
            data
        )

    def send_audio(
        self,
        phone: str,
        audio: bytes = None,
        audio_url: str = None
    ) -> Dict:
        """Envia áudio"""
        data = {"number": phone}

        if audio_url:
            data["audio"] = audio_url
        elif audio:
            data["audio"] = base64.b64encode(audio).decode('utf-8')

        return self._request(
            "POST",
            f"message/sendMedia/{self.instance_name}",
            data
        )

    def send_button(
        self,
        phone: str,
        title: str,
        description: str,
        buttons: List[Dict]
    ) -> Dict:
        """
        Envia mensagem com botões

        Args:
            phone: Número
            title: Título
            description: Descrição
            buttons: Lista de botões [{"id": "1", "text": "Sim"}]
        """
        data = {
            "number": phone,
            "title": title,
            "description": description,
            "buttons": buttons,
            "footerText": "LoboJur"
        }

        return self._request(
            "POST",
            f"message/sendButtons/{self.instance_name}",
            data
        )

    def send_list(
        self,
        phone: str,
        title: str,
        description: str,
        button_text: str,
        sections: List[Dict]
    ) -> Dict:
        """
        Envia lista interativa

        Args:
            sections: [
                {
                    "title": "Seção 1",
                    "rows": [
                        {"id": "1", "title": "Opção 1", "description": "Desc"}
                    ]
                }
            ]
        """
        data = {
            "number": phone,
            "title": title,
            "description": description,
            "buttonText": button_text,
            "sections": sections
        }

        return self._request(
            "POST",
            f"message/sendList/{self.instance_name}",
            data
        )

    # ==================== GRUPOS ====================

    def create_group(
        self,
        name: str,
        participants: List[str]
    ) -> Dict:
        """
        Cria grupo

        Args:
            name: Nome do grupo
            participants: Lista de números
        """
        data = {
            "subject": name,
            "participants": participants
        }

        return self._request(
            "POST",
            f"group/create/{self.instance_name}",
            data
        )

    # ==================== WEBHOOK ====================

    def set_webhook(
        self,
        webhook_url: str,
        events: List[str] = None
    ) -> Dict:
        """
        Configura webhook

        Args:
            webhook_url: URL para receber webhooks
            events: Eventos específicos ou None para todos
        """
        data = {
            "url": webhook_url,
            "enabled": True
        }

        if events:
            data["events"] = events

        return self._request(
            "POST",
            f"webhook/set/{self.instance_name}",
            data
        )

    # ==================== INSTÂNCIA ====================

    def get_instance_status(self) -> Dict:
        """Verifica status da instância"""
        return self._request(
            "GET",
            f"instance/connectionState/{self.instance_name}"
        )

    def get_qrcode(self) -> Dict:
        """Obtém QR Code para conectar"""
        return self._request(
            "GET",
            f"instance/qrcode/{self.instance_name}"
        )

    def logout(self) -> Dict:
        """Desconecta instância"""
        return self._request(
            "DELETE",
            f"instance/logout/{self.instance_name}"
        )

    # ==================== MÍDIA ====================

    async def download_media(self, media_url: str) -> bytes:
        """
        Baixa mídia do WhatsApp

        Args:
            media_url: URL da mídia

        Returns:
            Bytes do arquivo
        """
        response = requests.get(media_url, timeout=30)
        response.raise_for_status()
        return response.content

    # ==================== PERFIL ====================

    def get_profile_pic(self, phone: str) -> Dict:
        """Obtém foto de perfil"""
        return self._request(
            "GET",
            f"chat/getProfilePicUrl/{self.instance_name}?number={phone}"
        )

    def set_profile_name(self, name: str) -> Dict:
        """Define nome do perfil"""
        data = {"name": name}
        return self._request(
            "POST",
            f"chat/updateProfileName/{self.instance_name}",
            data
        )

    def set_profile_status(self, status: str) -> Dict:
        """Define status do perfil"""
        data = {"status": status}
        return self._request(
            "POST",
            f"chat/updateProfileStatus/{self.instance_name}",
            data
        )


# ==================== WEBHOOK HANDLER ====================

class EvolutionWebhookHandler:
    """Processa webhooks recebidos do Evolution API"""

    @staticmethod
    def process_webhook(payload: Dict) -> Dict:
        """
        Processa webhook recebido

        Args:
            payload: Dados do webhook

        Returns:
            Dados processados
        """
        event = payload.get('event')
        data = payload.get('data', {})

        handlers = {
            'messages.upsert': EvolutionWebhookHandler._handle_message,
            'messages.update': EvolutionWebhookHandler._handle_message_update,
            'connection.update': EvolutionWebhookHandler._handle_connection,
            'qrcode.updated': EvolutionWebhookHandler._handle_qrcode
        }

        handler = handlers.get(event)
        if handler:
            return handler(data)

        return {"status": "event_not_handled", "event": event}

    @staticmethod
    def _handle_message(data: Dict) -> Dict:
        """Processa nova mensagem"""
        message = data.get('message', {})

        return {
            'type': 'message',
            'phone': data.get('key', {}).get('remoteJid', '').replace('@s.whatsapp.net', ''),
            'from_me': data.get('key', {}).get('fromMe', False),
            'message_type': message.get('type'),
            'text': message.get('conversation') or message.get('extendedTextMessage', {}).get('text'),
            'media': message.get('imageMessage') or message.get('documentMessage'),
            'timestamp': data.get('messageTimestamp')
        }

    @staticmethod
    def _handle_message_update(data: Dict) -> Dict:
        """Processa atualização de mensagem (lida, entregue, etc)"""
        return {
            'type': 'message_update',
            'status': data.get('update', {}).get('status')
        }

    @staticmethod
    def _handle_connection(data: Dict) -> Dict:
        """Processa atualização de conexão"""
        return {
            'type': 'connection',
            'state': data.get('state'),
            'connected': data.get('state') == 'open'
        }

    @staticmethod
    def _handle_qrcode(data: Dict) -> Dict:
        """Processa atualização de QR Code"""
        return {
            'type': 'qrcode',
            'qrcode': data.get('qrcode')
        }


# ==================== EXEMPLO DE USO ====================

def exemplo_evolution_api():
    """Exemplo de uso da Evolution API"""

    # Inicializar cliente
    evolution = EvolutionAPIClient(
        api_url="https://sua-api.evolution.com",
        api_key="SUA_API_KEY",
        instance_name="lobojur_instance"
    )

    # Verificar status
    status = evolution.get_instance_status()
    print(f"Status: {status}")

    # Enviar mensagem simples
    evolution.send_text(
        phone="5511999999999",
        message="Olá! Sou o assistente do LoboJur 👋"
    )

    # Enviar mensagem com botões
    evolution.send_button(
        phone="5511999999999",
        title="Como posso ajudar?",
        description="Escolha uma opção:",
        buttons=[
            {"id": "1", "text": "📋 Cadastrar cliente"},
            {"id": "2", "text": "📄 Gerar procuração"},
            {"id": "3", "text": "💰 Consultar pagamento"}
        ]
    )

    # Enviar lista
    evolution.send_list(
        phone="5511999999999",
        title="Áreas do Direito",
        description="Selecione a área:",
        button_text="Ver áreas",
        sections=[
            {
                "title": "Áreas Disponíveis",
                "rows": [
                    {"id": "civil", "title": "⚖️ Direito Civil"},
                    {"id": "criminal", "title": "🔒 Direito Criminal"},
                    {"id": "trabalhista", "title": "💼 Direito Trabalhista"}
                ]
            }
        ]
    )

    # Enviar documento
    with open('procuracao.pdf', 'rb') as f:
        evolution.send_document(
            phone="5511999999999",
            document=f.read(),
            filename="Procuracao_Cliente.pdf",
            caption="📄 Sua procuração está pronta!"
        )

    # Configurar webhook
    evolution.set_webhook(
        webhook_url="https://seu-servidor.com/webhook/whatsapp",
        events=["messages.upsert", "connection.update"]
    )
