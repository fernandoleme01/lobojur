# 🚀 Guia Rápido - LoboLab

## Início Rápido em 5 Minutos

### 1. Instalação

```bash
# Clone o repositório
git clone https://github.com/fernandoleme01/lobojur.git
cd lobojur

# Instale as dependências
pip install -r requirements.txt
```

### 2. Configure as API Keys

Você precisa de 3 API keys (gratuitas para teste):

1. **Claude API** → https://console.anthropic.com/
2. **Gemini API** → https://makersuite.google.com/app/apikey
3. **Perplexity API** → https://www.perplexity.ai/settings/api

### 3. Execute o Sistema

```bash
streamlit run app.py
```

O navegador abrirá automaticamente em `http://localhost:8501`

### 4. Use o Sistema

1. **Na sidebar**, insira suas 3 API keys
2. **Faça upload** de um contrato em PDF
3. **(Opcional)** Configure opções de análise
4. Clique em **"🚀 Iniciar Análise Completa"**
5. Aguarde alguns minutos (3-5 min em média)
6. **Download** do laudo gerado!

## 🎯 O Que o Sistema Faz?

### Workflow Automático:

```
📄 PDF Upload
    ↓
🔍 OCR & Extração de Texto
    ↓
🧠 Análise com Gemini (estrutura e dados)
    ↓
🌐 Pesquisas com Perplexity (legislação/jurisprudência)
    ↓
🤖 Análise Multi-Agente com Claude:
    ├── Analista de Contratos
    ├── Advogado Especialista
    ├── Analista Financeiro
    ├── Assessor de Riscos
    └── Perito Técnico
    ↓
✍️ Geração do Laudo Final (Claude)
    ↓
📥 Download (TXT/DOCX/PDF)
```

## 📋 Estrutura do Laudo Gerado

O laudo técnico inclui:

1. **Identificação** - Partes, perito, objeto
2. **Preâmbulo** - Objetivo, metodologia, quesitos
3. **Análise Técnica** - Cláusulas, obrigações, estrutura
4. **Aspectos Jurídicos** - Conformidade, base legal, riscos
5. **Aspectos Financeiros** - Valores, projeções, garantias
6. **Avaliação de Riscos** - Matriz de riscos e mitigações
7. **Conclusão** - Síntese, parecer e recomendações

## 💡 Dicas

### Para Melhores Resultados:

- ✅ Use PDFs com boa qualidade
- ✅ Ative "Pesquisas Web" para análise mais completa
- ✅ Preencha informações adicionais quando disponível
- ✅ Use "Análise Completa" para laudos técnicos
- ✅ Revise o laudo antes de uso formal

### Custos de API:

- **Claude**: ~$0.50-2.00 por análise
- **Gemini**: ~$0.10-0.50 por análise
- **Perplexity**: ~$0.20-0.80 por análise

**Total médio**: $0.80-3.30 por contrato completo

## 🔧 Opções Avançadas

### Uso Programático

```python
from src.llm.orchestrator import ReportOrchestrator, APIKeys
from src.ocr.pdf_extractor import PDFExtractor
import asyncio

# Setup
api_keys = APIKeys(
    claude_api_key="sk-ant-...",
    gemini_api_key="AIza...",
    perplexity_api_key="pplx-..."
)

# Extrair PDF
extractor = PDFExtractor(use_ocr=True)
data = extractor.extract_text("contrato.pdf")

# Analisar
orchestrator = ReportOrchestrator(api_keys)
result = asyncio.run(
    orchestrator.generate_complete_report(
        contract_text=data['text'],
        enable_web_research=True
    )
)

# Laudo
print(result['final_report'])
```

### Análise Rápida (Sem Pesquisas)

```python
result = asyncio.run(
    orchestrator.quick_analysis(contract_text)
)
```

### Apenas Pesquisas

```python
result = asyncio.run(
    orchestrator.research_only(
        topics=["Lei 8078/1990", "Cláusulas abusivas CDC"]
    )
)
```

## 🆘 Problemas Comuns

### "Erro ao extrair texto"
- Verifique se o PDF não está protegido/criptografado
- Ative OCR para PDFs escaneados

### "API Error"
- Verifique se as API keys estão corretas
- Verifique se tem créditos nas APIs
- Tente novamente (retry automático em falhas de rede)

### "Análise incompleta"
- Pode ser limite de contexto da LLM
- Tente dividir contratos muito longos (>100 páginas)

### "OCR não funciona"
- Instale Tesseract: `sudo apt-get install tesseract-ocr`
- Verifique idioma: `tesseract-ocr-por`

## 📞 Suporte

- **Issues**: https://github.com/fernandoleme01/lobojur/issues
- **Documentação Completa**: Veja `README.md`

## 🎓 Exemplos de Uso

### Casos Recomendados:
- ✅ Contratos comerciais
- ✅ Contratos de prestação de serviços
- ✅ Contratos de locação
- ✅ Contratos trabalhistas
- ✅ Perícias judiciais
- ✅ Due diligence
- ✅ Compliance contratual

### Limitações:
- ⚠️ Contratos muito técnicos podem precisar revisão especializada
- ⚠️ Laudos são assistidos por IA - sempre revise
- ⚠️ Não substitui análise de advogado em casos complexos
- ⚠️ Dados são enviados para APIs externas (privacidade)

---

**Desenvolvido por LoboLab IA Consulting** 🐺

Bom uso! 🚀
