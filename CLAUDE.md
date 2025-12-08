# CLAUDE.md - Guia para Assistentes de IA

Este documento fornece um guia completo sobre a estrutura, convenções e fluxos de trabalho do projeto **LoboJur** para assistentes de IA que trabalharão neste repositório.

---

## 📁 Estrutura do Repositório

```
lobojur/
├── streamlit_app.py              # 🎨 Interface principal Streamlit
├── requirements.txt              # 📦 Dependências Python
├── .env.example                  # 🔑 Template de variáveis de ambiente
├── README.md                     # 📖 Documentação do usuário
├── CLAUDE.md                     # 🤖 Este arquivo - guia para IA
├── LICENSE                       # ⚖️ Licença MIT
│
├── config/                       # ⚙️ Configurações
│   └── config.py                # Constantes e configurações globais
│
├── agents/                       # 🤖 Agentes CrewAI
│   ├── __init__.py
│   ├── filtro_agent.py          # Agente classificador de área jurídica
│   ├── jurisprudencia_agent.py  # Agente de busca de jurisprudências (futuro)
│   ├── doutrina_agent.py        # Agente de busca de doutrinas (futuro)
│   └── especialistas/           # Agentes especialistas por área
│       ├── __init__.py
│       ├── civil_agent.py       # ⚖️ Direito Civil
│       ├── criminal_agent.py    # 🔒 Direito Criminal (futuro)
│       ├── ambiental_agent.py   # 🌳 Direito Ambiental (futuro)
│       ├── empresarial_agent.py # 💼 Direito Empresarial (futuro)
│       ├── agrario_agent.py     # 🌾 Direito Agrário (futuro)
│       └── tributario_agent.py  # 💰 Direito Tributário (futuro)
│
├── database/                     # 💾 Banco de Dados
│   ├── __init__.py
│   ├── models.py                # Modelos SQLAlchemy
│   ├── db_manager.py            # Gerenciador centralizado do BD
│   └── templates/               # Templates de petições
│       ├── ambiental/
│       ├── civil/
│       │   └── modelo_danos_morais.md
│       ├── criminal/
│       ├── empresarial/
│       ├── agrario/
│       └── tributario/
│
├── services/                     # 🔧 Serviços
│   ├── __init__.py
│   ├── jurisprudencia_service.py  # Busca jurisprudências
│   ├── doutrina_service.py        # Busca doutrinas
│   └── document_service.py        # Processamento de documentos
│
├── utils/                        # 🛠️ Utilitários
│   ├── __init__.py
│   ├── document_processor.py    # Extração de texto (futuro)
│   └── pdf_generator.py         # Geração de PDFs (futuro)
│
├── crews/                        # 🎭 Orquestração CrewAI
│   ├── __init__.py
│   └── petition_crew.py         # Crew principal (futuro)
│
└── data/                         # 📊 Dados
    ├── cache/                   # Cache de buscas
    ├── exports/                 # Petições exportadas
    └── lobojur.db              # Banco de dados SQLite (gerado)
```

---

## 🎯 Propósito do Projeto

**LoboJur** é um sistema de geração automática de petições jurídicas que utiliza:

1. **Agentes IA Especializados** (CrewAI) - Um agente para cada área do direito
2. **Busca Automática** - Jurisprudências e doutrinas via Browser Use
3. **Templates Dinâmicos** - Modelos de petições preenchidos automaticamente
4. **Cache Inteligente** - Armazenamento de jurisprudências/doutrinas consultadas
5. **Interface Moderna** - Streamlit com design profissional

---

## 🏗️ Arquitetura e Componentes

### 1. Interface (streamlit_app.py)

**Responsabilidade**: Interface web do usuário

**Componentes Principais**:
- `render_header()` - Header com gradiente azul
- `render_areas_grid()` - Grid 3x2 de áreas do direito
- `render_input_form()` - Formulário de entrada (texto ou upload)
- `gerar_peticao()` - Orquestra geração da petição
- `render_sidebar()` - Menu lateral com navegação

**Estilo**: CSS inline com design moderno (gradientes, cards, sombras)

### 2. Banco de Dados (database/)

**ORM**: SQLAlchemy
**Banco**: SQLite (desenvolvimento) - facilmente migrável para PostgreSQL

**Tabelas**:
- `areas_direito` - 6 áreas: Ambiental, Civil, Criminal, Empresarial, Agrário, Tributário
- `templates_peticao` - Templates por área com placeholders
- `peticoes_geradas` - Histórico de petições criadas
- `jurisprudencias_cache` - Cache de jurisprudências (STF, STJ, etc.)
- `doutrinas_cache` - Cache de doutrinas e artigos
- `documentos_usuario` - Documentos enviados pelos usuários
- `historico_buscas` - Log de buscas realizadas

**Gerenciador**: `DatabaseManager` em `db_manager.py`
- Context manager para sessões
- Métodos helper para queries comuns
- Inicialização automática de dados padrão

### 3. Agentes CrewAI (agents/)

#### Agente Filtro (`filtro_agent.py`)
**Papel**: Classificar a área do direito do caso

**Método Principal**: `classificar_area(contexto: str) -> Dict`

**Retorno**:
```python
{
    'area': 'Direito Civil',
    'confianca': 0.85,
    'scores': {'Direito Civil': 5, 'Direito Criminal': 1}
}
```

#### Agentes Especialistas (`especialistas/`)

Cada agente especialista possui:

**Estrutura**:
```python
class AgenteDireito[Area]:
    def __init__(self, llm, jurisprudencia_service, doutrina_service)
    async def analisar_caso(self, contexto: str) -> Dict
    async def buscar_fundamentacao(self, analise: Dict) -> Dict
    def _identificar_tipo_acao(self, contexto: str) -> str
    def _identificar_partes(self, contexto: str) -> Dict
    def _extrair_fatos(self, contexto: str) -> List[str]
    def _identificar_fundamentos(self, contexto: str) -> List[str]
    def _sugerir_pedidos(self, contexto: str) -> List[str]
```

**Exemplo Completo**: `civil_agent.py`

**Conhecimento Especializado**:
- Legislação específica da área
- Jurisprudência predominante
- Doutrinadores renomados
- Tipos de ação comuns
- Fundamentação típica

### 4. Serviços (services/)

#### JurisprudenciaService
**Fontes**: STF, STJ, TST, TRFs, TJs, JusBrasil

**Método Principal**:
```python
async def buscar_jurisprudencias(
    query: str,
    area_direito: str,
    tribunais: List[str] = None,
    max_resultados: int = 5
) -> List[Dict]
```

**Fluxo**:
1. Busca no cache local primeiro
2. Se insuficiente, busca online (Browser Use)
3. Salva novos resultados no cache
4. Retorna ordenado por relevância

#### DoutrinaService
**Fontes**: Google Scholar, SciELO, Repositórios Universitários

**Método Principal**:
```python
async def buscar_doutrinas(
    query: str,
    area_direito: str,
    fontes: List[str] = None,
    max_resultados: int = 3
) -> List[Dict]
```

#### DocumentService
**Formatos Suportados**: PDF, DOCX, DOC, TXT

**Métodos**:
- `processar_documento(arquivo_path: str) -> Dict`
- `salvar_upload(arquivo_bytes: bytes, nome_arquivo: str) -> str`

---

## 🔄 Fluxo de Trabalho Principal

### Geração de Petição (End-to-End)

```
1. Usuário seleciona área do direito
   └─> Streamlit: render_areas_grid()

2. Usuário fornece contexto (texto ou documentos)
   └─> Streamlit: render_input_form()

3. Clica em "Gerar Petição"
   └─> Streamlit: gerar_peticao()
       │
       ├─> [20%] Agente Filtro classifica área
       │   └─> filtro_agent.classificar_area()
       │
       ├─> [40%] Agente Especialista analisa caso
       │   └─> especialista.analisar_caso()
       │
       ├─> [60%] Busca jurisprudências
       │   └─> jurisprudencia_service.buscar_jurisprudencias()
       │       ├─> Consulta cache local
       │       └─> Browser Use busca online (se necessário)
       │
       ├─> [80%] Busca doutrinas
       │   └─> doutrina_service.buscar_doutrinas()
       │       ├─> Consulta cache local
       │       └─> Browser Use busca online (se necessário)
       │
       └─> [95%] Especialista gera petição
           └─> Template + Fundamentação → Petição Final

4. Exibe resultado com opções de download
   └─> PDF, DOCX, Cópia
```

---

## 📝 Convenções de Código

### Python Style Guide

- **PEP 8** estritamente seguido
- **Type hints** em todas as funções públicas
- **Docstrings** formato Google Style

```python
def funcao_exemplo(parametro: str, opcional: int = 10) -> Dict:
    """
    Descrição breve da função.

    Args:
        parametro: Descrição do parâmetro
        opcional: Descrição do parâmetro opcional (padrão: 10)

    Returns:
        Dicionário com resultado

    Raises:
        ValueError: Quando parametro é inválido
    """
    pass
```

### Nomeação

- **Variáveis/Funções**: `snake_case`
- **Classes**: `PascalCase`
- **Constantes**: `UPPER_SNAKE_CASE`
- **Privado**: `_prefixo_underscore`

### Imports

Ordem:
1. Biblioteca padrão
2. Bibliotecas terceiros
3. Módulos locais

```python
# Padrão
import os
from pathlib import Path

# Terceiros
import streamlit as st
from crewai import Agent

# Locais
from database.db_manager import db
from services.jurisprudencia_service import JurisprudenciaService
```

---

## 🎨 UI/UX Guidelines

### Design System

**Cores**:
```css
Primária: #3B82F6 (azul)
Primária Escura: #1E3A8A
Secundária: #8B5CF6 (roxo)
Sucesso: #10B981
Erro: #EF4444
Warning: #F59E0B
Cinza Claro: #F3F4F6
Texto: #1F2937
```

**Componentes**:
- Cards com `border-radius: 12px` e sombra suave
- Botões com gradiente e hover animado
- Inputs com borda destacada no focus
- Progress bar com gradiente azul→roxo

### Ícones por Área

- 🌳 Direito Ambiental
- ⚖️ Direito Civil
- 🔒 Direito Criminal
- 💼 Direito Empresarial
- 🌾 Direito Agrário
- 💰 Direito Tributário

---

## 🔧 Desenvolvimento

### Setup Ambiente

```bash
# 1. Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar .env
cp .env.example .env
# Editar .env com OPENAI_API_KEY

# 4. Executar
streamlit run streamlit_app.py
```

### Adicionar Nova Área do Direito

1. **Criar agente especialista**:
   ```python
   # agents/especialistas/nova_area_agent.py
   class AgenteNovaArea:
       # Implementar métodos padrão
   ```

2. **Adicionar em `database/models.py`**:
   - Inserir área em `initialize_default_data()`

3. **Criar templates**:
   - `database/templates/nova_area/modelo_tipo_acao.md`

4. **Atualizar cores** em `streamlit_app.py`:
   ```python
   cores = {
       'Nova Área': ('#HEXCOR', '#HEXCORCLARA'),
   }
   ```

### Adicionar Novo Tipo de Petição

1. **Criar template** em `database/templates/{area}/`
   - Usar placeholders `{VARIAVEL_MAIUSCULA}`

2. **Registrar no banco**:
   ```python
   template = TemplatePeticao(
       area_id=area_id,
       nome="Nome do Tipo",
       tipo_peticao="inicial",  # ou recurso, contestação, etc
       conteudo=template_text,
       variaveis=['NOME_AUTOR', 'CPF', ...]
   )
   ```

### Implementar Busca Real (Browser Use)

Localização: `services/jurisprudencia_service.py`

Método a implementar: `_buscar_[tribunal](query, area)`

```python
async def _buscar_stj(self, query: str, area_direito: str) -> List[Dict]:
    """
    Implementar usando Browser Use:
    1. Navegar para site do STJ
    2. Pesquisar por query
    3. Extrair resultados
    4. Parsear e estruturar dados
    5. Retornar lista de jurisprudências
    """
    # TODO: Implementação com Browser Use
    pass
```

---

## 🧪 Testes

### Estrutura de Testes (Futuro)

```
tests/
├── test_agents/
│   ├── test_filtro_agent.py
│   └── test_civil_agent.py
├── test_services/
│   ├── test_jurisprudencia.py
│   └── test_doutrina.py
└── test_database/
    └── test_models.py
```

### Executar Testes

```bash
pytest tests/ -v
```

---

## 📚 Recursos e Referências

### Documentação Técnica

- [Streamlit Docs](https://docs.streamlit.io/)
- [CrewAI Docs](https://docs.crewai.com/)
- [LangChain Docs](https://python.langchain.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Browser Use GitHub](https://github.com/browser-use/browser-use)

### Recursos Jurídicos

**Tribunais**:
- [STF](https://portal.stf.jus.br/)
- [STJ](https://www.stj.jus.br/)
- [JusBrasil](https://www.jusbrasil.com.br/)

**Legislação**:
- [Planalto - Legislação](http://www.planalto.gov.br/ccivil_03/)

---

## 🚧 Status de Implementação

### ✅ Implementado

- [x] Estrutura de pastas e arquivos
- [x] Banco de dados SQLite com modelos
- [x] Interface Streamlit moderna
- [x] Agente Filtro básico
- [x] Agente Civil básico
- [x] Serviços de busca (estrutura)
- [x] Templates de petições (exemplo)
- [x] Sistema de cache

### 🚧 Em Desenvolvimento

- [ ] Integração completa Browser Use
- [ ] Busca real em tribunais
- [ ] Geração de PDFs formatados
- [ ] Orquestração CrewAI completa
- [ ] Demais agentes especialistas (5 áreas)
- [ ] Sistema RAG para conhecimento

### 📅 Roadmap Futuro

- [ ] Autenticação de usuários
- [ ] Multi-tenancy
- [ ] API REST
- [ ] Dashboard analytics
- [ ] Versionamento de petições
- [ ] Colaboração em tempo real

---

## 🐛 Debugging

### Logs

Streamlit exibe logs no console. Para debug:

```python
import streamlit as st

st.write("Debug:", variavel)  # Output na interface
print("Debug:", variavel)     # Output no console
```

### Banco de Dados

Visualizar BD SQLite:

```bash
sqlite3 data/lobojur.db

# No prompt sqlite:
.tables                    # Listar tabelas
.schema areas_direito      # Ver estrutura
SELECT * FROM areas_direito;
```

### Session State

Verificar estado da sessão:

```python
st.write(st.session_state)
```

---

## 🤝 Contribuindo

### Processo de Contribuição

1. **Entender o contexto**: Ler este CLAUDE.md completamente
2. **Verificar estrutura**: Seguir padrões estabelecidos
3. **Testar localmente**: Garantir que funciona
4. **Documentar**: Atualizar docs se necessário
5. **Commit**: Mensagens claras e descritivas

### Mensagens de Commit

Formato: `tipo(escopo): descrição`

**Tipos**:
- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Documentação
- `style`: Formatação
- `refactor`: Refatoração
- `test`: Testes
- `chore`: Manutenção

**Exemplos**:
```
feat(agents): adiciona agente de direito criminal
fix(database): corrige query de jurisprudências
docs(readme): atualiza instruções de instalação
refactor(services): melhora performance de busca
```

---

## 💡 Dicas para Assistentes de IA

### Ao Trabalhar Neste Repositório:

1. **Sempre verifique** a estrutura existente antes de criar novos arquivos
2. **Mantenha consistência** com o código existente
3. **Use type hints** em todas as funções
4. **Documente** código complexo
5. **Teste** alterações localmente quando possível
6. **Siga** os padrões de nomeação estabelecidos
7. **Atualize** este CLAUDE.md se adicionar padrões novos

### Perguntas Comuns:

**Q: Onde adicionar nova funcionalidade de busca?**
A: Em `services/`, seguindo padrão de `jurisprudencia_service.py`

**Q: Como criar novo agente especialista?**
A: Copiar `civil_agent.py`, adaptar backstory e métodos específicos

**Q: Onde ficam templates de petições?**
A: `database/templates/{area}/modelo_*.md`

**Q: Como adicionar nova tabela no BD?**
A: Criar modelo em `database/models.py`, depois o banco recria automaticamente

**Q: Interface não atualiza, o que fazer?**
A: Streamlit tem cache agressivo. Use `st.rerun()` ou force refresh (Ctrl+R)

---

## 📞 Suporte

Para dúvidas sobre este projeto:

- **GitHub Issues**: Para bugs e features
- **Documentação**: README.md para uso geral
- **Este arquivo**: CLAUDE.md para desenvolvimento

---

**Última atualização**: 2025-12-08
**Versão**: 1.0.0
**Mantido por**: Equipe LoboJur

---

*Este guia foi criado especificamente para assistentes de IA trabalharem eficientemente neste repositório. Mantenha-o atualizado conforme o projeto evolui.*
