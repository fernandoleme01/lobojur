# ⚖️ LoboJur - Sistema Inteligente de Análise de Contratos

Sistema avançado de análise de contratos jurídicos e geração de laudos técnicos utilizando múltiplas inteligências artificiais especializadas.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.9+-green)
![License](https://img.shields.io/badge/license-Apache%202.0-orange)

## 🎯 Visão Geral

LoboJur é uma solução completa para análise automatizada de contratos legais, combinando:

- **Extração Inteligente**: OCR avançado para PDFs (texto e imagens)
- **Pesquisas em Tempo Real**: Perplexity AI para legislação e jurisprudência atualizadas
- **Análise Profunda**: Google Gemini para análise estrutural de documentos
- **Geração de Laudos**: Claude AI com sistema multi-agente especializado

## ✨ Funcionalidades

### 📄 Processamento de Documentos
- ✅ Extração automática de texto de PDFs
- ✅ OCR para documentos escaneados (Tesseract)
- ✅ Suporte a PDFs multipáginas
- ✅ Extração de metadados e tabelas

### 🔍 Análise Inteligente
- ✅ Sistema multi-agente especializado:
  - Analista de Contratos (estrutura e cláusulas)
  - Advogado Especialista (conformidade legal)
  - Analista Financeiro (aspectos econômicos)
  - Assessor de Riscos (identificação e mitigação)
  - Perito Técnico (elaboração de laudos)

### 🌐 Pesquisas em Tempo Real
- ✅ Busca automática de legislação aplicável
- ✅ Pesquisa de jurisprudência recente (STJ, STF, TST)
- ✅ Validação de informações em fontes oficiais
- ✅ Verificação de atualizações legislativas

### 📊 Geração de Laudos
- ✅ Laudos técnicos periciais completos
- ✅ Resumos executivos
- ✅ Avaliação detalhada de riscos
- ✅ Análises comparativas entre contratos
- ✅ Exportação em múltiplos formatos (TXT, DOCX, PDF)

## 🚀 Instalação

### Pré-requisitos

- Python 3.9 ou superior
- pip (gerenciador de pacotes Python)
- Tesseract OCR (opcional, para OCR)

### Instalação do Tesseract (Opcional)

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-por
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Download em: https://github.com/UB-Mannheim/tesseract/wiki

### Instalação do Projeto

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/lobojur.git
cd lobojur
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente (opcional):
```bash
cp .env.example .env
# Edite o arquivo .env com suas API keys
```

## 🔑 Configuração de API Keys

O sistema requer API keys das seguintes plataformas:

1. **Anthropic Claude**: https://console.anthropic.com/
2. **Google Gemini**: https://makersuite.google.com/app/apikey
3. **Perplexity AI**: https://www.perplexity.ai/settings/api

### Opção 1: Interface Web (Recomendado)
Configure as API keys diretamente na interface Streamlit (sidebar).

### Opção 2: Arquivo .env
```bash
CLAUDE_API_KEY=sk-ant-...
GEMINI_API_KEY=AIza...
PERPLEXITY_API_KEY=pplx-...
```

## 💻 Uso

### Interface Web (Streamlit)

1. Execute o aplicativo:
```bash
streamlit run app.py
```

2. Acesse no navegador: http://localhost:8501

3. Configure as API keys na barra lateral

4. Faça upload do contrato em PDF

5. Clique em "Iniciar Análise Completa"

### Uso Programático

```python
import asyncio
from src.ocr.pdf_extractor import PDFExtractor
from src.llm.orchestrator import ReportOrchestrator, APIKeys

# Configurar API keys
api_keys = APIKeys(
    claude_api_key="sua-chave-claude",
    gemini_api_key="sua-chave-gemini",
    perplexity_api_key="sua-chave-perplexity"
)

# Extrair texto do PDF
extractor = PDFExtractor(use_ocr=True)
extracted = extractor.extract_text("contrato.pdf")
contract_text = extracted['text']

# Inicializar orquestrador
orchestrator = ReportOrchestrator(api_keys)

# Executar análise
async def analyze():
    result = await orchestrator.generate_complete_report(
        contract_text=contract_text,
        enable_web_research=True
    )
    return result

# Executar
result = asyncio.run(analyze())

# Acessar laudo
laudo = result['final_report']
print(laudo)
```

## 🏗️ Arquitetura

```
lobojur/
├── src/
│   ├── ocr/                    # Extração de texto e OCR
│   │   ├── pdf_extractor.py
│   │   └── __init__.py
│   ├── llm/                    # Integrações com LLMs
│   │   ├── claude_analyzer.py
│   │   ├── gemini_analyzer.py
│   │   ├── perplexity_researcher.py
│   │   ├── contract_analyzer.py
│   │   ├── orchestrator.py
│   │   └── __init__.py
│   ├── scraping/               # Web scraping
│   │   ├── web_researcher.py
│   │   ├── legal_scraper.py
│   │   └── __init__.py
│   ├── templates/              # Templates de laudos
│   │   ├── report_templates.py
│   │   ├── document_generator.py
│   │   └── __init__.py
│   └── utils/                  # Utilitários
├── data/
│   ├── pdfs/                   # PDFs de entrada
│   ├── templates/              # Templates customizados
│   └── output/                 # Laudos gerados
├── tests/                      # Testes
├── app.py                      # Interface Streamlit
├── requirements.txt
└── README.md
```

## 🔄 Workflow de Análise

1. **Extração (OCR)**
   - Upload do PDF
   - Extração de texto com PyMuPDF
   - OCR automático se necessário

2. **Análise Inicial (Gemini)**
   - Análise estrutural do contrato
   - Extração de dados estruturados
   - Identificação de partes e cláusulas

3. **Pesquisas (Perplexity)**
   - Busca de legislação aplicável
   - Pesquisa de jurisprudência recente
   - Validação de informações

4. **Análise Multi-Agente (Claude)**
   - Agente 1: Análise estrutural
   - Agente 2: Análise das partes
   - Agente 3: Análise financeira
   - Agente 4: Análise jurídica e riscos
   - Agente 5: Avaliação consolidada
   - Agente 6: Elaboração do laudo

5. **Geração Final (Claude)**
   - Síntese de todas as análises
   - Escrita do laudo técnico
   - Formatação e exportação

## 📋 Estrutura do Laudo

Os laudos gerados seguem estrutura técnica profissional:

1. **Identificação**
   - Partes envolvidas
   - Perito responsável
   - Objeto da perícia

2. **Preâmbulo**
   - Objetivo e metodologia
   - Documentos analisados
   - Quesitos

3. **Análise Técnica**
   - Caracterização do contrato
   - Análise de cláusulas
   - Obrigações das partes

4. **Aspectos Jurídicos**
   - Conformidade legal
   - Base legal aplicável
   - Riscos identificados

5. **Aspectos Financeiros**
   - Valores e condições
   - Projeções
   - Garantias

6. **Avaliação de Riscos**
   - Matriz de riscos
   - Análise detalhada
   - Mitigações propostas

7. **Conclusão**
   - Síntese da análise
   - Parecer técnico
   - Recomendações

## 🛠️ Desenvolvimento

### Executar em Modo Debug
```bash
streamlit run app.py --logger.level=debug
```

### Testes
```bash
pytest tests/
```

### Estrutura de Código
- Código modular e bem documentado
- Type hints em Python
- Logging estruturado
- Tratamento de erros robusto

## 📊 Tecnologias Utilizadas

### Core
- **Python 3.9+**: Linguagem principal
- **Streamlit**: Interface web
- **AsyncIO**: Processamento assíncrono

### IA/LLM
- **Anthropic Claude**: Análise e escrita de laudos
- **Google Gemini**: Análise de documentos
- **Perplexity AI**: Pesquisas em tempo real

### Processamento de Documentos
- **PyMuPDF (fitz)**: Manipulação de PDFs
- **Tesseract**: OCR
- **pdf2image**: Conversão PDF para imagem
- **Pillow**: Processamento de imagens

### Geração de Documentos
- **python-docx**: Geração de DOCX
- **ReportLab**: Geração de PDFs
- **Jinja2**: Templates

### Utilities
- **pandas**: Manipulação de dados
- **pydantic**: Validação de dados
- **tenacity**: Retry logic
- **python-dotenv**: Gerenciamento de variáveis

## ⚠️ Limitações e Considerações

- **Custos de API**: O uso de múltiplas APIs tem custos associados
- **Rate Limits**: Respeite os limites de taxa de cada API
- **Privacidade**: Dados são enviados para APIs externas
- **Precisão OCR**: Qualidade depende do PDF original
- **Contexto**: Laudos são assistidos por IA, revisão humana é recomendada

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Add: MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Apache License 2.0 - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 📞 Suporte

Para questões e suporte:
- Abra uma issue no GitHub
- Consulte a documentação
- Entre em contato com a equipe de desenvolvimento

## 🎓 Casos de Uso

- ✅ Análise de contratos comerciais
- ✅ Revisão de contratos de trabalho
- ✅ Perícias judiciais
- ✅ Due diligence jurídica
- ✅ Compliance contratual
- ✅ Gestão de riscos contratuais
- ✅ Auditoria de contratos

## 🔮 Roadmap

- [ ] Integração com mais tribunais brasileiros
- [ ] Análise de contratos internacionais
- [ ] Dashboard de analytics
- [ ] API REST
- [ ] Integração com sistemas jurídicos
- [ ] Treinamento de modelos customizados
- [ ] Suporte a mais formatos de documento
- [ ] Banco de dados de cláusulas

---

**Desenvolvido com ⚖️ para análise jurídica automatizada**

*Última atualização: 2024*
