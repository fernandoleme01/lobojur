"""Templates para geração de laudos técnicos jurídicos."""

from typing import Dict, Any, Optional
from datetime import datetime


class ReportTemplates:
    """Templates para diferentes tipos de laudos técnicos."""

    @staticmethod
    def get_full_report_template() -> str:
        """Template completo de laudo técnico pericial."""
        return """
═══════════════════════════════════════════════════════════════
                        LAUDO TÉCNICO PERICIAL
                     ANÁLISE DE CONTRATO JURÍDICO
═══════════════════════════════════════════════════════════════

LAUDO Nº: {laudo_numero}
DATA: {data_emissao}

═══════════════════════════════════════════════════════════════
1. IDENTIFICAÇÃO
═══════════════════════════════════════════════════════════════

1.1. PERITO RESPONSÁVEL
Nome: {perito_nome}
Registro: {perito_registro}
Especialidade: {perito_especialidade}

1.2. PARTES ENVOLVIDAS

PARTE 1 (CONTRATANTE):
Nome/Razão Social: {parte1_nome}
CPF/CNPJ: {parte1_documento}
Endereço: {parte1_endereco}
Representante Legal: {parte1_representante}

PARTE 2 (CONTRATADA):
Nome/Razão Social: {parte2_nome}
CPF/CNPJ: {parte2_documento}
Endereço: {parte2_endereco}
Representante Legal: {parte2_representante}

1.3. OBJETO DA PERÍCIA
{objeto_pericia}

═══════════════════════════════════════════════════════════════
2. PREÂMBULO
═══════════════════════════════════════════════════════════════

2.1. OBJETIVO DO LAUDO
{objetivo}

2.2. QUESITOS A RESPONDER
{quesitos}

2.3. METODOLOGIA UTILIZADA
{metodologia}

2.4. DOCUMENTOS ANALISADOS
{documentos_analisados}

═══════════════════════════════════════════════════════════════
3. ANÁLISE TÉCNICA DO CONTRATO
═══════════════════════════════════════════════════════════════

3.1. CARACTERIZAÇÃO DO CONTRATO
Tipo: {tipo_contrato}
Data de Assinatura: {data_assinatura}
Local: {local_assinatura}
Número de Páginas: {num_paginas}
Número de Cláusulas: {num_clausulas}

3.2. OBJETO CONTRATUAL
{objeto_contratual}

3.3. ANÁLISE DAS CLÁUSULAS ESSENCIAIS

{analise_clausulas}

3.4. OBRIGAÇÕES DAS PARTES

OBRIGAÇÕES DA PARTE 1:
{obrigacoes_parte1}

OBRIGAÇÕES DA PARTE 2:
{obrigacoes_parte2}

═══════════════════════════════════════════════════════════════
4. ASPECTOS JURÍDICOS
═══════════════════════════════════════════════════════════════

4.1. CONFORMIDADE LEGAL
{conformidade_legal}

4.2. BASE LEGAL APLICÁVEL
{base_legal}

4.3. CLÁUSULAS DE ATENÇÃO ESPECIAL
{clausulas_atencao}

4.4. IDENTIFICAÇÃO DE RISCOS JURÍDICOS
{riscos_juridicos}

═══════════════════════════════════════════════════════════════
5. ASPECTOS FINANCEIROS
═══════════════════════════════════════════════════════════════

5.1. VALORES CONTRATUAIS
Valor Total: {valor_total}
Forma de Pagamento: {forma_pagamento}
Parcelas: {parcelas}

5.2. REAJUSTES E ÍNDICES
{reajustes}

5.3. MULTAS E PENALIDADES
{multas_penalidades}

5.4. GARANTIAS EXIGIDAS
{garantias}

5.5. PROJEÇÃO FINANCEIRA
{projecao_financeira}

═══════════════════════════════════════════════════════════════
6. PRAZOS E VIGÊNCIA
═══════════════════════════════════════════════════════════════

6.1. PRAZO DE VIGÊNCIA
{prazo_vigencia}

6.2. CONDIÇÕES DE PRORROGAÇÃO
{condicoes_prorrogacao}

6.3. RESCISÃO CONTRATUAL
{condicoes_rescisao}

6.4. PRAZOS PRESCRICIONAIS
{prazos_prescricionais}

═══════════════════════════════════════════════════════════════
7. AVALIAÇÃO DE RISCOS
═══════════════════════════════════════════════════════════════

7.1. MATRIZ DE RISCOS

{matriz_riscos}

7.2. RISCOS JURÍDICOS IDENTIFICADOS
{detalhamento_riscos_juridicos}

7.3. RISCOS FINANCEIROS IDENTIFICADOS
{detalhamento_riscos_financeiros}

7.4. RISCOS OPERACIONAIS
{riscos_operacionais}

═══════════════════════════════════════════════════════════════
8. RESPOSTAS AOS QUESITOS
═══════════════════════════════════════════════════════════════

{respostas_quesitos}

═══════════════════════════════════════════════════════════════
9. CONCLUSÃO
═══════════════════════════════════════════════════════════════

9.1. SÍNTESE DA ANÁLISE
{sintese_analise}

9.2. PARECER TÉCNICO
{parecer_tecnico}

9.3. RECOMENDAÇÕES
{recomendacoes}

═══════════════════════════════════════════════════════════════
10. ENCERRAMENTO
═══════════════════════════════════════════════════════════════

Local e Data: {local_data_final}

Nada mais havendo a declarar, encerro o presente laudo técnico pericial,
o qual submeto à apreciação e julgamento.


_________________________________
{perito_nome}
{perito_registro}
Perito Técnico


═══════════════════════════════════════════════════════════════
ANEXOS
═══════════════════════════════════════════════════════════════

{anexos}
"""

    @staticmethod
    def get_summary_template() -> str:
        """Template de resumo executivo."""
        return """
═══════════════════════════════════════════════════════════════
                      RESUMO EXECUTIVO
                   ANÁLISE DE CONTRATO
═══════════════════════════════════════════════════════════════

DATA: {data}
CONTRATO: {tipo_contrato}

─────────────────────────────────────────────────────────────
1. PARTES
─────────────────────────────────────────────────────────────
{partes}

─────────────────────────────────────────────────────────────
2. OBJETO
─────────────────────────────────────────────────────────────
{objeto}

─────────────────────────────────────────────────────────────
3. VALORES E PRAZOS
─────────────────────────────────────────────────────────────
Valor Total: {valor_total}
Prazo: {prazo}
Vigência: {vigencia}

─────────────────────────────────────────────────────────────
4. PRINCIPAIS OBRIGAÇÕES
─────────────────────────────────────────────────────────────
{obrigacoes}

─────────────────────────────────────────────────────────────
5. PONTOS CRÍTICOS
─────────────────────────────────────────────────────────────
{pontos_criticos}

─────────────────────────────────────────────────────────────
6. RISCOS IDENTIFICADOS
─────────────────────────────────────────────────────────────
{riscos}

─────────────────────────────────────────────────────────────
7. RECOMENDAÇÕES
─────────────────────────────────────────────────────────────
{recomendacoes}
"""

    @staticmethod
    def get_risk_assessment_template() -> str:
        """Template de avaliação de riscos."""
        return """
═══════════════════════════════════════════════════════════════
                   AVALIAÇÃO DE RISCOS CONTRATUAIS
═══════════════════════════════════════════════════════════════

CONTRATO: {contrato_id}
DATA: {data}

═══════════════════════════════════════════════════════════════
MATRIZ DE RISCOS
═══════════════════════════════════════════════════════════════

{matriz_riscos_tabela}

═══════════════════════════════════════════════════════════════
DETALHAMENTO DOS RISCOS
═══════════════════════════════════════════════════════════════

1. RISCOS JURÍDICOS (Nível: {nivel_risco_juridico})
───────────────────────────────────────────────────────────────
{riscos_juridicos}

2. RISCOS FINANCEIROS (Nível: {nivel_risco_financeiro})
───────────────────────────────────────────────────────────────
{riscos_financeiros}

3. RISCOS OPERACIONAIS (Nível: {nivel_risco_operacional})
───────────────────────────────────────────────────────────────
{riscos_operacionais}

═══════════════════════════════════════════════════════════════
PLANO DE MITIGAÇÃO
═══════════════════════════════════════════════════════════════

{plano_mitigacao}

═══════════════════════════════════════════════════════════════
CONCLUSÃO E RECOMENDAÇÕES
═══════════════════════════════════════════════════════════════

NÍVEL DE RISCO GERAL: {nivel_risco_geral}

{conclusao_riscos}
"""

    @staticmethod
    def get_comparative_template() -> str:
        """Template de análise comparativa."""
        return """
═══════════════════════════════════════════════════════════════
                    ANÁLISE COMPARATIVA DE CONTRATOS
═══════════════════════════════════════════════════════════════

DATA: {data}

CONTRATO A: {contrato_a_id}
CONTRATO B: {contrato_b_id}

═══════════════════════════════════════════════════════════════
1. DIFERENÇAS ESTRUTURAIS
═══════════════════════════════════════════════════════════════

{diferencas_estruturais}

═══════════════════════════════════════════════════════════════
2. DIFERENÇAS EM CLÁUSULAS ESSENCIAIS
═══════════════════════════════════════════════════════════════

{diferencas_clausulas}

═══════════════════════════════════════════════════════════════
3. VARIAÇÕES FINANCEIRAS
═══════════════════════════════════════════════════════════════

{variacoes_financeiras}

═══════════════════════════════════════════════════════════════
4. MUDANÇAS EM OBRIGAÇÕES
═══════════════════════════════════════════════════════════════

{mudancas_obrigacoes}

═══════════════════════════════════════════════════════════════
5. ALTERAÇÕES EM PRAZOS E CONDIÇÕES
═══════════════════════════════════════════════════════════════

{alteracoes_prazos}

═══════════════════════════════════════════════════════════════
6. IMPACTO DAS DIFERENÇAS
═══════════════════════════════════════════════════════════════

{impacto}

═══════════════════════════════════════════════════════════════
7. RECOMENDAÇÕES
═══════════════════════════════════════════════════════════════

{recomendacoes}
"""

    @staticmethod
    def format_risk_matrix(risks: Dict[str, Any]) -> str:
        """Formata matriz de riscos."""
        matrix = """
┌─────────────────────────────┬───────────┬──────────────┬─────────────┐
│ Categoria de Risco          │ Nível     │ Probabilidade│ Impacto     │
├─────────────────────────────┼───────────┼──────────────┼─────────────┤
"""
        for category, data in risks.items():
            matrix += f"│ {category:<27} │ {data['nivel']:<9} │ {data['probabilidade']:<12} │ {data['impacto']:<11} │\n"

        matrix += "└─────────────────────────────┴───────────┴──────────────┴─────────────┘"
        return matrix

    @staticmethod
    def format_checklist(items: list) -> str:
        """Formata checklist."""
        checklist = ""
        for item in items:
            status = "✓" if item.get('completed') else "☐"
            checklist += f"{status} {item['description']}\n"
        return checklist
