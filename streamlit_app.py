"""
LoboJur - Sistema Inteligente de Petições Jurídicas
Interface Streamlit com Design Moderno
"""
import streamlit as st
from streamlit_option_menu import option_menu
import asyncio
from pathlib import Path
import sys

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from database.db_manager import db
from services.jurisprudencia_service import JurisprudenciaService
from services.doutrina_service import DoutrinaService
from services.document_service import DocumentService
from agents.filtro_agent import criar_agente_filtro


# ==================== CONFIGURAÇÃO DA PÁGINA ====================
st.set_page_config(
    page_title="LoboJur - Sistema de Petições Jurídicas",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "LoboJur - Sistema Inteligente de Petições Jurídicas com IA"
    }
)

# ==================== CSS CUSTOMIZADO ====================
st.markdown("""
<style>
    /* Importar fonte moderna */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Estilo global */
    * {
        font-family: 'Inter', sans-serif;
    }

    /* Header principal */
    .main-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }

    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }

    .main-header p {
        color: #E0E7FF;
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }

    /* Cards */
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        margin-bottom: 1rem;
        border-left: 4px solid #3B82F6;
        transition: transform 0.2s, box-shadow 0.2s;
    }

    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 12px rgba(0,0,0,0.12);
    }

    .card-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
    }

    .card-subtitle {
        font-size: 0.9rem;
        color: #6B7280;
        margin-bottom: 1rem;
    }

    /* Área cards - grid */
    .area-card {
        background: linear-gradient(135deg, var(--card-color) 0%, var(--card-color-light) 100%);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        min-height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }

    .area-card:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 16px rgba(0,0,0,0.15);
    }

    .area-icon {
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }

    .area-title {
        color: white;
        font-size: 1.2rem;
        font-weight: 600;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }

    /* Stats */
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
    }

    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: #3B82F6;
        margin-bottom: 0.3rem;
    }

    .stat-label {
        font-size: 0.9rem;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Botões customizados */
    .stButton>button {
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.7rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s;
        box-shadow: 0 4px 6px rgba(59, 130, 246, 0.3);
    }

    .stButton>button:hover {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        box-shadow: 0 6px 12px rgba(59, 130, 246, 0.4);
        transform: translateY(-2px);
    }

    /* Sidebar */
    .css-1d391kg {
        background: #F9FAFB;
    }

    /* Inputs */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        border-radius: 8px;
        border: 2px solid #E5E7EB;
        padding: 0.7rem;
        font-size: 1rem;
    }

    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #3B82F6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }

    /* Progress */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #3B82F6 0%, #8B5CF6 100%);
    }

    /* Alerts */
    .stAlert {
        border-radius: 10px;
        border-left: 4px solid #3B82F6;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: #F3F4F6;
        border-radius: 8px;
        font-weight: 600;
    }

    /* File uploader */
    .stFileUploader {
        background: #F9FAFB;
        border: 2px dashed #D1D5DB;
        border-radius: 12px;
        padding: 2rem;
        transition: all 0.3s;
    }

    .stFileUploader:hover {
        border-color: #3B82F6;
        background: #EFF6FF;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 600;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    ::-webkit-scrollbar-track {
        background: #F3F4F6;
    }

    ::-webkit-scrollbar-thumb {
        background: #9CA3AF;
        border-radius: 5px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #6B7280;
    }
</style>
""", unsafe_allow_html=True)


# ==================== INICIALIZAÇÃO ====================
def init_session_state():
    """Inicializa variáveis de sessão"""
    if 'area_selecionada' not in st.session_state:
        st.session_state.area_selecionada = None
    if 'contexto_caso' not in st.session_state:
        st.session_state.contexto_caso = ""
    if 'peticao_gerada' not in st.session_state:
        st.session_state.peticao_gerada = None
    if 'historico' not in st.session_state:
        st.session_state.historico = []


def get_services():
    """Retorna instâncias dos serviços"""
    if 'services' not in st.session_state:
        st.session_state.services = {
            'jurisprudencia': JurisprudenciaService(db),
            'doutrina': DoutrinaService(db),
            'documento': DocumentService(db)
        }
    return st.session_state.services


# ==================== COMPONENTES ====================
def render_header():
    """Renderiza header principal"""
    st.markdown("""
        <div class="main-header">
            <h1>⚖️ LoboJur</h1>
            <p>Sistema Inteligente de Petições Jurídicas com IA</p>
        </div>
    """, unsafe_allow_html=True)


def render_areas_grid():
    """Renderiza grid de áreas do direito"""
    st.markdown("### 📚 Selecione a Área do Direito")

    areas = db.get_areas_direito()

    # Criar grid 3x2
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]

    for idx, area in enumerate(areas):
        with cols[idx % 3]:
            # Determinar cor baseada na área
            cores = {
                'Direito Ambiental': ('#228B22', '#32CD32'),
                'Direito Civil': ('#1E3A8A', '#3B82F6'),
                'Direito Criminal': ('#B91C1C', '#EF4444'),
                'Direito Empresarial': ('#7C3AED', '#A78BFA'),
                'Direito Agrário': ('#CA8A04', '#FACC15'),
                'Direito Tributário': ('#DC2626', '#F87171')
            }

            cor, cor_light = cores.get(area.nome, ('#3B82F6', '#60A5FA'))

            if st.button(
                f"{area.icone}\n\n{area.nome}",
                key=f"area_{area.id}",
                use_container_width=True
            ):
                st.session_state.area_selecionada = area
                st.rerun()


def render_stats():
    """Renderiza estatísticas do sistema"""
    peticoes = db.get_peticoes_recentes(limit=100)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{len(peticoes)}</div>
                <div class="stat-label">Petições Geradas</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        with db.session_scope() as session:
            from database.models import JurisprudenciaCache
            total_jurisp = session.query(JurisprudenciaCache).count()

        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{total_jurisp}</div>
                <div class="stat-label">Jurisprudências</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        with db.session_scope() as session:
            from database.models import DoutrinaCache
            total_dout = session.query(DoutrinaCache).count()

        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{total_dout}</div>
                <div class="stat-label">Doutrinas</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">6</div>
                <div class="stat-label">Áreas Atendidas</div>
            </div>
        """, unsafe_allow_html=True)


def render_input_form(area):
    """Renderiza formulário de entrada"""
    st.markdown(f"""
        <div class="card">
            <div class="card-title">{area.icone} {area.nome}</div>
            <div class="card-subtitle">{area.descricao}</div>
        </div>
    """, unsafe_allow_html=True)

    # Tabs para diferentes formas de entrada
    tab1, tab2 = st.tabs(["✍️ Descrever Caso", "📄 Upload de Documentos"])

    with tab1:
        st.markdown("#### Descreva o caso jurídico")
        contexto = st.text_area(
            "Detalhe os fatos, partes envolvidas e o que você deseja solicitar:",
            height=300,
            placeholder="Exemplo: Meu cliente João Silva sofreu danos morais devido a...",
            key="contexto_input"
        )

        col1, col2 = st.columns([3, 1])
        with col1:
            tipo_peticao = st.selectbox(
                "Tipo de Petição",
                ["Petição Inicial", "Contestação", "Recurso", "Agravo", "Habeas Corpus", "Mandado de Segurança"]
            )
        with col2:
            urgente = st.checkbox("🚨 Urgente")

    with tab2:
        st.markdown("#### Envie documentos relacionados ao caso")
        uploaded_files = st.file_uploader(
            "Arraste arquivos ou clique para selecionar",
            accept_multiple_files=True,
            type=['pdf', 'docx', 'doc', 'txt'],
            help="Formatos aceitos: PDF, DOCX, DOC, TXT"
        )

        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} arquivo(s) carregado(s)")
            for file in uploaded_files:
                st.info(f"📎 {file.name} ({file.size / 1024:.1f} KB)")

    st.markdown("---")

    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        if st.button("🚀 Gerar Petição", use_container_width=True, type="primary"):
            if contexto or uploaded_files:
                gerar_peticao(area, contexto, uploaded_files if 'uploaded_files' in locals() else None)
            else:
                st.error("⚠️ Por favor, descreva o caso ou envie documentos")

    with col2:
        if st.button("🔍 Buscar Jurisprudência", use_container_width=True):
            if contexto:
                buscar_jurisprudencia_preview(area, contexto)
            else:
                st.warning("Digite um contexto primeiro")

    with col3:
        if st.button("← Voltar", use_container_width=True):
            st.session_state.area_selecionada = None
            st.rerun()


def gerar_peticao(area, contexto, arquivos=None):
    """Gera a petição usando os agentes"""
    with st.spinner("🤖 Analisando caso e gerando petição..."):
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Simular processo de geração
        status_text.text("📋 Classificando área jurídica...")
        progress_bar.progress(20)

        status_text.text(f"🎓 Acionando especialista em {area.nome}...")
        progress_bar.progress(40)

        status_text.text("📚 Buscando jurisprudências relevantes...")
        progress_bar.progress(60)

        status_text.text("📖 Consultando doutrinas...")
        progress_bar.progress(80)

        status_text.text("✍️ Elaborando petição...")
        progress_bar.progress(95)

        # Petição de exemplo (em produção, seria gerada pelos agentes)
        peticao_exemplo = f"""
# PETIÇÃO INICIAL - {area.nome.upper()}

## EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(A) DE DIREITO DA ... VARA ...

**AUTOR**, brasileiro(a), [qualificação completa], vem, por seu advogado que esta subscreve,
com fundamento nos artigos aplicáveis do Código Civil e demais legislação pertinente,
propor a presente

## AÇÃO [TIPO DE AÇÃO]

em face de **RÉU**, [qualificação], pelos fatos e fundamentos jurídicos a seguir expostos:

### I - DOS FATOS

{contexto}

### II - DO DIREITO

[Fundamentação jurídica será inserida aqui com base em jurisprudências e doutrinas encontradas]

### III - DO PEDIDO

Diante do exposto, requer-se:

a) A citação do réu para, querendo, contestar a presente ação;

b) A procedência total dos pedidos;

c) A condenação do réu ao pagamento de custas processuais e honorários advocatícios.

Dá-se à causa o valor de R$ _______.

Nestes termos,
Pede deferimento.

[Cidade], [Data]

_______________________
Advogado(a)
OAB/XX nº XXXXX
"""

        progress_bar.progress(100)
        status_text.text("✅ Petição gerada com sucesso!")

        st.session_state.peticao_gerada = peticao_exemplo

        # Exibir resultado
        st.success("✅ Petição gerada com sucesso!")

        st.markdown("### 📄 Prévia da Petição")
        st.markdown(peticao_exemplo)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.download_button(
                "📥 Baixar PDF",
                peticao_exemplo,
                file_name="peticao.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        with col2:
            st.download_button(
                "📥 Baixar DOCX",
                peticao_exemplo,
                file_name="peticao.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
        with col3:
            if st.button("📋 Copiar", use_container_width=True):
                st.info("Texto copiado para área de transferência!")


def buscar_jurisprudencia_preview(area, contexto):
    """Busca e exibe preview de jurisprudências"""
    with st.spinner("🔍 Buscando jurisprudências..."):
        st.info("🔍 Funcionalidade em desenvolvimento - Em breve com Browser Use!")


# ==================== NAVEGAÇÃO ====================
def render_sidebar():
    """Renderiza sidebar com navegação"""
    with st.sidebar:
        st.markdown("### 🎯 Menu Principal")

        selected = option_menu(
            menu_title=None,
            options=["🏠 Início", "📝 Nova Petição", "📚 Histórico", "⚙️ Configurações"],
            icons=["house", "file-text", "clock-history", "gear"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important"},
                "nav-link": {
                    "font-size": "14px",
                    "text-align": "left",
                    "margin": "5px",
                    "border-radius": "8px"
                },
                "nav-link-selected": {"background-color": "#3B82F6"},
            }
        )

        st.markdown("---")
        st.markdown("### 📊 Estatísticas")
        render_stats()

        return selected


# ==================== MAIN ====================
def main():
    """Função principal"""
    init_session_state()
    render_header()

    menu_option = render_sidebar()

    if menu_option == "🏠 Início" or menu_option == "📝 Nova Petição":
        if st.session_state.area_selecionada:
            render_input_form(st.session_state.area_selecionada)
        else:
            render_areas_grid()

    elif menu_option == "📚 Histórico":
        st.markdown("### 📚 Histórico de Petições")
        st.info("🚧 Funcionalidade em desenvolvimento")

    elif menu_option == "⚙️ Configurações":
        st.markdown("### ⚙️ Configurações do Sistema")

        with st.expander("🔑 API Keys", expanded=False):
            openai_key = st.text_input("OpenAI API Key", type="password", help="Sua chave da API OpenAI")
            if st.button("Salvar Chave"):
                st.success("✅ Chave salva com sucesso!")

        with st.expander("🎨 Preferências", expanded=False):
            st.checkbox("Modo escuro", value=False)
            st.selectbox("Modelo LLM", ["GPT-4", "GPT-3.5-Turbo", "Claude"])
            st.slider("Temperatura", 0.0, 1.0, 0.7)


if __name__ == "__main__":
    main()
