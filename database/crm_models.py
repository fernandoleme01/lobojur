"""
Modelos de CRM - Gestão de Clientes
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .models import Base


class TipoPessoa(enum.Enum):
    """Tipo de pessoa"""
    FISICA = "fisica"
    JURIDICA = "juridica"


class StatusCliente(enum.Enum):
    """Status do cliente"""
    ATIVO = "ativo"
    INATIVO = "inativo"
    PROSPECTO = "prospecto"
    BLOQUEADO = "bloqueado"


class Cliente(Base):
    """Cliente do escritório"""
    __tablename__ = 'clientes'

    id = Column(Integer, primary_key=True)

    # Dados básicos
    nome = Column(String(200), nullable=False, index=True)
    tipo_pessoa = Column(SQLEnum(TipoPessoa), default=TipoPessoa.FISICA)
    cpf = Column(String(11), unique=True, index=True, nullable=True)
    cnpj = Column(String(14), unique=True, index=True, nullable=True)
    rg = Column(String(20), nullable=True)

    # Contato
    email = Column(String(200), index=True)
    telefone = Column(String(20))
    celular = Column(String(20))
    whatsapp = Column(String(20), index=True)

    # Endereço
    cep = Column(String(8))
    logradouro = Column(String(200))
    numero = Column(String(20))
    complemento = Column(String(100))
    bairro = Column(String(100))
    cidade = Column(String(100))
    estado = Column(String(2))

    # Dados profissionais (se PJ)
    razao_social = Column(String(200))
    nome_fantasia = Column(String(200))
    inscricao_estadual = Column(String(20))
    inscricao_municipal = Column(String(20))

    # Status
    status = Column(SQLEnum(StatusCliente), default=StatusCliente.PROSPECTO)
    data_cadastro = Column(DateTime, default=datetime.now)
    data_primeira_consulta = Column(DateTime, nullable=True)
    origem = Column(String(100))  # indicação, google, whatsapp, etc

    # Informações adicionais
    observacoes = Column(Text)
    tags = Column(Text)  # JSON array de tags

    # Integração Asaas
    asaas_customer_id = Column(String(100), unique=True, index=True)

    # Relacionamentos
    processos = relationship('ProcessoCliente', back_populates='cliente')
    documentos = relationship('DocumentoCliente', back_populates='cliente')

    # Metadata
    criado_em = Column(DateTime, default=datetime.now)
    atualizado_em = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    criado_por_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    def __repr__(self):
        return f"<Cliente(id={self.id}, nome='{self.nome}')>"

    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'tipo_pessoa': self.tipo_pessoa.value if self.tipo_pessoa else None,
            'cpf': self.cpf,
            'cnpj': self.cnpj,
            'email': self.email,
            'telefone': self.telefone,
            'celular': self.celular,
            'whatsapp': self.whatsapp,
            'endereco': {
                'cep': self.cep,
                'logradouro': self.logradouro,
                'numero': self.numero,
                'complemento': self.complemento,
                'bairro': self.bairro,
                'cidade': self.cidade,
                'estado': self.estado
            },
            'status': self.status.value if self.status else None,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None,
            'observacoes': self.observacoes,
            'asaas_customer_id': self.asaas_customer_id,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None
        }


class ProcessoCliente(Base):
    """Processos vinculados a clientes"""
    __tablename__ = 'processos_clientes'

    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)

    numero_processo = Column(String(100), unique=True, index=True, nullable=False)
    tribunal = Column(String(50))
    vara = Column(String(100))

    tipo_acao = Column(String(100))
    area_direito_id = Column(Integer, ForeignKey('areas_direito.id'))

    polo = Column(String(20))  # 'ativo', 'passivo'
    valor_causa = Column(String(50))

    data_distribuicao = Column(DateTime)
    data_encerramento = Column(DateTime, nullable=True)
    status = Column(String(50))  # 'em_andamento', 'suspenso', 'encerrado'

    observacoes = Column(Text)

    # Relacionamentos
    cliente = relationship('Cliente', back_populates='processos')

    criado_em = Column(DateTime, default=datetime.now)
    atualizado_em = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<ProcessoCliente(numero='{self.numero_processo}')>"


class DocumentoCliente(Base):
    """Documentos dos clientes"""
    __tablename__ = 'documentos_clientes'

    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)

    tipo_documento = Column(String(50))  # rg, cpf, contrato, procuracao, etc
    nome_arquivo = Column(String(200), nullable=False)
    caminho_arquivo = Column(String(500), nullable=False)
    tamanho_bytes = Column(Integer)
    mime_type = Column(String(100))

    descricao = Column(Text)

    # Relacionamentos
    cliente = relationship('Cliente', back_populates='documentos')

    criado_em = Column(DateTime, default=datetime.now)
    criado_por_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    def __repr__(self):
        return f"<DocumentoCliente(tipo='{self.tipo_documento}', arquivo='{self.nome_arquivo}')>"

    def to_dict(self):
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'tipo_documento': self.tipo_documento,
            'nome_arquivo': self.nome_arquivo,
            'tamanho_bytes': self.tamanho_bytes,
            'mime_type': self.mime_type,
            'descricao': self.descricao,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None
        }


# ==================== FUNÇÕES AUXILIARES ====================

def criar_cliente_completo(db_session, dados: dict, asaas_client=None) -> Cliente:
    """
    Cria cliente completo com validação e integração Asaas

    Args:
        db_session: Sessão do banco
        dados: Dados do cliente
        asaas_client: Cliente Asaas (opcional)

    Returns:
        Cliente criado
    """
    # Criar cliente
    cliente = Cliente(**dados)
    db_session.add(cliente)
    db_session.flush()  # Pega o ID

    # Criar no Asaas se fornecido
    if asaas_client and dados.get('email'):
        asaas_data = asaas_client.criar_cliente(
            nome=dados['nome'],
            cpf_cnpj=dados.get('cpf') or dados.get('cnpj'),
            email=dados['email'],
            telefone=dados.get('celular') or dados.get('telefone'),
            endereco={
                'cep': dados.get('cep'),
                'logradouro': dados.get('logradouro'),
                'numero': dados.get('numero'),
                'complemento': dados.get('complemento'),
                'bairro': dados.get('bairro'),
                'cidade': dados.get('cidade'),
                'estado': dados.get('estado')
            }
        )
        cliente.asaas_customer_id = asaas_data['id']

    db_session.commit()
    return cliente


def buscar_clientes(db_session, filtros: dict = None, limit: int = 50, offset: int = 0):
    """
    Busca clientes com filtros

    Args:
        db_session: Sessão do banco
        filtros: Filtros (nome, cpf, status, etc)
        limit: Limite de resultados
        offset: Offset para paginação

    Returns:
        Lista de clientes
    """
    query = db_session.query(Cliente)

    if filtros:
        if filtros.get('nome'):
            query = query.filter(Cliente.nome.ilike(f"%{filtros['nome']}%"))

        if filtros.get('cpf'):
            query = query.filter(Cliente.cpf == filtros['cpf'])

        if filtros.get('cnpj'):
            query = query.filter(Cliente.cnpj == filtros['cnpj'])

        if filtros.get('whatsapp'):
            query = query.filter(Cliente.whatsapp == filtros['whatsapp'])

        if filtros.get('status'):
            query = query.filter(Cliente.status == StatusCliente[filtros['status'].upper()])

    return query.order_by(Cliente.nome).limit(limit).offset(offset).all()


def buscar_cliente_por_id(db_session, cliente_id: int):
    """Busca cliente por ID"""
    return db_session.query(Cliente).filter(Cliente.id == cliente_id).first()


def buscar_cliente_por_documento(db_session, cpf: str = None, cnpj: str = None):
    """Busca cliente por CPF ou CNPJ"""
    if cpf:
        return db_session.query(Cliente).filter(Cliente.cpf == cpf).first()
    elif cnpj:
        return db_session.query(Cliente).filter(Cliente.cnpj == cnpj).first()
    return None


def atualizar_cliente(db_session, cliente_id: int, dados: dict):
    """Atualiza dados do cliente"""
    cliente = buscar_cliente_por_id(db_session, cliente_id)

    if not cliente:
        raise ValueError(f"Cliente {cliente_id} não encontrado")

    for key, value in dados.items():
        if hasattr(cliente, key):
            setattr(cliente, key, value)

    cliente.atualizado_em = datetime.now()
    db_session.commit()

    return cliente


def adicionar_processo_cliente(db_session, cliente_id: int, processo_data: dict):
    """Adiciona processo ao cliente"""
    processo = ProcessoCliente(
        cliente_id=cliente_id,
        **processo_data
    )
    db_session.add(processo)
    db_session.commit()
    return processo
