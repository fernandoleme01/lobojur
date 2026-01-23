"""Extrator de texto de arquivos PDF com suporte a OCR."""

import io
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

import fitz  # PyMuPDF
from PIL import Image
from pdf2image import convert_from_path, convert_from_bytes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFExtractor:
    """Classe para extrair texto de arquivos PDF usando OCR quando necessário."""

    def __init__(self, use_ocr: bool = True, dpi: int = 300):
        """
        Inicializa o extrator de PDF.

        Args:
            use_ocr: Se True, usa OCR para páginas que não contêm texto extraível
            dpi: Resolução DPI para conversão de imagens (padrão: 300)
        """
        self.use_ocr = use_ocr
        self.dpi = dpi

    def extract_text(self, pdf_path: Union[str, Path, bytes]) -> Dict[str, any]:
        """
        Extrai texto de um arquivo PDF.

        Args:
            pdf_path: Caminho para o arquivo PDF ou bytes do PDF

        Returns:
            Dicionário contendo:
                - text: Texto completo extraído
                - pages: Lista de textos por página
                - metadata: Metadados do documento
                - num_pages: Número total de páginas
        """
        try:
            if isinstance(pdf_path, bytes):
                doc = fitz.open(stream=pdf_path, filetype="pdf")
            else:
                doc = fitz.open(pdf_path)

            # Extrair metadados
            metadata = doc.metadata

            pages_text = []
            full_text = []

            for page_num in range(len(doc)):
                page = doc[page_num]

                # Tentar extrair texto direto
                text = page.get_text()

                # Se não houver texto e OCR estiver habilitado, usar OCR
                if not text.strip() and self.use_ocr:
                    logger.info(f"Usando OCR na página {page_num + 1}")
                    text = self._ocr_page(page)

                pages_text.append({
                    'page_number': page_num + 1,
                    'text': text.strip()
                })
                full_text.append(text)

            doc.close()

            return {
                'text': '\n\n'.join(full_text),
                'pages': pages_text,
                'metadata': metadata,
                'num_pages': len(pages_text)
            }

        except Exception as e:
            logger.error(f"Erro ao extrair texto do PDF: {str(e)}")
            raise

    def _ocr_page(self, page) -> str:
        """
        Aplica OCR em uma página específica do PDF.

        Args:
            page: Objeto de página do PyMuPDF

        Returns:
            Texto extraído via OCR
        """
        try:
            # Importar pytesseract apenas se OCR for necessário
            import pytesseract

            # Converter página para imagem
            pix = page.get_pixmap(matrix=fitz.Matrix(self.dpi/72, self.dpi/72))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # Aplicar OCR
            text = pytesseract.image_to_string(img, lang='por')

            return text

        except ImportError:
            logger.warning("pytesseract não está instalado. OCR não disponível.")
            return ""
        except Exception as e:
            logger.error(f"Erro ao aplicar OCR: {str(e)}")
            return ""

    def extract_tables(self, pdf_path: Union[str, Path, bytes]) -> List[List[List[str]]]:
        """
        Extrai tabelas do PDF.

        Args:
            pdf_path: Caminho para o arquivo PDF ou bytes

        Returns:
            Lista de tabelas encontradas (cada tabela é uma lista de linhas)
        """
        try:
            if isinstance(pdf_path, bytes):
                doc = fitz.open(stream=pdf_path, filetype="pdf")
            else:
                doc = fitz.open(pdf_path)

            all_tables = []

            for page_num in range(len(doc)):
                page = doc[page_num]
                tables = page.find_tables()

                for table in tables:
                    if table:
                        table_data = table.extract()
                        all_tables.append(table_data)

            doc.close()
            return all_tables

        except Exception as e:
            logger.error(f"Erro ao extrair tabelas: {str(e)}")
            return []

    def extract_images(self, pdf_path: Union[str, Path, bytes], output_dir: Optional[Path] = None) -> List[Dict]:
        """
        Extrai imagens do PDF.

        Args:
            pdf_path: Caminho para o arquivo PDF ou bytes
            output_dir: Diretório para salvar imagens (opcional)

        Returns:
            Lista de informações sobre imagens extraídas
        """
        try:
            if isinstance(pdf_path, bytes):
                doc = fitz.open(stream=pdf_path, filetype="pdf")
            else:
                doc = fitz.open(pdf_path)

            images_info = []

            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images()

                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = doc.extract_image(xref)

                    image_info = {
                        'page': page_num + 1,
                        'index': img_index,
                        'width': base_image['width'],
                        'height': base_image['height'],
                        'ext': base_image['ext']
                    }

                    # Salvar imagem se output_dir foi fornecido
                    if output_dir:
                        output_dir = Path(output_dir)
                        output_dir.mkdir(parents=True, exist_ok=True)

                        image_path = output_dir / f"page{page_num+1}_img{img_index}.{base_image['ext']}"
                        with open(image_path, 'wb') as f:
                            f.write(base_image['image'])

                        image_info['saved_path'] = str(image_path)

                    images_info.append(image_info)

            doc.close()
            return images_info

        except Exception as e:
            logger.error(f"Erro ao extrair imagens: {str(e)}")
            return []

    def get_pdf_info(self, pdf_path: Union[str, Path, bytes]) -> Dict:
        """
        Obtém informações sobre o PDF.

        Args:
            pdf_path: Caminho para o arquivo PDF ou bytes

        Returns:
            Dicionário com informações do PDF
        """
        try:
            if isinstance(pdf_path, bytes):
                doc = fitz.open(stream=pdf_path, filetype="pdf")
            else:
                doc = fitz.open(pdf_path)

            info = {
                'num_pages': len(doc),
                'metadata': doc.metadata,
                'is_encrypted': doc.is_encrypted,
                'page_sizes': []
            }

            for page_num in range(len(doc)):
                page = doc[page_num]
                rect = page.rect
                info['page_sizes'].append({
                    'page': page_num + 1,
                    'width': rect.width,
                    'height': rect.height
                })

            doc.close()
            return info

        except Exception as e:
            logger.error(f"Erro ao obter informações do PDF: {str(e)}")
            raise
