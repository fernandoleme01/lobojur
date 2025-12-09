"""
Integração com Asaas - Gateway de Pagamento
"""
import requests
from typing import Dict, List, Optional
from decimal import Decimal
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class AsaasClient:
    """Cliente para integração com API do Asaas"""

    def __init__(self, api_key: str, sandbox: bool = False):
        """
        Inicializa cliente Asaas

        Args:
            api_key: Chave API do Asaas
            sandbox: Se True, usa ambiente de testes
        """
        self.api_key = api_key
        self.base_url = "https://sandbox.asaas.com/api/v3" if sandbox else "https://www.asaas.com/api/v3"
        self.headers = {
            "access_token": api_key,
            "Content-Type": "application/json"
        }

    def _request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Faz requisição à API"""
        url = f"{self.base_url}/{endpoint}"

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição Asaas: {str(e)}")
            raise

    # ==================== CLIENTES ====================

    def criar_cliente(
        self,
        nome: str,
        cpf_cnpj: str,
        email: str,
        telefone: str,
        endereco: Dict = None
    ) -> Dict:
        """
        Cria cliente no Asaas

        Args:
            nome: Nome completo ou razão social
            cpf_cnpj: CPF ou CNPJ
            email: Email do cliente
            telefone: Telefone
            endereco: Dados de endereço

        Returns:
            Dados do cliente criado
        """
        data = {
            "name": nome,
            "cpfCnpj": cpf_cnpj,
            "email": email,
            "phone": telefone,
            "mobilePhone": telefone,
            "notificationDisabled": False
        }

        if endereco:
            data.update({
                "address": endereco.get('logradouro'),
                "addressNumber": endereco.get('numero'),
                "complement": endereco.get('complemento'),
                "province": endereco.get('bairro'),
                "postalCode": endereco.get('cep')
            })

        return self._request("POST", "customers", data)

    def buscar_cliente(self, customer_id: str) -> Dict:
        """Busca cliente por ID"""
        return self._request("GET", f"customers/{customer_id}")

    # ==================== COBRANÇAS ====================

    def criar_cobranca(
        self,
        customer_id: str,
        valor: Decimal,
        vencimento: datetime,
        descricao: str,
        forma_pagamento: str = "UNDEFINED",  # BOLETO, CREDIT_CARD, PIX, UNDEFINED
        parcelas: int = 1,
        external_reference: str = None
    ) -> Dict:
        """
        Cria cobrança no Asaas

        Args:
            customer_id: ID do cliente no Asaas
            valor: Valor da cobrança
            vencimento: Data de vencimento
            descricao: Descrição da cobrança
            forma_pagamento: BOLETO, CREDIT_CARD, PIX, UNDEFINED
            parcelas: Número de parcelas (para cartão)
            external_reference: Referência externa (ex: ID do processo)

        Returns:
            Dados da cobrança criada
        """
        data = {
            "customer": customer_id,
            "billingType": forma_pagamento,
            "value": float(valor),
            "dueDate": vencimento.strftime("%Y-%m-%d"),
            "description": descricao,
            "externalReference": external_reference or f"PROCESSO_{datetime.now().timestamp()}"
        }

        if forma_pagamento == "CREDIT_CARD" and parcelas > 1:
            data["installmentCount"] = parcelas
            data["installmentValue"] = float(valor / parcelas)

        return self._request("POST", "payments", data)

    def criar_cobranca_pix(
        self,
        customer_id: str,
        valor: Decimal,
        descricao: str,
        external_reference: str = None
    ) -> Dict:
        """
        Cria cobrança PIX com QR Code

        Returns:
            Dict com 'encodedImage' (QR Code base64) e 'payload' (código PIX)
        """
        cobranca = self.criar_cobranca(
            customer_id=customer_id,
            valor=valor,
            vencimento=datetime.now() + timedelta(hours=2),
            descricao=descricao,
            forma_pagamento="PIX",
            external_reference=external_reference
        )

        # Gera QR Code PIX
        payment_id = cobranca['id']
        qr_code = self._request("GET", f"payments/{payment_id}/pixQrCode")

        return {
            "cobranca": cobranca,
            "qr_code": qr_code
        }

    def listar_cobrancas(
        self,
        customer_id: str = None,
        status: str = None,
        offset: int = 0,
        limit: int = 100
    ) -> List[Dict]:
        """
        Lista cobranças

        Args:
            customer_id: Filtrar por cliente
            status: PENDING, RECEIVED, CONFIRMED, OVERDUE, etc
            offset: Offset para paginação
            limit: Limite de resultados
        """
        params = {
            "offset": offset,
            "limit": limit
        }

        if customer_id:
            params["customer"] = customer_id
        if status:
            params["status"] = status

        endpoint = f"payments?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
        return self._request("GET", endpoint)

    def estornar_cobranca(self, payment_id: str) -> Dict:
        """Estorna uma cobrança paga"""
        return self._request("POST", f"payments/{payment_id}/refund")

    # ==================== ASSINATURAS (RECORRÊNCIA) ====================

    def criar_assinatura(
        self,
        customer_id: str,
        valor: Decimal,
        ciclo: str,  # WEEKLY, MONTHLY, YEARLY
        descricao: str,
        forma_pagamento: str = "CREDIT_CARD",
        dia_vencimento: int = 10
    ) -> Dict:
        """
        Cria assinatura recorrente

        Args:
            customer_id: ID do cliente
            valor: Valor da assinatura
            ciclo: WEEKLY, MONTHLY, YEARLY
            descricao: Descrição
            forma_pagamento: BOLETO ou CREDIT_CARD
            dia_vencimento: Dia do vencimento (1-28)
        """
        data = {
            "customer": customer_id,
            "billingType": forma_pagamento,
            "cycle": ciclo,
            "value": float(valor),
            "nextDueDate": self._calcular_proximo_vencimento(dia_vencimento),
            "description": descricao
        }

        return self._request("POST", "subscriptions", data)

    def cancelar_assinatura(self, subscription_id: str) -> Dict:
        """Cancela assinatura"""
        return self._request("DELETE", f"subscriptions/{subscription_id}")

    # ==================== SPLIT DE PAGAMENTOS ====================

    def criar_split(
        self,
        payment_id: str,
        splits: List[Dict]
    ) -> Dict:
        """
        Cria split de pagamento (divisão entre advogados/escritório)

        Args:
            payment_id: ID da cobrança
            splits: Lista de dicionários com 'walletId' e 'percentualValue' ou 'fixedValue'

        Example:
            splits = [
                {"walletId": "advogado_1_wallet", "percentualValue": 70},  # 70% para advogado
                {"walletId": "escritorio_wallet", "percentualValue": 30}   # 30% para escritório
            ]
        """
        data = {"payment": payment_id, "splits": splits}
        return self._request("POST", "paymentSplits", data)

    # ==================== TRANSFERÊNCIAS ====================

    def solicitar_transferencia(
        self,
        valor: Decimal,
        tipo_conta: str = "BANCO"  # BANCO ou PIX
    ) -> Dict:
        """
        Solicita transferência do saldo para conta bancária

        Args:
            valor: Valor a transferir
            tipo_conta: BANCO ou PIX
        """
        data = {
            "value": float(valor),
            "operationType": tipo_conta
        }
        return self._request("POST", "transfers", data)

    def consultar_saldo(self) -> Dict:
        """Consulta saldo disponível na conta"""
        return self._request("GET", "finance/getCurrentBalance")

    # ==================== WEBHOOKS ====================

    def processar_webhook(self, payload: Dict) -> Dict:
        """
        Processa notificação webhook do Asaas

        Events:
        - PAYMENT_CREATED
        - PAYMENT_UPDATED
        - PAYMENT_CONFIRMED
        - PAYMENT_RECEIVED
        - PAYMENT_OVERDUE
        - PAYMENT_REFUNDED
        """
        event = payload.get('event')
        payment = payload.get('payment', {})

        logger.info(f"Webhook Asaas recebido: {event} - Payment ID: {payment.get('id')}")

        # Processar cada tipo de evento
        handlers = {
            'PAYMENT_CONFIRMED': self._handle_payment_confirmed,
            'PAYMENT_RECEIVED': self._handle_payment_received,
            'PAYMENT_OVERDUE': self._handle_payment_overdue,
            'PAYMENT_REFUNDED': self._handle_payment_refunded
        }

        handler = handlers.get(event)
        if handler:
            return handler(payment)

        return {"status": "event_not_handled"}

    # ==================== MÉTODOS AUXILIARES ====================

    def _calcular_proximo_vencimento(self, dia: int) -> str:
        """Calcula próxima data de vencimento"""
        hoje = datetime.now()
        if hoje.day <= dia:
            proximo = hoje.replace(day=dia)
        else:
            # Próximo mês
            if hoje.month == 12:
                proximo = hoje.replace(year=hoje.year + 1, month=1, day=dia)
            else:
                proximo = hoje.replace(month=hoje.month + 1, day=dia)

        return proximo.strftime("%Y-%m-%d")

    def _handle_payment_confirmed(self, payment: Dict):
        """Trata pagamento confirmado"""
        # TODO: Atualizar status do processo no banco
        # TODO: Enviar notificação para advogado
        # TODO: Liberar acesso ao serviço
        logger.info(f"Pagamento confirmado: {payment['id']}")
        return {"status": "processed"}

    def _handle_payment_received(self, payment: Dict):
        """Trata pagamento recebido"""
        logger.info(f"Pagamento recebido: {payment['id']}")
        return {"status": "processed"}

    def _handle_payment_overdue(self, payment: Dict):
        """Trata pagamento vencido"""
        # TODO: Enviar lembrete ao cliente
        # TODO: Bloquear acesso se necessário
        logger.warning(f"Pagamento vencido: {payment['id']}")
        return {"status": "processed"}

    def _handle_payment_refunded(self, payment: Dict):
        """Trata estorno"""
        logger.info(f"Pagamento estornado: {payment['id']}")
        return {"status": "processed"}


# ==================== EXEMPLOS DE USO ====================

def exemplo_fluxo_completo():
    """Exemplo de fluxo completo de cobrança"""

    asaas = AsaasClient(api_key="SEU_API_KEY", sandbox=True)

    # 1. Criar cliente
    cliente = asaas.criar_cliente(
        nome="João Silva",
        cpf_cnpj="12345678901",
        email="joao@email.com",
        telefone="11999999999",
        endereco={
            "logradouro": "Rua Exemplo",
            "numero": "123",
            "bairro": "Centro",
            "cep": "01310-100"
        }
    )

    # 2. Criar cobrança PIX
    cobranca_pix = asaas.criar_cobranca_pix(
        customer_id=cliente['id'],
        valor=Decimal("500.00"),
        descricao="Honorários - Processo 1234/2024",
        external_reference="PROCESSO_1234"
    )

    print(f"QR Code PIX: {cobranca_pix['qr_code']['encodedImage']}")
    print(f"Código PIX: {cobranca_pix['qr_code']['payload']}")

    # 3. Criar assinatura mensal
    assinatura = asaas.criar_assinatura(
        customer_id=cliente['id'],
        valor=Decimal("299.90"),
        ciclo="MONTHLY",
        descricao="Plano Premium LoboJur",
        forma_pagamento="CREDIT_CARD",
        dia_vencimento=10
    )

    # 4. Consultar saldo
    saldo = asaas.consultar_saldo()
    print(f"Saldo disponível: R$ {saldo['balance']}")

    # 5. Solicitar transferência
    if saldo['balance'] > 100:
        transferencia = asaas.solicitar_transferencia(
            valor=Decimal("100.00"),
            tipo_conta="BANCO"
        )
        print(f"Transferência solicitada: {transferencia['id']}")
