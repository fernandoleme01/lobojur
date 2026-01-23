"""Handler para processar mensagens WhatsApp e gerar laudos."""

import logging
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import tempfile

from .evolution_client import EvolutionClient
from ..ocr.pdf_extractor import PDFExtractor
from ..llm.orchestrator import ReportOrchestrator, APIKeys
from ..templates.document_generator import DocumentGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WhatsAppHandler:
    """
    Handler para processar mensagens do WhatsApp e gerar laudos.

    Workflow:
    1. Recebe PDF/imagem via WhatsApp
    2. Processa com OCR
    3. Analisa com Multi-IA
    4. Gera laudo
    5. Envia de volta via WhatsApp
    """

    def __init__(
        self,
        evolution_client: EvolutionClient,
        api_keys: APIKeys,
        admin_numbers: Optional[List[str]] = None
    ):
        """
        Inicializa handler.

        Args:
            evolution_client: Cliente Evolution API
            api_keys: Chaves das APIs (Claude, Gemini, Perplexity)
            admin_numbers: Números autorizados (None = todos)
        """
        self.evolution = evolution_client
        self.api_keys = api_keys
        self.admin_numbers = admin_numbers or []
        self.orchestrator = ReportOrchestrator(api_keys)
        self.pdf_extractor = PDFExtractor(use_ocr=True)
        self.doc_generator = DocumentGenerator()

        # Estados de conversa (usuário: estado)
        self.user_states: Dict[str, Dict] = {}

    def is_authorized(self, phone_number: str) -> bool:
        """Verifica se número está autorizado."""
        if not self.admin_numbers:
            return True  # Todos autorizados se lista vazia
        return phone_number in self.admin_numbers

    async def handle_message(self, message_data: Dict[str, Any]) -> None:
        """
        Processa mensagem recebida.

        Args:
            message_data: Dados da mensagem do webhook
        """
        try:
            # Extrair informações da mensagem
            phone = message_data.get('key', {}).get('remoteJid', '').split('@')[0]
            message_type = message_data.get('messageType')
            message_text = message_data.get('message', {}).get('conversation', '')

            logger.info(f"Mensagem de {phone}: tipo={message_type}")

            # Verificar autorização
            if not self.is_authorized(phone):
                await self.evolution.send_text(
                    phone,
                    "❌ Desculpe, você não está autorizado a usar este serviço."
                )
                return

            # Processar comando de texto
            if message_type == 'conversation' or message_type == 'extendedTextMessage':
                await self.handle_text_message(phone, message_text)

            # Processar documento PDF
            elif message_type == 'documentMessage':
                await self.handle_document(phone, message_data)

            # Processar imagem
            elif message_type == 'imageMessage':
                await self.handle_image(phone, message_data)

            else:
                await self.evolution.send_text(
                    phone,
                    "ℹ️ Por favor, envie um *documento PDF* ou *imagem* do contrato para análise."
                )

        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {str(e)}")
            if 'phone' in locals():
                await self.evolution.send_text(
                    phone,
                    f"❌ Erro ao processar: {str(e)}\n\nTente novamente ou entre em contato com suporte."
                )

    async def handle_text_message(self, phone: str, text: str) -> None:
        """
        Processa mensagem de texto (comandos).

        Args:
            phone: Número do telefone
            text: Texto da mensagem
        """
        text_lower = text.lower().strip()

        # Comando: /start ou /menu
        if text_lower in ['/start', '/menu', 'menu', 'começar', 'oi', 'olá']:
            await self.send_welcome(phone)

        # Comando: /ajuda
        elif text_lower in ['/ajuda', '/help', 'ajuda', 'help']:
            await self.send_help(phone)

        # Comando: /status
        elif text_lower in ['/status', 'status']:
            status = await self.evolution.get_instance_status()
            await self.evolution.send_text(
                phone,
                f"🤖 *Status do Sistema*\n\n"
                f"Conexão: {status.get('state', 'Desconhecido')}\n"
                f"Sistema: ✅ Operacional"
            )

        else:
            await self.evolution.send_text(
                phone,
                "ℹ️ Comando não reconhecido.\n\n"
                "Envie */menu* para ver opções ou envie um *PDF do contrato* para análise."
            )

    async def handle_document(self, phone: str, message_data: Dict) -> None:
        """
        Processa documento PDF.

        Args:
            phone: Número do telefone
            message_data: Dados da mensagem
        """
        try:
            # Enviar reação de recebido
            message_id = message_data.get('key', {}).get('id')
            if message_id:
                await self.evolution.send_reaction(phone, message_id, "👍")

            # Enviar mensagem de processamento
            await self.evolution.send_text(
                phone,
                "📄 *Documento recebido!*\n\n"
                "🔄 Iniciando análise completa...\n"
                "⏱️ Tempo estimado: 3-5 minutos\n\n"
                "_Aguarde enquanto nossos agentes de IA analisam o contrato..._"
            )

            # Status digitando
            await self.evolution.send_typing(phone, 5)

            # Baixar documento
            media_url = message_data.get('message', {}).get('documentMessage', {}).get('url')
            filename = message_data.get('message', {}).get('documentMessage', {}).get('fileName', 'documento.pdf')

            if not media_url:
                raise ValueError("URL da mídia não encontrada")

            # Criar diretório temporário
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_path = Path(tmpdir)

                # Baixar arquivo
                pdf_path = tmp_path / filename
                await self.evolution.download_media(media_url, str(pdf_path))

                # Extrair texto
                await self.evolution.send_text(
                    phone,
                    "📖 Extraindo texto do documento..."
                )

                extracted_data = self.pdf_extractor.extract_text(str(pdf_path))
                contract_text = extracted_data['text']
                num_pages = extracted_data['num_pages']

                if not contract_text.strip():
                    await self.evolution.send_text(
                        phone,
                        "❌ Não foi possível extrair texto do documento.\n\n"
                        "Verifique se o PDF não está protegido ou corrompido."
                    )
                    return

                # Análise Multi-IA
                await self.evolution.send_text(
                    phone,
                    f"✅ Texto extraído ({num_pages} páginas)\n\n"
                    f"🤖 Executando análise Multi-IA:\n"
                    f"├─ 🔍 Perplexity: Pesquisas jurídicas\n"
                    f"├─ 🧠 Gemini: Análise documental\n"
                    f"└─ ✍️ Claude: Geração do laudo"
                )

                metadata = {
                    "num_paginas": num_pages,
                    "origem": "WhatsApp",
                    "telefone": phone,
                    "data_analise": datetime.now().isoformat()
                }

                # Executar análise
                result = await self.orchestrator.generate_complete_report(
                    contract_text=contract_text,
                    contract_metadata=metadata,
                    enable_web_research=True
                )

                # Gerar laudo em DOCX
                await self.evolution.send_text(
                    phone,
                    "📝 Gerando laudo técnico..."
                )

                report_data = {
                    "parecer_tecnico": result['final_report'],
                    "analise_clausulas": result['contract_analysis'].contract_summary,
                    "riscos_juridicos": result['contract_analysis'].legal_risks,
                    "sintese_analise": result['gemini_analysis'].get('analysis', ''),
                    **metadata
                }

                output_path = self.doc_generator.generate_full_report(
                    analysis_data=report_data,
                    format="docx",
                    filename=f"laudo_{phone}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )

                # Enviar laudo
                await self.evolution.send_document(
                    phone,
                    str(output_path),
                    caption="✅ *Laudo Técnico Completo*\n\n"
                           f"📊 Páginas analisadas: {num_pages}\n"
                           f"🤖 Análise Multi-IA concluída\n"
                           f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}"
                )

                # Enviar resumo em texto
                summary_text = self._generate_summary_text(result)
                await self.evolution.send_text(phone, summary_text)

                # Enviar menu de opções
                await self.evolution.send_buttons(
                    phone,
                    "📋 O que deseja fazer agora?",
                    "Escolha uma opção:",
                    [
                        {"id": "1", "text": "📄 Analisar outro contrato"},
                        {"id": "2", "text": "❓ Fazer pergunta sobre o laudo"},
                        {"id": "3", "text": "📊 Ver resumo executivo"}
                    ]
                )

                logger.info(f"Análise concluída para {phone}")

        except Exception as e:
            logger.error(f"Erro ao processar documento: {str(e)}")
            await self.evolution.send_text(
                phone,
                f"❌ *Erro no processamento*\n\n"
                f"{str(e)}\n\n"
                f"Tente novamente ou entre em contato com suporte."
            )

    async def handle_image(self, phone: str, message_data: Dict) -> None:
        """
        Processa imagem (foto do contrato).

        Args:
            phone: Número do telefone
            message_data: Dados da mensagem
        """
        await self.evolution.send_text(
            phone,
            "📸 *Imagem recebida!*\n\n"
            "🔄 Processamento de imagens em desenvolvimento.\n"
            "Por enquanto, envie o contrato em *PDF* para análise completa.\n\n"
            "💡 *Dica:* Use um app de scanner para converter fotos em PDF."
        )

    async def send_welcome(self, phone: str) -> None:
        """Envia mensagem de boas-vindas."""
        welcome = """
🐺 *Bem-vindo ao LoboLab!*

Sistema Inteligente de Análise de Contratos com Multi-IA

🤖 *Como funciona:*
1. Envie o PDF do contrato
2. Aguarde 3-5 minutos
3. Receba o laudo técnico completo!

✨ *Tecnologias:*
├─ 🔍 Perplexity AI - Pesquisas jurídicas
├─ 🧠 Gemini - Análise documental
└─ ✍️ Claude - Geração de laudos

📋 *O que analisamos:*
✓ Conformidade legal
✓ Riscos jurídicos e financeiros
✓ Cláusulas abusivas
✓ Obrigações das partes
✓ Recomendações técnicas

💡 *Comandos:*
• /menu - Ver este menu
• /ajuda - Obter ajuda
• /status - Ver status do sistema

*Pronto para começar?*
Envie seu contrato em PDF! 📄
"""
        await self.evolution.send_text(phone, welcome)

    async def send_help(self, phone: str) -> None:
        """Envia mensagem de ajuda."""
        help_text = """
❓ *Ajuda - LoboLab*

*📄 Como enviar contrato:*
1. Envie o arquivo PDF do contrato
2. Aguarde a análise (3-5 min)
3. Receba o laudo técnico

*🔍 O que é analisado:*
• Estrutura do contrato
• Partes envolvidas
• Cláusulas principais
• Aspectos financeiros
• Riscos jurídicos
• Conformidade legal
• Recomendações

*💰 Custos:*
Análise completa: R$ 5-15 por contrato
(Custo das APIs de IA)

*⚠️ Importante:*
• PDFs protegidos não podem ser processados
• Qualidade do OCR depende da imagem
• Laudos são assistidos por IA
• Sempre revise com advogado

*📞 Suporte:*
Em caso de problemas, entre em contato com nossa equipe.

*Comandos:*
/menu - Menu principal
/status - Ver status
"""
        await self.evolution.send_text(phone, help_text)

    def _generate_summary_text(self, result: Dict) -> str:
        """Gera resumo em texto da análise."""
        try:
            analysis = result['contract_analysis']

            summary = f"""
📊 *RESUMO DA ANÁLISE*

━━━━━━━━━━━━━━━━━━━━━
*📋 INFORMAÇÕES GERAIS*
━━━━━━━━━━━━━━━━━━━━━

{analysis.contract_summary[:500]}...

━━━━━━━━━━━━━━━━━━━━━
*⚠️ PRINCIPAIS RISCOS*
━━━━━━━━━━━━━━━━━━━━━

{analysis.legal_risks[:500]}...

━━━━━━━━━━━━━━━━━━━━━
*💡 RECOMENDAÇÕES*
━━━━━━━━━━━━━━━━━━━━━

{analysis.recommendations[:500]}...

━━━━━━━━━━━━━━━━━━━━━

📄 *Laudo completo enviado em anexo*

✅ Análise realizada com sucesso!
"""
            return summary

        except Exception as e:
            return "✅ Análise concluída! Veja o laudo completo no documento anexado."
