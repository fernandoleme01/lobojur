"""
LoboJur - Sistema de Análise de Contratos e Geração de Laudos Técnicos

Sistema avançado que combina:
- OCR para extração de PDFs
- Perplexity AI para pesquisas em tempo real
- Gemini para análise profunda de documentos
- Claude para escrita de laudos técnicos
"""

import streamlit as st
import asyncio
from pathlib import Path
import sys

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ocr.pdf_extractor import PDFExtractor
from llm.orchestrator import ReportOrchestrator, APIKeys
from templates.document_generator import DocumentGenerator

# Configuração da página
st.set_page_config(
    page_title="LoboJur - Análise de Contratos",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 1rem 1rem 1rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
    }
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 1rem;
    }
    .logo-img {
        max-width: 400px;
        height: auto;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
    }
    .sub-header {
        font-size: 1.3rem;
        color: #4a5568;
        text-align: center;
        margin-top: 1rem;
        font-weight: 500;
        letter-spacing: 0.5px;
    }
    .tagline {
        font-size: 1rem;
        color: #718096;
        text-align: center;
        margin-top: 0.5rem;
        font-style: italic;
    }
    .info-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .info-box strong {
        color: #ffd700;
    }
    .success-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: none;
    }
    .stButton>button {
        background: linear-gradient(135deg, #FF8C42 0%, #FF6B35 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(255, 107, 53, 0.3);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2d3748 0%, #1a202c 100%);
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        color: #FF8C42;
        font-weight: bold;
    }
    .element-container:has(.main-header) {
        margin-top: -3rem;
    }
</style>
""", unsafe_allow_html=True)

# Header com Logo
st.markdown("""
<div class="main-header">
    <div class="logo-container">
        <img src="https://i.imgur.com/placeholder.png" alt="LoboLab Logo" class="logo-img"
             onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
        <div style="display:none;">
            <h1 style="color: #4a5568; margin: 0;">
                <span style="color: #4a5568;">LOBO</span><span style="color: #FF8C42;">LAB</span>
            </h1>
            <p style="color: #718096; font-size: 0.9rem; margin: 0;">IA CONSULTING</p>
        </div>
    </div>
    <div class="sub-header">Sistema Inteligente de Análise de Contratos</div>
    <div class="tagline">Powered by Multi-AI Technology: Claude • Gemini • Perplexity</div>
</div>
""", unsafe_allow_html=True)

# Sidebar - Configurações
with st.sidebar:
    # Logo na sidebar também
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0; margin-bottom: 1.5rem;">
        <h2 style="margin: 0; color: #4a5568;">
            <span style="color: #4a5568;">LOBO</span><span style="color: #FF8C42;">LAB</span>
        </h2>
        <p style="color: #718096; font-size: 0.8rem; margin: 0;">IA CONSULTING</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.header("⚙️ Configurações")

    st.subheader("🔑 API Keys")

    claude_api_key = st.text_input(
        "Claude API Key",
        type="password",
        help="Chave API do Anthropic Claude"
    )

    gemini_api_key = st.text_input(
        "Gemini API Key",
        type="password",
        help="Chave API do Google Gemini"
    )

    perplexity_api_key = st.text_input(
        "Perplexity API Key",
        type="password",
        help="Chave API do Perplexity AI"
    )

    st.divider()

    st.subheader("🎯 Opções de Análise")

    enable_web_research = st.checkbox(
        "Habilitar Pesquisas Web (Perplexity)",
        value=True,
        help="Buscar legislação e jurisprudência atualizadas"
    )

    use_ocr = st.checkbox(
        "Usar OCR em PDFs sem texto",
        value=True,
        help="Aplicar OCR em páginas sem texto extraível"
    )

    analysis_depth = st.select_slider(
        "Profundidade da Análise",
        options=["Rápida", "Padrão", "Completa"],
        value="Completa"
    )

    st.divider()

    st.subheader("📄 Formato de Saída")

    output_format = st.selectbox(
        "Formato do Laudo",
        ["TXT", "DOCX", "PDF"],
        index=1
    )

# Tabs principais
tab1, tab2, tab3, tab4 = st.tabs([
    "📂 Upload e Análise",
    "📊 Resultados",
    "🔍 Pesquisas",
    "ℹ️ Sobre"
])

# Tab 1: Upload e Análise
with tab1:
    st.header("📂 Upload de Contrato")

    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "Selecione o arquivo do contrato (PDF)",
            type=["pdf"],
            help="Faça upload do contrato em PDF para análise"
        )

    with col2:
        st.markdown("""
        <div class="info-box">
        <strong>📋 Formatos Aceitos</strong><br>
        ✓ PDF com texto<br>
        ✓ PDF escaneado (OCR)<br>
        ✓ Multipáginas<br>
        <br>
        <strong>⚡ Processamento</strong><br>
        ✓ Extração automática<br>
        ✓ OCR inteligente<br>
        ✓ Análise Multi-IA<br>
        ✓ Pesquisas em tempo real
        </div>
        """, unsafe_allow_html=True)

    if uploaded_file:
        st.success(f"✅ Arquivo carregado: {uploaded_file.name}")

        # Metadados adicionais
        with st.expander("➕ Informações Adicionais (Opcional)"):
            col1, col2 = st.columns(2)

            with col1:
                contract_type = st.text_input("Tipo de Contrato")
                contract_date = st.date_input("Data do Contrato")

            with col2:
                contract_value = st.text_input("Valor do Contrato")
                contract_parties = st.text_area("Partes Envolvidas")

            research_topics = st.text_area(
                "Tópicos Específicos para Pesquisa (um por linha)",
                help="Tópicos adicionais para pesquisar além da análise automática"
            )

        # Botão de análise
        st.divider()

        if st.button("🚀 Iniciar Análise Completa", type="primary", use_container_width=True):
            # Validar API keys
            if not all([claude_api_key, gemini_api_key, perplexity_api_key]):
                st.error("❌ Por favor, configure todas as API keys na barra lateral.")
            else:
                with st.spinner("🔄 Processando contrato..."):
                    try:
                        # 1. Extrair texto do PDF
                        st.info("📄 Extraindo texto do PDF...")
                        pdf_extractor = PDFExtractor(use_ocr=use_ocr)

                        pdf_bytes = uploaded_file.read()
                        extracted_data = pdf_extractor.extract_text(pdf_bytes)

                        contract_text = extracted_data['text']
                        num_pages = extracted_data['num_pages']

                        st.success(f"✅ Texto extraído: {num_pages} páginas, {len(contract_text)} caracteres")

                        # Salvar no session state
                        st.session_state['extracted_text'] = contract_text
                        st.session_state['pdf_metadata'] = extracted_data['metadata']
                        st.session_state['num_pages'] = num_pages

                        # 2. Inicializar orquestrador
                        st.info("🤖 Inicializando análise multi-IA...")

                        api_keys = APIKeys(
                            claude_api_key=claude_api_key,
                            gemini_api_key=gemini_api_key,
                            perplexity_api_key=perplexity_api_key
                        )

                        orchestrator = ReportOrchestrator(api_keys)

                        # 3. Preparar metadados
                        metadata = {
                            "tipo_contrato": contract_type,
                            "data_contrato": str(contract_date) if contract_date else None,
                            "valor_contrato": contract_value,
                            "partes": contract_parties,
                            "num_paginas": num_pages
                        }

                        # 4. Análise
                        topics = [t.strip() for t in research_topics.split('\n') if t.strip()] if research_topics else None

                        st.info("🔍 Executando análise completa (isso pode levar alguns minutos)...")

                        # Executar análise assíncrona
                        async def run_analysis():
                            return await orchestrator.generate_complete_report(
                                contract_text=contract_text,
                                contract_metadata=metadata,
                                enable_web_research=enable_web_research,
                                research_topics=topics
                            )

                        # Criar event loop se necessário
                        try:
                            loop = asyncio.get_event_loop()
                        except RuntimeError:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)

                        analysis_result = loop.run_until_complete(run_analysis())

                        # Salvar resultados
                        st.session_state['analysis_result'] = analysis_result
                        st.session_state['analysis_complete'] = True

                        # 5. Gerar documento
                        st.info("📝 Gerando laudo técnico...")

                        doc_generator = DocumentGenerator()

                        # Preparar dados para o documento
                        report_data = {
                            "parecer_tecnico": analysis_result['final_report'],
                            "analise_clausulas": analysis_result['contract_analysis'].contract_summary,
                            "riscos_juridicos": analysis_result['contract_analysis'].legal_risks,
                            "sintese_analise": analysis_result['gemini_analysis'].get('analysis', ''),
                            **metadata
                        }

                        output_path = doc_generator.generate_full_report(
                            analysis_data=report_data,
                            format=output_format.lower()
                        )

                        st.session_state['output_file'] = output_path

                        st.success("✅ Análise concluída com sucesso!")

                        # Download
                        with open(output_path, 'rb') as f:
                            st.download_button(
                                label=f"📥 Download Laudo ({output_format})",
                                data=f.read(),
                                file_name=output_path.name,
                                mime="application/octet-stream",
                                type="primary",
                                use_container_width=True
                            )

                    except Exception as e:
                        st.error(f"❌ Erro durante a análise: {str(e)}")
                        st.exception(e)

# Tab 2: Resultados
with tab2:
    st.header("📊 Resultados da Análise")

    if 'analysis_complete' in st.session_state and st.session_state['analysis_complete']:
        result = st.session_state['analysis_result']

        # Métricas
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Páginas Analisadas", st.session_state.get('num_pages', 0))

        with col2:
            apis_used = len(result['metadata']['apis_used'])
            st.metric("APIs Utilizadas", apis_used)

        with col3:
            web_results = len(result['web_research'].get('results', []))
            st.metric("Pesquisas Web", web_results)

        with col4:
            st.metric("Status", "✅ Completo")

        st.divider()

        # Laudo final
        with st.expander("📄 Laudo Técnico Completo", expanded=True):
            st.markdown(result['final_report'])

        # Análises detalhadas
        col1, col2 = st.columns(2)

        with col1:
            with st.expander("🔍 Análise Gemini"):
                st.markdown(result['gemini_analysis'].get('analysis', ''))

            with st.expander("💰 Análise Financeira"):
                st.markdown(result['contract_analysis'].financial_analysis)

        with col2:
            with st.expander("⚖️ Análise Jurídica"):
                st.markdown(result['contract_analysis'].legal_risks)

            with st.expander("⚠️ Recomendações"):
                st.markdown(result['contract_analysis'].recommendations)

        # Dados estruturados
        with st.expander("📋 Dados Extraídos"):
            st.json(result['extracted_data'])

    else:
        st.info("👈 Faça upload e análise de um contrato na aba 'Upload e Análise'")

# Tab 3: Pesquisas
with tab3:
    st.header("🔍 Pesquisas Web Realizadas")

    if 'analysis_result' in st.session_state:
        research = st.session_state['analysis_result']['web_research']

        if research:
            st.subheader(f"Tópicos Pesquisados: {len(research.get('topics_researched', []))}")

            for topic in research.get('topics_researched', []):
                st.markdown(f"• {topic}")

            st.divider()

            for idx, result in enumerate(research.get('results', []), 1):
                with st.expander(f"Pesquisa {idx}"):
                    st.markdown("**Resposta:**")
                    st.write(result.get('answer', ''))

                    citations = result.get('citations', [])
                    if citations:
                        st.markdown("**Fontes:**")
                        for cite in citations:
                            st.markdown(f"• {cite}")
        else:
            st.info("Pesquisas web não foram realizadas nesta análise.")
    else:
        st.info("👈 Execute uma análise primeiro")

# Tab 4: Sobre
with tab4:
    # Logo centralizada
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1 style="margin: 0; font-size: 3rem;">
            <span style="color: #4a5568;">LOBO</span><span style="color: #FF8C42;">LAB</span>
        </h1>
        <p style="color: #718096; font-size: 1.2rem; margin-top: 0.5rem;">IA CONSULTING</p>
        <p style="color: #a0aec0; font-size: 1rem; margin-top: 1rem;">Sistema Inteligente de Análise de Contratos Jurídicos</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 10px; color: white;">
            <h2 style="color: white; margin: 0;">🤖</h2>
            <h3 style="color: white;">Multi-IA</h3>
            <p style="color: #e0e0e0; font-size: 0.9rem;">3 Engines de IA trabalhando em conjunto</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #FF8C42 0%, #FF6B35 100%);
                    border-radius: 10px; color: white;">
            <h2 style="color: white; margin: 0;">⚖️</h2>
            <h3 style="color: white;">Jurídico</h3>
            <p style="color: #f0f0f0; font-size: 0.9rem;">Especializado em contratos brasileiros</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 10px; color: white;">
            <h2 style="color: white; margin: 0;">📊</h2>
            <h3 style="color: white;">Laudos</h3>
            <p style="color: #e0e0e0; font-size: 0.9rem;">Laudos técnicos profissionais</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    ### 🎯 Objetivo

    O **LoboLab** oferece um sistema avançado de análise de contratos jurídicos e geração de laudos técnicos,
    utilizando múltiplas inteligências artificiais especializadas.

    ### 🤖 Tecnologias

    - **Perplexity AI**: Pesquisas em tempo real de legislação e jurisprudência
    - **Google Gemini**: Análise profunda de documentos e extração de dados
    - **Claude (Anthropic)**: Escrita de laudos técnicos e análise multi-agente
    - **PyMuPDF + Tesseract**: Extração de texto e OCR

    ### 🔄 Workflow

    1. **Extração**: OCR e extração de texto do PDF
    2. **Análise Inicial**: Gemini analisa estrutura e extrai dados
    3. **Pesquisas**: Perplexity busca informações atualizadas
    4. **Análise Detalhada**: Claude multi-agente analisa todos os aspectos
    5. **Geração**: Claude escreve o laudo técnico final

    ### ✨ Funcionalidades

    - ✅ Análise automática de contratos em PDF
    - ✅ OCR para documentos escaneados
    - ✅ Pesquisa de legislação e jurisprudência em tempo real
    - ✅ Análise multi-agente especializada
    - ✅ Geração de laudos técnicos profissionais
    - ✅ Exportação em TXT, DOCX e PDF
    - ✅ Identificação de riscos jurídicos e financeiros
    - ✅ Conformidade legal automatizada

    ### 📚 Requisitos

    - Python 3.9+
    - API Keys: Claude, Gemini, Perplexity
    - Tesseract OCR (opcional, para OCR)

    ### 👨‍💻 Desenvolvido por

    Sistema desenvolvido para análise jurídica automatizada com IA.

    ---

    **Versão**: 1.0.0
    """)

    st.info("💡 **Dica**: Configure todas as API keys na barra lateral antes de começar.")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    ⚖️ LoboJur - Sistema Inteligente de Análise de Contratos | 2024
</div>
""", unsafe_allow_html=True)
