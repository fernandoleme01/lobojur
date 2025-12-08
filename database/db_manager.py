"""
Gerenciador do banco de dados
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
from pathlib import Path
from .models import Base, AreaDireito, TemplatePeticao, PeticaoGerada
from .models import JurisprudenciaCache, DoutrinaCache, DocumentoUsuario, HistoricoBusca


class DatabaseManager:
    """Gerenciador centralizado do banco de dados"""

    def __init__(self, db_path: str = "data/lobojur.db"):
        """
        Inicializa o gerenciador do banco de dados

        Args:
            db_path: Caminho para o arquivo do banco de dados SQLite
        """
        # Garantir que o diretório existe
        db_file = Path(db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)

        # Criar engine
        self.engine = create_engine(
            f'sqlite:///{db_path}',
            echo=False,
            connect_args={'check_same_thread': False}
        )

        # Criar session factory
        self.SessionFactory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.SessionFactory)

        # Criar todas as tabelas
        self.create_tables()

        # Inicializar dados padrão
        self.initialize_default_data()

    def create_tables(self):
        """Cria todas as tabelas no banco de dados"""
        Base.metadata.create_all(self.engine)

    @contextmanager
    def session_scope(self):
        """
        Context manager para sessões do banco de dados
        Uso: with db.session_scope() as session: ...
        """
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def initialize_default_data(self):
        """Inicializa áreas do direito padrão"""
        with self.session_scope() as session:
            # Verificar se já existem áreas
            if session.query(AreaDireito).count() > 0:
                return

            # Criar áreas padrão
            areas = [
                {
                    'nome': 'Direito Ambiental',
                    'descricao': 'Proteção ao meio ambiente, licenciamento ambiental, crimes ambientais',
                    'icone': '🌳',
                    'cor': '#228B22'
                },
                {
                    'nome': 'Direito Civil',
                    'descricao': 'Contratos, responsabilidade civil, família, sucessões, propriedade',
                    'icone': '⚖️',
                    'cor': '#1E3A8A'
                },
                {
                    'nome': 'Direito Criminal',
                    'descricao': 'Crimes, processo penal, execução penal, habeas corpus',
                    'icone': '🔒',
                    'cor': '#B91C1C'
                },
                {
                    'nome': 'Direito Empresarial',
                    'descricao': 'Sociedades, contratos empresariais, recuperação judicial, falência',
                    'icone': '💼',
                    'cor': '#7C3AED'
                },
                {
                    'nome': 'Direito Agrário',
                    'descricao': 'Reforma agrária, propriedade rural, contratos agrários, meio ambiente rural',
                    'icone': '🌾',
                    'cor': '#CA8A04'
                },
                {
                    'nome': 'Direito Tributário',
                    'descricao': 'Impostos, tributos, execução fiscal, planejamento tributário',
                    'icone': '💰',
                    'cor': '#DC2626'
                }
            ]

            for area_data in areas:
                area = AreaDireito(**area_data)
                session.add(area)

    def get_areas_direito(self):
        """Retorna todas as áreas do direito"""
        with self.session_scope() as session:
            return session.query(AreaDireito).all()

    def get_area_by_nome(self, nome: str):
        """Retorna área do direito pelo nome"""
        with self.session_scope() as session:
            return session.query(AreaDireito).filter_by(nome=nome).first()

    def salvar_peticao(self, peticao_data: dict):
        """Salva uma petição gerada"""
        with self.session_scope() as session:
            peticao = PeticaoGerada(**peticao_data)
            session.add(peticao)
            session.flush()
            return peticao.id

    def salvar_jurisprudencia(self, jurisp_data: dict):
        """Salva jurisprudência no cache"""
        with self.session_scope() as session:
            # Verificar se já existe
            existing = session.query(JurisprudenciaCache).filter_by(
                tribunal=jurisp_data.get('tribunal'),
                numero_processo=jurisp_data.get('numero_processo')
            ).first()

            if existing:
                existing.total_acessos += 1
                return existing.id
            else:
                jurisp = JurisprudenciaCache(**jurisp_data)
                session.add(jurisp)
                session.flush()
                return jurisp.id

    def salvar_doutrina(self, doutrina_data: dict):
        """Salva doutrina no cache"""
        with self.session_scope() as session:
            # Verificar se já existe
            existing = session.query(DoutrinaCache).filter_by(
                titulo=doutrina_data.get('titulo'),
                autor=doutrina_data.get('autor')
            ).first()

            if existing:
                existing.total_acessos += 1
                return existing.id
            else:
                doutrina = DoutrinaCache(**doutrina_data)
                session.add(doutrina)
                session.flush()
                return doutrina.id

    def buscar_jurisprudencias(self, area_direito: str = None, palavras_chave: list = None, limit: int = 10):
        """Busca jurisprudências no cache"""
        with self.session_scope() as session:
            query = session.query(JurisprudenciaCache)

            if area_direito:
                query = query.filter_by(area_direito=area_direito)

            if palavras_chave:
                # Busca por palavras-chave (simplificado)
                for palavra in palavras_chave:
                    query = query.filter(
                        JurisprudenciaCache.ementa.contains(palavra) |
                        JurisprudenciaCache.decisao.contains(palavra)
                    )

            return query.order_by(JurisprudenciaCache.relevancia_score.desc()).limit(limit).all()

    def buscar_doutrinas(self, area_direito: str = None, palavras_chave: list = None, limit: int = 10):
        """Busca doutrinas no cache"""
        with self.session_scope() as session:
            query = session.query(DoutrinaCache)

            if area_direito:
                query = query.filter_by(area_direito=area_direito)

            if palavras_chave:
                for palavra in palavras_chave:
                    query = query.filter(
                        DoutrinaCache.titulo.contains(palavra) |
                        DoutrinaCache.resumo.contains(palavra)
                    )

            return query.order_by(DoutrinaCache.relevancia_score.desc()).limit(limit).all()

    def get_peticoes_recentes(self, limit: int = 10):
        """Retorna as petições mais recentes"""
        with self.session_scope() as session:
            return session.query(PeticaoGerada).order_by(
                PeticaoGerada.created_at.desc()
            ).limit(limit).all()


# Instância global
db = DatabaseManager()
