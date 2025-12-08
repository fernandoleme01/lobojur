"""
Sistema Multi-LLM - Gerenciador de Múltiplos Modelos
Aproveita melhor modelo para cada tarefa
"""
from typing import Dict, List, Optional, Union
from enum import Enum
import anthropic
import openai
from google import generativeai as genai
import cohere
import logging

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Provedores de LLM disponíveis"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    COHERE = "cohere"
    OPENROUTER = "openrouter"


class ModelCapability(Enum):
    """Capacidades dos modelos"""
    LONG_CONTEXT = "long_context"          # Claude 3, Gemini 1.5 Pro
    FAST_RESPONSE = "fast_response"        # GPT-3.5, Claude Haiku
    REASONING = "reasoning"                # GPT-4, Claude 3 Opus
    EMBEDDINGS = "embeddings"              # text-embedding-3, Cohere
    VISION = "vision"                      # GPT-4V, Claude 3, Gemini Pro Vision
    FUNCTION_CALLING = "function_calling"  # GPT-4, Claude 3


class MultiLLMManager:
    """Gerenciador central de múltiplos LLMs"""

    def __init__(self, api_keys: Dict[str, str]):
        """
        Inicializa gerenciador multi-LLM

        Args:
            api_keys: Dict com chaves de cada provider
                {
                    'openai': 'sk-...',
                    'anthropic': 'sk-ant-...',
                    'google': 'AIza...',
                    'cohere': 'xxx',
                    'openrouter': 'sk-or-...'
                }
        """
        self.api_keys = api_keys
        self.clients = {}
        self._initialize_clients()

    def _initialize_clients(self):
        """Inicializa clientes de cada provider"""

        # OpenAI
        if 'openai' in self.api_keys:
            openai.api_key = self.api_keys['openai']
            self.clients['openai'] = openai

        # Anthropic (Claude)
        if 'anthropic' in self.api_keys:
            self.clients['anthropic'] = anthropic.Anthropic(
                api_key=self.api_keys['anthropic']
            )

        # Google (Gemini)
        if 'google' in self.api_keys:
            genai.configure(api_key=self.api_keys['google'])
            self.clients['google'] = genai

        # Cohere
        if 'cohere' in self.api_keys:
            self.clients['cohere'] = cohere.Client(
                api_key=self.api_keys['cohere']
            )

        logger.info(f"Inicializados {len(self.clients)} provedores de LLM")

    # ==================== CONFIGURAÇÕES DE MODELOS ====================

    MODELS_CONFIG = {
        # OpenAI
        "gpt-4-turbo-preview": {
            "provider": LLMProvider.OPENAI,
            "max_tokens": 128000,
            "capabilities": [
                ModelCapability.LONG_CONTEXT,
                ModelCapability.REASONING,
                ModelCapability.FUNCTION_CALLING
            ],
            "cost_per_1k_input": 0.01,
            "cost_per_1k_output": 0.03,
            "use_for": ["análise_complexa", "petições_complexas", "pareceres"]
        },
        "gpt-3.5-turbo": {
            "provider": LLMProvider.OPENAI,
            "max_tokens": 16385,
            "capabilities": [
                ModelCapability.FAST_RESPONSE,
                ModelCapability.FUNCTION_CALLING
            ],
            "cost_per_1k_input": 0.0005,
            "cost_per_1k_output": 0.0015,
            "use_for": ["chat", "triagem", "resumos_simples"]
        },

        # Anthropic (Claude)
        "claude-3-opus-20240229": {
            "provider": LLMProvider.ANTHROPIC,
            "max_tokens": 200000,
            "capabilities": [
                ModelCapability.LONG_CONTEXT,
                ModelCapability.REASONING,
                ModelCapability.VISION,
                ModelCapability.FUNCTION_CALLING
            ],
            "cost_per_1k_input": 0.015,
            "cost_per_1k_output": 0.075,
            "use_for": ["análise_profunda", "documentos_longos", "contratos"]
        },
        "claude-3-sonnet-20240229": {
            "provider": LLMProvider.ANTHROPIC,
            "max_tokens": 200000,
            "capabilities": [
                ModelCapability.LONG_CONTEXT,
                ModelCapability.FAST_RESPONSE,
                ModelCapability.VISION
            ],
            "cost_per_1k_input": 0.003,
            "cost_per_1k_output": 0.015,
            "use_for": ["petições_médias", "análise_jurisprudências", "pesquisa"]
        },
        "claude-3-haiku-20240307": {
            "provider": LLMProvider.ANTHROPIC,
            "max_tokens": 200000,
            "capabilities": [
                ModelCapability.LONG_CONTEXT,
                ModelCapability.FAST_RESPONSE
            ],
            "cost_per_1k_input": 0.00025,
            "cost_per_1k_output": 0.00125,
            "use_for": ["chat_rápido", "classificação", "extração_dados"]
        },

        # Google (Gemini)
        "gemini-1.5-pro": {
            "provider": LLMProvider.GOOGLE,
            "max_tokens": 2097152,  # 2 MILHÕES de tokens!
            "capabilities": [
                ModelCapability.LONG_CONTEXT,
                ModelCapability.VISION,
                ModelCapability.REASONING
            ],
            "cost_per_1k_input": 0.0035,
            "cost_per_1k_output": 0.0105,
            "use_for": ["processos_completos", "vários_documentos", "histórico_completo"]
        },

        # Cohere
        "command-r-plus": {
            "provider": LLMProvider.COHERE,
            "max_tokens": 128000,
            "capabilities": [
                ModelCapability.LONG_CONTEXT,
                ModelCapability.REASONING
            ],
            "cost_per_1k_input": 0.003,
            "cost_per_1k_output": 0.015,
            "use_for": ["busca_semântica", "rag", "pesquisa"]
        }
    }

    # ==================== SELEÇÃO AUTOMÁTICA DE MODELO ====================

    def select_best_model(
        self,
        task_type: str,
        context_size: int = 0,
        budget: str = "medium"  # low, medium, high
    ) -> str:
        """
        Seleciona melhor modelo baseado na tarefa

        Args:
            task_type: Tipo de tarefa (análise_complexa, chat, petição, etc)
            context_size: Tamanho estimado do contexto em tokens
            budget: Orçamento (low=barato, medium=balanceado, high=melhor)

        Returns:
            Nome do modelo selecionado
        """
        candidates = []

        # Filtrar modelos adequados para a tarefa
        for model_name, config in self.MODELS_CONFIG.items():
            if task_type in config.get('use_for', []):
                # Verificar se suporta o tamanho do contexto
                if context_size <= config['max_tokens']:
                    candidates.append((model_name, config))

        if not candidates:
            # Fallback: usar GPT-3.5 ou Claude Haiku
            return "gpt-3.5-turbo" if 'openai' in self.clients else "claude-3-haiku-20240307"

        # Ordenar por custo baseado no budget
        if budget == "low":
            candidates.sort(key=lambda x: x[1]['cost_per_1k_input'])
        elif budget == "high":
            candidates.sort(key=lambda x: x[1]['cost_per_1k_input'], reverse=True)
        else:
            # Medium: balanceado entre custo e performance
            candidates.sort(key=lambda x: (
                x[1]['cost_per_1k_input'] + x[1]['cost_per_1k_output']
            ) / 2)

        selected_model = candidates[0][0]
        logger.info(f"Modelo selecionado para '{task_type}': {selected_model}")

        return selected_model

    # ==================== CHAMADAS UNIFICADAS ====================

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        task_type: str = "chat",
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Gera resposta usando o modelo apropriado

        Args:
            prompt: Prompt do usuário
            model: Modelo específico (None = seleção automática)
            task_type: Tipo da tarefa
            temperature: Temperatura (0-1)
            max_tokens: Máximo de tokens na resposta
            system_prompt: System prompt (se aplicável)

        Returns:
            Resposta gerada
        """
        # Selecionar modelo automaticamente se não especificado
        if model is None:
            context_size = len(prompt.split()) * 1.3  # Estimativa rough
            model = self.select_best_model(task_type, int(context_size))

        config = self.MODELS_CONFIG.get(model)
        if not config:
            raise ValueError(f"Modelo {model} não configurado")

        provider = config['provider']

        # Chamar provider apropriado
        if provider == LLMProvider.OPENAI:
            return self._call_openai(prompt, model, temperature, max_tokens, system_prompt)
        elif provider == LLMProvider.ANTHROPIC:
            return self._call_anthropic(prompt, model, temperature, max_tokens, system_prompt)
        elif provider == LLMProvider.GOOGLE:
            return self._call_google(prompt, model, temperature, max_tokens)
        elif provider == LLMProvider.COHERE:
            return self._call_cohere(prompt, model, temperature, max_tokens)
        else:
            raise ValueError(f"Provider {provider} não implementado")

    def _call_openai(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        system_prompt: Optional[str]
    ) -> str:
        """Chama OpenAI API"""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        response = self.clients['openai'].chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return response.choices[0].message.content

    def _call_anthropic(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        system_prompt: Optional[str]
    ) -> str:
        """Chama Anthropic (Claude) API"""
        message = self.clients['anthropic'].messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt or "",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return message.content[0].text

    def _call_google(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Chama Google (Gemini) API"""
        gemini_model = self.clients['google'].GenerativeModel(model)

        response = gemini_model.generate_content(
            prompt,
            generation_config={
                'temperature': temperature,
                'max_output_tokens': max_tokens
            }
        )

        return response.text

    def _call_cohere(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Chama Cohere API"""
        response = self.clients['cohere'].generate(
            model=model,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return response.generations[0].text

    # ==================== EMBEDDINGS ====================

    def create_embedding(
        self,
        text: Union[str, List[str]],
        model: str = "text-embedding-3-large"
    ) -> List[float]:
        """
        Cria embedding para RAG

        Args:
            text: Texto ou lista de textos
            model: Modelo de embedding

        Returns:
            Vetor de embedding
        """
        if 'openai' in self.clients:
            response = self.clients['openai'].embeddings.create(
                model=model,
                input=text
            )
            return response.data[0].embedding

        elif 'cohere' in self.clients:
            response = self.clients['cohere'].embed(
                texts=[text] if isinstance(text, str) else text,
                model='embed-multilingual-v3.0'
            )
            return response.embeddings[0]

        else:
            raise ValueError("Nenhum provider de embeddings disponível")


# ==================== EXEMPLOS DE USO ====================

def exemplo_uso_multi_llm():
    """Exemplo de uso do sistema multi-LLM"""

    # Inicializar com múltiplas chaves
    manager = MultiLLMManager({
        'openai': 'sk-proj-...',
        'anthropic': 'sk-ant-...',
        'google': 'AIza...',
        'cohere': 'xxx'
    })

    # 1. Chat rápido (usará GPT-3.5 ou Claude Haiku - barato e rápido)
    resposta = manager.generate(
        prompt="Explique o que é usucapião",
        task_type="chat",
        budget="low"
    )
    print(f"Chat: {resposta}")

    # 2. Análise de processo completo (usará Gemini 1.5 Pro - 2M tokens!)
    processo_completo = """
    [Aqui entrariam 500 páginas de processo, jurisprudências, etc]
    """

    analise = manager.generate(
        prompt=f"Analise este processo completo e sugira estratégia:\n\n{processo_completo}",
        task_type="processos_completos",
        budget="medium",
        system_prompt="Você é um advogado especialista em direito civil"
    )
    print(f"Análise: {analise[:200]}...")

    # 3. Petição complexa (usará Claude 3 Opus - melhor raciocínio)
    peticao = manager.generate(
        prompt="Gere uma petição inicial de ação de indenização por danos morais...",
        task_type="petições_complexas",
        budget="high",
        temperature=0.3  # Mais determinístico para documentos formais
    )
    print(f"Petição: {peticao[:200]}...")

    # 4. Busca semântica (usará Cohere - especializado em search)
    embedding = manager.create_embedding(
        text="jurisprudência sobre dano moral e internet",
        model="text-embedding-3-large"
    )
    print(f"Embedding gerado: {len(embedding)} dimensões")
