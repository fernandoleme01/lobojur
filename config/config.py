"""
Configurações do sistema
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Diretórios base
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"
EXPORTS_DIR = DATA_DIR / "exports"
TEMPLATES_DIR = BASE_DIR / "database" / "templates"

# Criar diretórios se não existirem
for dir_path in [DATA_DIR, CACHE_DIR, EXPORTS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Configurações do LLM
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4-turbo-preview")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "4000"))

# Configurações do Browser Use
BROWSER_HEADLESS = os.getenv("BROWSER_HEADLESS", "True").lower() == "true"
BROWSER_TIMEOUT = int(os.getenv("BROWSER_TIMEOUT", "30"))

# Configurações de busca
MAX_JURISPRUDENCIAS = int(os.getenv("MAX_JURISPRUDENCIAS", "5"))
MAX_DOUTRINAS = int(os.getenv("MAX_DOUTRINAS", "3"))

# Tribunais para busca
TRIBUNAIS = {
    'STF': 'https://portal.stf.jus.br/jurisprudencia/',
    'STJ': 'https://scon.stj.jus.br/SCON/',
    'TST': 'https://jurisprudencia.tst.jus.br/',
    'JUSBRASIL': 'https://www.jusbrasil.com.br/jurisprudencia/'
}

# Fontes de doutrina
FONTES_DOUTRINA = {
    'GOOGLE_SCHOLAR': 'https://scholar.google.com.br/',
    'SCIELO': 'https://www.scielo.br/',
    'CAPES': 'https://www.periodicos.capes.gov.br/'
}

# Áreas do Direito
AREAS_DIREITO = [
    'Direito Ambiental',
    'Direito Civil',
    'Direito Criminal',
    'Direito Empresarial',
    'Direito Agrário',
    'Direito Tributário'
]

# Configurações do Streamlit
STREAMLIT_THEME = {
    'primaryColor': '#1E3A8A',
    'backgroundColor': '#FFFFFF',
    'secondaryBackgroundColor': '#F3F4F6',
    'textColor': '#1F2937',
    'font': 'sans serif'
}
