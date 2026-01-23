"""Cliente para Evolution API - WhatsApp Integration."""

import logging
import httpx
import asyncio
from typing import Dict, List, Optional, Any
from pathlib import Path
import base64

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EvolutionClient:
    """
    Cliente para Evolution API.

    Permite enviar e receber mensagens, documentos e mídias via WhatsApp.
    """

    def __init__(
        self,
        api_url: str,
        api_key: str,
        instance_name: str
    ):
        """
        Inicializa cliente Evolution API.

        Args:
            api_url: URL da Evolution API (ex: http://localhost:8080)
            api_key: Chave de API
            instance_name: Nome da instância WhatsApp
        """
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.instance_name = instance_name
        self.headers = {
            "apikey": api_key,
            "Content-Type": "application/json"
        }

    async def send_text(
        self,
        phone_number: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Envia mensagem de texto.

        Args:
            phone_number: Número com DDI (ex: 5511999999999)
            message: Texto da mensagem

        Returns:
            Resposta da API
        """
        try:
            url = f"{self.api_url}/message/sendText/{self.instance_name}"

            payload = {
                "number": phone_number,
                "text": message
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Erro ao enviar texto: {str(e)}")
            raise

    async def send_document(
        self,
        phone_number: str,
        document_path: str,
        caption: Optional[str] = None,
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Envia documento.

        Args:
            phone_number: Número com DDI
            document_path: Caminho do documento
            caption: Legenda opcional
            filename: Nome do arquivo

        Returns:
            Resposta da API
        """
        try:
            url = f"{self.api_url}/message/sendMedia/{self.instance_name}"

            # Ler arquivo e converter para base64
            with open(document_path, 'rb') as f:
                file_data = base64.b64encode(f.read()).decode('utf-8')

            if not filename:
                filename = Path(document_path).name

            payload = {
                "number": phone_number,
                "mediatype": "document",
                "media": file_data,
                "fileName": filename,
                "caption": caption or f"📄 {filename}"
            }

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Erro ao enviar documento: {str(e)}")
            raise

    async def send_image(
        self,
        phone_number: str,
        image_path: str,
        caption: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Envia imagem.

        Args:
            phone_number: Número com DDI
            image_path: Caminho da imagem
            caption: Legenda

        Returns:
            Resposta da API
        """
        try:
            url = f"{self.api_url}/message/sendMedia/{self.instance_name}"

            with open(image_path, 'rb') as f:
                file_data = base64.b64encode(f.read()).decode('utf-8')

            payload = {
                "number": phone_number,
                "mediatype": "image",
                "media": file_data,
                "caption": caption or "📸 Imagem"
            }

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Erro ao enviar imagem: {str(e)}")
            raise

    async def download_media(
        self,
        media_url: str,
        output_path: str
    ) -> str:
        """
        Baixa mídia recebida.

        Args:
            media_url: URL da mídia
            output_path: Caminho de saída

        Returns:
            Caminho do arquivo salvo
        """
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(media_url)
                response.raise_for_status()

                with open(output_path, 'wb') as f:
                    f.write(response.content)

                logger.info(f"Mídia baixada: {output_path}")
                return output_path

        except Exception as e:
            logger.error(f"Erro ao baixar mídia: {str(e)}")
            raise

    async def send_typing(
        self,
        phone_number: str,
        duration: int = 5
    ) -> Dict[str, Any]:
        """
        Envia status de 'digitando'.

        Args:
            phone_number: Número com DDI
            duration: Duração em segundos

        Returns:
            Resposta da API
        """
        try:
            url = f"{self.api_url}/chat/presence/{self.instance_name}"

            payload = {
                "number": phone_number,
                "presence": "composing"
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()

                # Aguardar duração
                await asyncio.sleep(duration)

                # Parar de digitar
                payload["presence"] = "available"
                await client.post(url, headers=self.headers, json=payload)

                return response.json()

        except Exception as e:
            logger.error(f"Erro ao enviar typing: {str(e)}")
            return {}

    async def get_instance_status(self) -> Dict[str, Any]:
        """
        Obtém status da instância.

        Returns:
            Status da instância
        """
        try:
            url = f"{self.api_url}/instance/connectionState/{self.instance_name}"

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Erro ao obter status: {str(e)}")
            return {"state": "error", "error": str(e)}

    async def send_buttons(
        self,
        phone_number: str,
        title: str,
        description: str,
        buttons: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Envia mensagem com botões interativos.

        Args:
            phone_number: Número com DDI
            title: Título da mensagem
            description: Descrição
            buttons: Lista de botões [{"id": "1", "text": "Botão 1"}]

        Returns:
            Resposta da API
        """
        try:
            url = f"{self.api_url}/message/sendButtons/{self.instance_name}"

            payload = {
                "number": phone_number,
                "title": title,
                "description": description,
                "buttons": buttons
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Erro ao enviar botões: {str(e)}")
            raise

    async def send_list(
        self,
        phone_number: str,
        title: str,
        description: str,
        button_text: str,
        sections: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Envia mensagem com lista interativa.

        Args:
            phone_number: Número com DDI
            title: Título
            description: Descrição
            button_text: Texto do botão
            sections: Seções da lista

        Returns:
            Resposta da API
        """
        try:
            url = f"{self.api_url}/message/sendList/{self.instance_name}"

            payload = {
                "number": phone_number,
                "title": title,
                "description": description,
                "buttonText": button_text,
                "sections": sections
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Erro ao enviar lista: {str(e)}")
            raise

    async def send_reaction(
        self,
        phone_number: str,
        message_id: str,
        emoji: str
    ) -> Dict[str, Any]:
        """
        Envia reação a uma mensagem.

        Args:
            phone_number: Número com DDI
            message_id: ID da mensagem
            emoji: Emoji da reação

        Returns:
            Resposta da API
        """
        try:
            url = f"{self.api_url}/message/sendReaction/{self.instance_name}"

            payload = {
                "number": phone_number,
                "key": {
                    "id": message_id
                },
                "reaction": emoji
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Erro ao enviar reação: {str(e)}")
            return {}
