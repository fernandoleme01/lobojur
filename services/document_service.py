"""
Serviço de processamento de documentos
"""
import os
from pathlib import Path
from typing import Dict, Optional
import pdfplumber
from docx import Document


class DocumentService:
    """Serviço para processar documentos enviados pelos usuários"""

    def __init__(self, db_manager):
        """
        Inicializa o serviço de documentos

        Args:
            db_manager: Instância do gerenciador de banco de dados
        """
        self.db = db_manager
        self.upload_dir = Path("data/uploads")
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def processar_documento(self, arquivo_path: str) -> Dict:
        """
        Processa um documento e extrai seu texto

        Args:
            arquivo_path: Caminho do arquivo

        Returns:
            Dicionário com informações do documento e texto extraído
        """
        extensao = Path(arquivo_path).suffix.lower()

        processadores = {
            '.pdf': self._processar_pdf,
            '.docx': self._processar_docx,
            '.doc': self._processar_docx,
            '.txt': self._processar_txt
        }

        if extensao not in processadores:
            raise ValueError(f"Formato de arquivo não suportado: {extensao}")

        return processadores[extensao](arquivo_path)

    def _processar_pdf(self, arquivo_path: str) -> Dict:
        """Extrai texto de arquivo PDF"""
        texto_completo = []

        try:
            with pdfplumber.open(arquivo_path) as pdf:
                for pagina in pdf.pages:
                    texto = pagina.extract_text()
                    if texto:
                        texto_completo.append(texto)

            return {
                'sucesso': True,
                'texto': '\n\n'.join(texto_completo),
                'num_paginas': len(texto_completo),
                'tipo': 'pdf'
            }
        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e),
                'tipo': 'pdf'
            }

    def _processar_docx(self, arquivo_path: str) -> Dict:
        """Extrai texto de arquivo DOCX"""
        try:
            doc = Document(arquivo_path)
            texto_completo = []

            for paragrafo in doc.paragraphs:
                if paragrafo.text.strip():
                    texto_completo.append(paragrafo.text)

            return {
                'sucesso': True,
                'texto': '\n\n'.join(texto_completo),
                'num_paragrafos': len(texto_completo),
                'tipo': 'docx'
            }
        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e),
                'tipo': 'docx'
            }

    def _processar_txt(self, arquivo_path: str) -> Dict:
        """Lê arquivo TXT"""
        try:
            with open(arquivo_path, 'r', encoding='utf-8') as f:
                texto = f.read()

            return {
                'sucesso': True,
                'texto': texto,
                'tipo': 'txt'
            }
        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e),
                'tipo': 'txt'
            }

    def salvar_upload(self, arquivo_bytes: bytes, nome_arquivo: str) -> str:
        """
        Salva arquivo enviado pelo usuário

        Args:
            arquivo_bytes: Bytes do arquivo
            nome_arquivo: Nome original do arquivo

        Returns:
            Caminho do arquivo salvo
        """
        caminho_arquivo = self.upload_dir / nome_arquivo

        with open(caminho_arquivo, 'wb') as f:
            f.write(arquivo_bytes)

        return str(caminho_arquivo)
