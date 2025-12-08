"""
Sistema RAG (Retrieval Augmented Generation) para Documentos Jurídicos
Armazena e recupera:
- Jurisprudências
- Doutrinas
- Legislação
- Templates
- Documentos de clientes
"""
from typing import List, Dict, Optional, Tuple
import chromadb
from chromadb.config import Settings
from pathlib import Path
import pypdf2
from docx import Document
import logging

logger = logging.getLogger(__name__)


class JuridicalRAG:
    """Sistema RAG especializado em documentos jurídicos"""

    def __init__(
        self,
        persist_directory: str = "./data/rag_storage",
        embedding_function=None
    ):
        """
        Inicializa sistema RAG

        Args:
            persist_directory: Diretório para persistir vetores
            embedding_function: Função de embedding customizada
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # Inicializar ChromaDB
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=str(self.persist_directory)
        ))

        # Coleções especializadas
        self.collections = {
            'jurisprudencias': self._get_or_create_collection('jurisprudencias'),
            'doutrinas': self._get_or_create_collection('doutrinas'),
            'legislacao': self._get_or_create_collection('legislacao'),
            'templates': self._get_or_create_collection('templates'),
            'documentos_clientes': self._get_or_create_collection('documentos_clientes'),
            'conhecimento_interno': self._get_or_create_collection('conhecimento_interno')
        }

    def _get_or_create_collection(self, name: str):
        """Obtém ou cria coleção"""
        return self.client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"}  # Similaridade por cosseno
        )

    # ==================== INGESTÃO DE DOCUMENTOS ====================

    def add_jurisprudencia(
        self,
        texto: str,
        metadata: Dict,
        chunk_size: int = 1000,
        overlap: int = 200
    ) -> List[str]:
        """
        Adiciona jurisprudência ao RAG

        Args:
            texto: Texto completo da jurisprudência
            metadata: {
                'tribunal': 'STJ',
                'numero_processo': '...',
                'relator': '...',
                'data_julgamento': '...',
                'area_direito': 'Civil',
                'palavras_chave': ['dano moral', 'indenização'],
                'url': '...'
            }
            chunk_size: Tamanho dos chunks
            overlap: Sobreposição entre chunks

        Returns:
            IDs dos chunks adicionados
        """
        # Dividir texto em chunks com sobreposição
        chunks = self._split_text(texto, chunk_size, overlap)

        ids = []
        documents = []
        metadatas = []

        for i, chunk in enumerate(chunks):
            chunk_id = f"{metadata['numero_processo']}_chunk_{i}"
            ids.append(chunk_id)
            documents.append(chunk)

            # Metadata para cada chunk
            chunk_metadata = metadata.copy()
            chunk_metadata['chunk_index'] = i
            chunk_metadata['total_chunks'] = len(chunks)
            metadatas.append(chunk_metadata)

        # Adicionar à coleção
        self.collections['jurisprudencias'].add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

        logger.info(f"Jurisprudência adicionada: {len(chunks)} chunks")
        return ids

    def add_doutrina(
        self,
        texto: str,
        metadata: Dict,
        chunk_size: int = 1500
    ) -> List[str]:
        """
        Adiciona doutrina (livro, artigo) ao RAG

        Args:
            texto: Texto completo
            metadata: {
                'titulo': '...',
                'autor': '...',
                'ano': 2024,
                'editora': '...',
                'area_direito': '...',
                'tipo': 'livro' ou 'artigo',
                'isbn': '...'
            }
        """
        chunks = self._split_text(texto, chunk_size, 300)

        ids = []
        documents = []
        metadatas = []

        for i, chunk in enumerate(chunks):
            chunk_id = f"{metadata.get('isbn', 'doc')}_{i}"
            ids.append(chunk_id)
            documents.append(chunk)

            chunk_metadata = metadata.copy()
            chunk_metadata['chunk_index'] = i
            metadatas.append(chunk_metadata)

        self.collections['doutrinas'].add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

        return ids

    def add_legislacao(
        self,
        texto: str,
        metadata: Dict
    ) -> List[str]:
        """
        Adiciona legislação (lei, decreto, etc) ao RAG

        Args:
            metadata: {
                'tipo': 'lei', 'decreto', 'portaria',
                'numero': '10.406',
                'ano': 2002,
                'titulo': 'Código Civil',
                'ementa': '...',
                'artigos': {...}  # Opcional: dict com artigos específicos
            }
        """
        # Legislação pode ter artigos separados
        if 'artigos' in metadata:
            return self._add_legislacao_com_artigos(texto, metadata)

        # Ou texto corrido
        chunks = self._split_text(texto, 800, 150)

        ids = []
        for i, chunk in enumerate(chunks):
            ids.append(f"{metadata['tipo']}_{metadata['numero']}_{i}")

        metadatas = [metadata.copy() for _ in chunks]

        self.collections['legislacao'].add(
            ids=ids,
            documents=chunks,
            metadatas=metadatas
        )

        return ids

    def _add_legislacao_com_artigos(
        self,
        texto: str,
        metadata: Dict
    ) -> List[str]:
        """Adiciona legislação com artigos indexados individualmente"""
        ids = []
        documents = []
        metadatas = []

        for artigo_num, artigo_texto in metadata['artigos'].items():
            doc_id = f"{metadata['tipo']}_{metadata['numero']}_art_{artigo_num}"
            ids.append(doc_id)
            documents.append(artigo_texto)

            art_metadata = metadata.copy()
            art_metadata['artigo'] = artigo_num
            del art_metadata['artigos']  # Remover dict de artigos
            metadatas.append(art_metadata)

        self.collections['legislacao'].add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

        return ids

    def add_template(
        self,
        nome: str,
        conteudo: str,
        metadata: Dict
    ) -> str:
        """
        Adiciona template de petição

        Args:
            nome: Nome do template
            conteudo: Texto do template
            metadata: {
                'area_direito': '...',
                'tipo_peticao': 'inicial', 'recurso', etc,
                'variaveis': ['NOME_AUTOR', ...],
                'tags': ['dano moral', ...]
            }
        """
        template_id = f"template_{nome}"

        self.collections['templates'].add(
            ids=[template_id],
            documents=[conteudo],
            metadatas=[metadata]
        )

        return template_id

    def add_documento_cliente(
        self,
        arquivo_path: str,
        cliente_id: int,
        metadata: Dict
    ) -> List[str]:
        """
        Adiciona documento de cliente

        Args:
            arquivo_path: Caminho do arquivo
            cliente_id: ID do cliente
            metadata: {
                'tipo_documento': 'contrato', 'procuração', etc,
                'data': '...',
                'tags': [...]
            }
        """
        # Extrair texto baseado no tipo de arquivo
        texto = self._extract_text(arquivo_path)

        chunks = self._split_text(texto, 1000, 200)

        ids = []
        for i, chunk in enumerate(chunks):
            ids.append(f"cliente_{cliente_id}_doc_{Path(arquivo_path).stem}_{i}")

        metadatas = []
        for _ in chunks:
            chunk_metadata = metadata.copy()
            chunk_metadata['cliente_id'] = cliente_id
            chunk_metadata['arquivo'] = arquivo_path
            metadatas.append(chunk_metadata)

        self.collections['documentos_clientes'].add(
            ids=ids,
            documents=chunks,
            metadatas=metadatas
        )

        return ids

    # ==================== BUSCA E RETRIEVAL ====================

    def search_jurisprudencias(
        self,
        query: str,
        area_direito: Optional[str] = None,
        tribunal: Optional[str] = None,
        n_results: int = 5,
        min_score: float = 0.7
    ) -> List[Dict]:
        """
        Busca jurisprudências relevantes

        Args:
            query: Consulta em linguagem natural
            area_direito: Filtrar por área
            tribunal: Filtrar por tribunal
            n_results: Número de resultados
            min_score: Score mínimo de similaridade

        Returns:
            Lista de jurisprudências com score
        """
        where = {}
        if area_direito:
            where['area_direito'] = area_direito
        if tribunal:
            where['tribunal'] = tribunal

        results = self.collections['jurisprudencias'].query(
            query_texts=[query],
            n_results=n_results,
            where=where if where else None
        )

        return self._format_results(results, min_score)

    def search_doutrinas(
        self,
        query: str,
        area_direito: Optional[str] = None,
        autor: Optional[str] = None,
        n_results: int = 3
    ) -> List[Dict]:
        """Busca doutrinas relevantes"""
        where = {}
        if area_direito:
            where['area_direito'] = area_direito
        if autor:
            where['autor'] = autor

        results = self.collections['doutrinas'].query(
            query_texts=[query],
            n_results=n_results,
            where=where if where else None
        )

        return self._format_results(results)

    def search_legislacao(
        self,
        query: str,
        tipo: Optional[str] = None,
        n_results: int = 5
    ) -> List[Dict]:
        """Busca artigos de lei relevantes"""
        where = {}
        if tipo:
            where['tipo'] = tipo

        results = self.collections['legislacao'].query(
            query_texts=[query],
            n_results=n_results,
            where=where if where else None
        )

        return self._format_results(results)

    def search_similar_cases(
        self,
        caso_descricao: str,
        cliente_id: Optional[int] = None,
        n_results: int = 5
    ) -> List[Dict]:
        """
        Busca casos similares nos documentos de clientes

        Args:
            caso_descricao: Descrição do caso atual
            cliente_id: Filtrar por cliente específico
            n_results: Número de resultados
        """
        where = {}
        if cliente_id:
            where['cliente_id'] = cliente_id

        results = self.collections['documentos_clientes'].query(
            query_texts=[caso_descricao],
            n_results=n_results,
            where=where if where else None
        )

        return self._format_results(results)

    def hybrid_search(
        self,
        query: str,
        collections: List[str] = None,
        n_results_per_collection: int = 3
    ) -> Dict[str, List[Dict]]:
        """
        Busca híbrida em múltiplas coleções

        Args:
            query: Consulta
            collections: Lista de coleções ou None para todas
            n_results_per_collection: Resultados por coleção

        Returns:
            Dict com resultados por coleção
        """
        if collections is None:
            collections = ['jurisprudencias', 'doutrinas', 'legislacao', 'templates']

        results = {}

        for coll_name in collections:
            if coll_name in self.collections:
                coll_results = self.collections[coll_name].query(
                    query_texts=[query],
                    n_results=n_results_per_collection
                )
                results[coll_name] = self._format_results(coll_results)

        return results

    # ==================== MÉTODOS AUXILIARES ====================

    def _split_text(
        self,
        text: str,
        chunk_size: int,
        overlap: int
    ) -> List[str]:
        """Divide texto em chunks com sobreposição"""
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)

        return chunks

    def _extract_text(self, arquivo_path: str) -> str:
        """Extrai texto de arquivo"""
        path = Path(arquivo_path)
        extension = path.suffix.lower()

        if extension == '.pdf':
            return self._extract_pdf(arquivo_path)
        elif extension in ['.docx', '.doc']:
            return self._extract_docx(arquivo_path)
        elif extension == '.txt':
            with open(arquivo_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            raise ValueError(f"Formato não suportado: {extension}")

    def _extract_pdf(self, pdf_path: str) -> str:
        """Extrai texto de PDF"""
        # Implementação simplificada
        # Na produção, usar pdfplumber ou PyMuPDF
        return "Texto extraído do PDF"

    def _extract_docx(self, docx_path: str) -> str:
        """Extrai texto de DOCX"""
        doc = Document(docx_path)
        return '\n\n'.join([p.text for p in doc.paragraphs])

    def _format_results(
        self,
        results: Dict,
        min_score: float = 0.0
    ) -> List[Dict]:
        """Formata resultados da busca"""
        formatted = []

        if not results['ids']:
            return formatted

        for i, doc_id in enumerate(results['ids'][0]):
            # ChromaDB retorna distance, converter para score
            distance = results['distances'][0][i]
            score = 1 - distance  # Quanto menor a distância, maior o score

            if score >= min_score:
                formatted.append({
                    'id': doc_id,
                    'texto': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'score': score
                })

        return formatted

    # ==================== ESTATÍSTICAS ====================

    def get_stats(self) -> Dict:
        """Retorna estatísticas do RAG"""
        stats = {}

        for name, collection in self.collections.items():
            stats[name] = collection.count()

        stats['total_documentos'] = sum(stats.values())

        return stats


# ==================== EXEMPLO DE USO ====================

def exemplo_rag_juridico():
    """Exemplo de uso do RAG jurídico"""

    rag = JuridicalRAG(persist_directory="./data/rag_juridico")

    # 1. Adicionar jurisprudência
    jurisp_texto = """
    AGRAVO DE INSTRUMENTO. AÇÃO DE INDENIZAÇÃO POR DANOS MORAIS...
    [Texto completo da jurisprudência]
    """

    rag.add_jurisprudencia(
        texto=jurisp_texto,
        metadata={
            'tribunal': 'STJ',
            'numero_processo': 'AIRG 12345-67.2024.1.00.0000',
            'relator': 'Min. Fulano de Tal',
            'data_julgamento': '2024-01-15',
            'area_direito': 'Civil',
            'palavras_chave': ['dano moral', 'internet', 'indenização'],
            'url': 'https://...'
        }
    )

    # 2. Adicionar doutrina
    doutrina_texto = """
    A responsabilidade civil por danos morais na internet...
    [Capítulo de livro ou artigo]
    """

    rag.add_doutrina(
        texto=doutrina_texto,
        metadata={
            'titulo': 'Responsabilidade Civil Digital',
            'autor': 'Carlos Roberto Gonçalves',
            'ano': 2023,
            'editora': 'Saraiva',
            'area_direito': 'Civil',
            'tipo': 'livro',
            'isbn': '978-...'
        }
    )

    # 3. Adicionar legislação (Código Civil art. 186-187)
    rag.add_legislacao(
        texto="",  # Pode ser vazio se usar 'artigos'
        metadata={
            'tipo': 'lei',
            'numero': '10.406',
            'ano': 2002,
            'titulo': 'Código Civil',
            'artigos': {
                '186': 'Aquele que, por ação ou omissão voluntária...',
                '187': 'Também comete ato ilícito o titular de um direito...',
                '927': 'Aquele que, por ato ilícito, causar dano a outrem...'
            }
        }
    )

    # 4. Buscar para fundamentar petição
    query = "Quero fundamentação sobre dano moral causado por ofensa na internet"

    # Busca híbrida em todas as fontes
    resultados = rag.hybrid_search(
        query=query,
        n_results_per_collection=3
    )

    print("=== JURISPRUDÊNCIAS ===")
    for jurisp in resultados.get('jurisprudencias', []):
        print(f"Score: {jurisp['score']:.2f}")
        print(f"Tribunal: {jurisp['metadata']['tribunal']}")
        print(f"Texto: {jurisp['texto'][:200]}...\n")

    print("\n=== DOUTRINAS ===")
    for dout in resultados.get('doutrinas', []):
        print(f"Score: {dout['score']:.2f}")
        print(f"Autor: {dout['metadata']['autor']}")
        print(f"Texto: {dout['texto'][:200]}...\n")

    print("\n=== LEGISLAÇÃO ===")
    for lei in resultados.get('legislacao', []):
        print(f"Score: {lei['score']:.2f}")
        print(f"Artigo: {lei['metadata'].get('artigo', 'N/A')}")
        print(f"Texto: {lei['texto'][:200]}...\n")

    # 5. Estatísticas
    stats = rag.get_stats()
    print(f"\n=== ESTATÍSTICAS ===")
    print(f"Total de documentos no RAG: {stats['total_documentos']}")
    for tipo, count in stats.items():
        if tipo != 'total_documentos':
            print(f"{tipo}: {count}")
