# ⚖️ LoboJur - Sistema Inteligente de Petições Jurídicas

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31.0-FF4B4B.svg)
![CrewAI](https://img.shields.io/badge/CrewAI-0.28.8-purple.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**Sistema de geração automática de petições jurídicas usando IA e agentes especializados**

[Documentação](#documentação) •
[Instalação](#instalação) •
[Uso](#como-usar) •
[Arquitetura](#arquitetura) •
[Contribuindo](#contribuindo)

</div>

---

## 📋 Sobre o Projeto

**LoboJur** é um sistema inteligente que utiliza agentes de IA especializados para auxiliar na elaboração de petições jurídicas de alta qualidade. O sistema emprega o framework **CrewAI** para orquestrar agentes especialistas em diferentes áreas do direito, buscando automaticamente jurisprudências e doutrinas relevantes para fundamentar as petições.

### ✨ Principais Funcionalidades

- 🤖 **Agentes Especialistas** em 6 áreas do direito (Civil, Criminal, Ambiental, Empresarial, Agrário, Tributário)
- 📚 **Busca Automática** de jurisprudências (STF, STJ, TRFs, TJs)
- 📖 **Pesquisa de Doutrinas** em bases acadêmicas
- 🌐 **Browser Use** para navegação autônoma e coleta de informações
- 📄 **Processamento de Documentos** (PDF, DOCX, TXT)
- 💾 **Banco de Dados** com cache de jurisprudências e doutrinas
- 🎨 **Interface Moderna** em Streamlit
- 📥 **Exportação** em PDF e DOCX

---

## 🏗️ Arquitetura

```
lobojur/
├── streamlit_app.py              # Interface principal
├── requirements.txt              # Dependências
├── config/
│   ├── config.py                # Configurações gerais
│   └── api_keys.py              # Gestão de API keys
├── agents/
│   ├── filtro_agent.py          # Agente classificador
│   ├── jurisprudencia_agent.py  # Busca jurisprudências
│   ├── doutrina_agent.py        # Busca doutrinas
│   └── especialistas/           # Agentes por área
│       ├── civil_agent.py
│       ├── criminal_agent.py
│       ├── ambiental_agent.py
│       ├── empresarial_agent.py
│       ├── agrario_agent.py
│       └── tributario_agent.py
├── database/
│   ├── models.py                # Modelos SQLAlchemy
│   ├── db_manager.py            # Gerenciador do BD
│   └── templates/               # Templates de petições
├── services/
│   ├── jurisprudencia_service.py
│   ├── doutrina_service.py
│   └── document_service.py
├── utils/
│   ├── document_processor.py    # Processamento de docs
│   └── pdf_generator.py         # Geração de PDFs
└── crews/
    └── petition_crew.py         # Orquestração CrewAI
```

---

## 🚀 Instalação

### Pré-requisitos

- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)
- Chave API da OpenAI

### Passo a Passo

1. **Clone o repositório**
   ```bash
   git clone https://github.com/seu-usuario/lobojur.git
   cd lobojur
   ```

2. **Crie um ambiente virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate     # Windows
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente**
   ```bash
   cp .env.example .env
   # Edite o arquivo .env e adicione sua chave da OpenAI
   ```

5. **Execute a aplicação**
   ```bash
   streamlit run streamlit_app.py
   ```

6. **Acesse no navegador**
   ```
   http://localhost:8501
   ```

---

## 💻 Como Usar

### 1. Selecione a Área do Direito

Na tela inicial, escolha uma das 6 áreas disponíveis:
- 🌳 Direito Ambiental
- ⚖️ Direito Civil
- 🔒 Direito Criminal
- 💼 Direito Empresarial
- 🌾 Direito Agrário
- 💰 Direito Tributário

### 2. Forneça Informações do Caso

Você pode:
- ✍️ **Descrever o caso** em texto livre
- 📄 **Enviar documentos** (PDF, DOCX, TXT)

### 3. Gere a Petição

Clique em "Gerar Petição" e aguarde enquanto:
1. O agente filtro classifica a área
2. O agente especialista analisa o caso
3. Jurisprudências relevantes são buscadas
4. Doutrinas são consultadas
5. A petição é gerada com fundamentação completa

### 4. Revise e Exporte

- 📄 Visualize a prévia da petição
- 📥 Baixe em PDF ou DOCX
- ✏️ Edite conforme necessário

---

## 🤖 Agentes Especializados

### Agente Filtro
Analisa o contexto e classifica a área jurídica correta do caso.

### Agentes Especialistas
Cada área possui um agente com conhecimento profundo:
- Legislação específica
- Jurisprudência predominante
- Doutrina relevante
- Melhores práticas

### Agentes de Busca
- **Jurisprudência**: Navega sites dos tribunais (STF, STJ, etc.)
- **Doutrina**: Pesquisa em Google Scholar, SciELO, repositórios

---

## 📊 Tecnologias Utilizadas

- **Framework Web**: Streamlit 1.31.0
- **IA e LLM**:
  - CrewAI 0.28.8
  - LangChain 0.1.13
  - OpenAI GPT-4
  - Browser Use 0.1.4
- **Banco de Dados**: SQLAlchemy + SQLite
- **Processamento de Documentos**:
  - PyPDF2
  - python-docx
  - pdfplumber
- **Geração de PDFs**: ReportLab, WeasyPrint
- **Vector Store**: ChromaDB, FAISS

---

## 🗄️ Banco de Dados

O sistema utiliza SQLite com as seguintes tabelas principais:

- `areas_direito`: Áreas jurídicas disponíveis
- `templates_peticao`: Templates por área
- `peticoes_geradas`: Histórico de petições
- `jurisprudencias_cache`: Cache de jurisprudências
- `doutrinas_cache`: Cache de doutrinas
- `documentos_usuario`: Documentos enviados

---

## 🔧 Configuração Avançada

### Variáveis de Ambiente (.env)

```env
# API Keys
OPENAI_API_KEY=sua_chave_aqui

# Modelo LLM
LLM_MODEL=gpt-4-turbo-preview
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4000

# Browser Use
BROWSER_HEADLESS=True
BROWSER_TIMEOUT=30

# Limites de Busca
MAX_JURISPRUDENCIAS=5
MAX_DOUTRINAS=3
```

---

## 📝 Roadmap

- [x] Interface Streamlit moderna
- [x] Banco de dados SQLite
- [x] Agentes especialistas básicos
- [x] Sistema de templates
- [ ] Integração completa com Browser Use
- [ ] Busca real em tribunais
- [ ] Sistema de memória RAG
- [ ] Geração de PDFs formatados
- [ ] Autenticação de usuários
- [ ] API REST
- [ ] Modo multi-tenant

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 👥 Autores

- **Equipe LoboJur** - Desenvolvimento inicial

---

## 📞 Suporte

Para suporte, envie um email para suporte@lobojur.com ou abra uma issue no GitHub.

---

## 🙏 Agradecimentos

- [Streamlit](https://streamlit.io/) - Framework web
- [CrewAI](https://www.crewai.io/) - Orquestração de agentes
- [OpenAI](https://openai.com/) - Modelos de linguagem
- [LangChain](https://langchain.com/) - Framework LLM

---

<div align="center">

**Feito com ❤️ e ⚖️ para a comunidade jurídica**

[⬆ Voltar ao topo](#️-lobojur---sistema-inteligente-de-petições-jurídicas)

</div>
