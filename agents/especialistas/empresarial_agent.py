"""
Agente Especialista em Direito Empresarial
"""
from typing import Dict, List


class AgenteDireitoEmpresarial:
    """Agente especializado em Direito Empresarial"""

    def __init__(self, llm, jurisprudencia_service, doutrina_service):
        self.llm = llm
        self.jurisprudencia_service = jurisprudencia_service
        self.doutrina_service = doutrina_service

        self.backstory = """
        Você é um advogado empresarial experiente, especializado em:
        - Constituição de sociedades (LTDA, SA, SLU)
        - Contratos empresariais
        - Recuperação judicial e falência
        - Direito societário
        - Propriedade intelectual (marcas, patentes)
        - Compliance e governança corporativa
        - Fusões e aquisições (M&A)
        - Direito do consumidor empresarial
        - Títulos de crédito
        - Arbitragem comercial

        Legislação principal:
        - Código Civil (arts. 966 a 1.195 - Direito de Empresa)
        - Lei 11.101/05 (Recuperação Judicial e Falência)
        - Lei 6.404/76 (Lei das S.A.)
        - Lei 9.279/96 (Propriedade Industrial)
        - Lei 9.609/98 (Software)
        - Lei 8.078/90 (CDC nas relações empresariais)
        - Lei 13.874/19 (Declaração de Direitos de Liberdade Econômica)

        Doutrinadores:
        - Fábio Ulhoa Coelho
        - André Luiz Santa Cruz Ramos
        - Gladston Mamede
        - Marlon Tomazette
        """

    async def analisar_caso(self, contexto: str) -> Dict:
        """Analisa caso empresarial"""
        tipo_acao = self._identificar_tipo_acao(contexto)
        partes = self._identificar_partes(contexto)
        fatos = self._extrair_fatos(contexto)
        fundamentos = self._identificar_fundamentos(contexto)
        pedidos = self._sugerir_pedidos(contexto, tipo_acao)
        documentos = self._sugerir_documentos(contexto)

        return {
            'tipo_acao': tipo_acao,
            'partes': partes,
            'fatos': fatos,
            'fundamentos': fundamentos,
            'pedidos': pedidos,
            'documentos_necessarios': documentos
        }

    def _identificar_tipo_acao(self, contexto: str) -> str:
        """Identifica tipo de ação/serviço empresarial"""
        contexto_lower = contexto.lower()

        tipos = {
            'constituição de empresa': ['constituir', 'abrir empresa', 'criar sociedade'],
            'alteração contratual': ['alteração', 'mudança de sócios', 'capital social'],
            'recuperação judicial': ['recuperação judicial', 'rj', 'crise financeira'],
            'dissolução de sociedade': ['dissolução', 'encerramento', 'baixa'],
            'ação de dissolução parcial': ['retirada de sócio', 'apuração de haveres'],
            'registro de marca': ['marca', 'registro inpi'],
            'contrato empresarial': ['contrato', 'fornecimento', 'distribuição'],
            'ação de cobrança empresarial': ['cobrança', 'inadimplemento', 'duplicata'],
            'arbitragem comercial': ['arbitragem', 'câmara arbitral']
        }

        for tipo, palavras_chave in tipos.items():
            if any(palavra in contexto_lower for palavra in palavras_chave):
                return tipo

        return 'consultoria empresarial'

    def _identificar_partes(self, contexto: str) -> Dict:
        """Identifica partes empresariais"""
        return {
            'sociedade': 'Razão Social da Empresa',
            'sócios': ['Sócio 1', 'Sócio 2'],
            'cnpj': '00.000.000/0001-00',
            'tipo_societário': 'LTDA/SA/SLU'
        }

    def _extrair_fatos(self, contexto: str) -> List[str]:
        """Extrai fatos empresarialmente relevantes"""
        return [
            "Objeto social da empresa",
            "Situação financeira/patrimonial",
            "Relação entre sócios",
            "Operações empresariais relevantes"
        ]

    def _identificar_fundamentos(self, contexto: str) -> List[str]:
        """Fundamentos jurídicos empresariais"""
        return [
            "Código Civil - Livro II (Direito de Empresa)",
            "Princípio da preservação da empresa",
            "Função social da empresa",
            "Boa-fé objetiva nas relações empresariais",
            "Jurisprudência do STJ (Direito Empresarial)"
        ]

    def _sugerir_pedidos(self, contexto: str, tipo_acao: str) -> List[str]:
        """Sugere pedidos para casos empresariais"""
        if 'recuperação' in tipo_acao.lower():
            return [
                "Deferimento do processamento da recuperação judicial",
                "Suspensão de ações e execuções (art. 6º Lei 11.101/05)",
                "Aprovação do plano de recuperação judicial",
                "Concessão do stay period"
            ]
        elif 'dissolução' in tipo_acao.lower():
            return [
                "Dissolução parcial da sociedade",
                "Apuração de haveres do sócio retirante",
                "Nomeação de perito contador",
                "Pagamento das quotas em X parcelas"
            ]
        elif 'marca' in tipo_acao.lower():
            return [
                "Registro da marca junto ao INPI",
                "Proteção em todas as classes relevantes",
                "Oposição a pedidos conflitantes"
            ]
        elif 'cobrança' in tipo_acao.lower():
            return [
                "Condenação do réu ao pagamento do valor devido",
                "Juros de mora e correção monetária",
                "Honorários advocatícios e custas processuais",
                "Protesto do título"
            ]
        else:
            return [
                "Reconhecimento do direito pleiteado",
                "Cumprimento das obrigações contratuais"
            ]

    def _sugerir_documentos(self, contexto: str) -> List[str]:
        """Sugere documentos necessários"""
        documentos = [
            "Contrato social/Estatuto social atualizado",
            "Última alteração contratual registrada",
            "Cartão CNPJ",
            "Balanços patrimoniais (últimos 3 anos)",
            "Certidões negativas (federal, estadual, municipal)",
            "Ata de reunião/assembleia (se aplicável)"
        ]

        contexto_lower = contexto.lower()

        if 'recuperação' in contexto_lower:
            documentos.extend([
                "Demonstrações financeiras",
                "Relação de credores",
                "Certidão de protestos",
                "Relação de empregados"
            ])

        if 'marca' in contexto_lower:
            documentos.extend([
                "Logotipo da marca",
                "Comprovante de atividade empresarial",
                "Procuração para INPI"
            ])

        return documentos

    async def buscar_fundamentacao(self, analise: Dict) -> Dict:
        """Busca jurisprudências empresariais"""
        return {
            'jurisprudencias': [],
            'doutrinas': [],
            'precedentes_stj': []
        }
