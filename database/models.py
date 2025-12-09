"""
Modelos do banco de dados para o sistema de petições jurídicas
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class AreaDireito(Base):
    """Áreas do direito disponíveis no sistema"""
    __tablename__ = 'areas_direito'

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), unique=True, nullable=False)
    descricao = Column(Text)
    icone = Column(String(50))  # emoji ou nome do ícone
    cor = Column(String(20))  # código hexadecimal da cor
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    templates = relationship("TemplatePeticao", back_populates="area")
    peticoes = relationship("PeticaoGerada", back_populates="area")


class TemplatePeticao(Base):
    """Templates de petições por área do direito"""
    __tablename__ = 'templates_peticao'

    id = Column(Integer, primary_key=True)
    area_id = Column(Integer, ForeignKey('areas_direito.id'), nullable=False)
    nome = Column(String(200), nullable=False)
    descricao = Column(Text)
    tipo_peticao = Column(String(100))  # inicial, recurso, contestação, etc
    conteudo = Column(Text, nullable=False)  # Template com placeholders
    variaveis = Column(JSON)  # Lista de variáveis esperadas
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    area = relationship("AreaDireito", back_populates="templates")
    peticoes = relationship("PeticaoGerada", back_populates="template")


class PeticaoGerada(Base):
    """Petições geradas pelo sistema"""
    __tablename__ = 'peticoes_geradas'

    id = Column(Integer, primary_key=True)
    area_id = Column(Integer, ForeignKey('areas_direito.id'), nullable=False)
    template_id = Column(Integer, ForeignKey('templates_peticao.id'))
    titulo = Column(String(300), nullable=False)
    conteudo = Column(Text, nullable=False)
    contexto_usuario = Column(Text)  # Entrada original do usuário
    documentos_anexados = Column(JSON)  # Lista de documentos anexados
    jurisprudencias_utilizadas = Column(JSON)  # Lista de jurisprudências
    doutrinas_utilizadas = Column(JSON)  # Lista de doutrinas
    status = Column(String(50), default='gerada')  # gerada, revisada, exportada
    formato_exportacao = Column(String(20))  # pdf, docx
    caminho_arquivo = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    area = relationship("AreaDireito", back_populates="peticoes")
    template = relationship("TemplatePeticao", back_populates="peticoes")


class JurisprudenciaCache(Base):
    """Cache de jurisprudências buscadas"""
    __tablename__ = 'jurisprudencias_cache'

    id = Column(Integer, primary_key=True)
    tribunal = Column(String(50), nullable=False)  # STF, STJ, TRF1, etc
    numero_processo = Column(String(100))
    ementa = Column(Text)
    decisao = Column(Text)
    relator = Column(String(200))
    data_julgamento = Column(DateTime)
    palavras_chave = Column(JSON)
    area_direito = Column(String(100))
    relevancia_score = Column(Float)
    url_fonte = Column(String(500))
    conteudo_completo = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    ultimo_acesso = Column(DateTime, default=datetime.utcnow)
    total_acessos = Column(Integer, default=0)


class DoutrinaCache(Base):
    """Cache de doutrinas e artigos jurídicos"""
    __tablename__ = 'doutrinas_cache'

    id = Column(Integer, primary_key=True)
    titulo = Column(String(500), nullable=False)
    autor = Column(String(300))
    ano = Column(Integer)
    fonte = Column(String(200))  # Livro, artigo, revista, etc
    editora = Column(String(200))
    resumo = Column(Text)
    citacao_abnt = Column(Text)
    palavras_chave = Column(JSON)
    area_direito = Column(String(100))
    relevancia_score = Column(Float)
    url_fonte = Column(String(500))
    conteudo_relevante = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    ultimo_acesso = Column(DateTime, default=datetime.utcnow)
    total_acessos = Column(Integer, default=0)


class DocumentoUsuario(Base):
    """Documentos enviados pelos usuários"""
    __tablename__ = 'documentos_usuario'

    id = Column(Integer, primary_key=True)
    nome_arquivo = Column(String(300), nullable=False)
    tipo_arquivo = Column(String(50))  # pdf, docx, txt, jpg, png
    tamanho_bytes = Column(Integer)
    caminho_arquivo = Column(String(500), nullable=False)
    texto_extraido = Column(Text)
    metadados = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class HistoricoBusca(Base):
    """Histórico de buscas realizadas"""
    __tablename__ = 'historico_buscas'

    id = Column(Integer, primary_key=True)
    tipo_busca = Column(String(50), nullable=False)  # jurisprudencia, doutrina
    query = Column(Text, nullable=False)
    area_direito = Column(String(100))
    filtros = Column(JSON)
    resultados_encontrados = Column(Integer)
    tempo_resposta_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
