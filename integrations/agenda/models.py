"""
Sistema de Agenda Completa
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Calendario(models.Model):
    """Calendários individuais ou compartilhados"""

    TIPOS = [
        ('PESSOAL', 'Pessoal'),
        ('TRABALHO', 'Trabalho'),
        ('AUDIENCIAS', 'Audiências'),
        ('PRAZOS', 'Prazos Processuais'),
        ('COMPARTILHADO', 'Compartilhado')
    ]

    nome = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20, choices=TIPOS, default='TRABALHO')
    cor = models.CharField(max_length=7, default='#3B82F6')
    descricao = models.TextField(blank=True)

    # Permissões
    proprietario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='calendarios')
    compartilhado_com = models.ManyToManyField(User, through='PermissaoCalendario', related_name='calendarios_compartilhados', blank=True)

    # Integração
    google_calendar_id = models.CharField(max_length=200, blank=True, help_text="ID do Google Calendar")
    sincronizar_google = models.BooleanField(default=False)

    criado_em = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.proprietario.username})"


class PermissaoCalendario(models.Model):
    """Permissões de calendários compartilhados"""

    NIVEIS = [
        ('VISUALIZAR', 'Apenas Visualizar'),
        ('EDITAR', 'Editar Eventos'),
        ('GERENCIAR', 'Gerenciar Tudo')
    ]

    calendario = models.ForeignKey(Calendario, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nivel = models.CharField(max_length=20, choices=NIVEIS, default='VISUALIZAR')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['calendario', 'usuario']


class Evento(models.Model):
    """Eventos da agenda"""

    TIPOS_EVENTO = [
        ('CONSULTA', 'Consulta com Cliente'),
        ('AUDIENCIA', 'Audiência'),
        ('REUNIAO', 'Reunião'),
        ('PRAZO', 'Prazo Processual'),
        ('TAREFA', 'Tarefa'),
        ('OUTRO', 'Outro')
    ]

    STATUS = [
        ('AGENDADO', 'Agendado'),
        ('CONFIRMADO', 'Confirmado'),
        ('CANCELADO', 'Cancelado'),
        ('CONCLUIDO', 'Concluído'),
        ('REMARCADO', 'Remarcado')
    ]

    calendario = models.ForeignKey(Calendario, on_delete=models.CASCADE, related_name='eventos')
    titulo = models.CharField(max_length=300)
    descricao = models.TextField(blank=True)
    tipo = models.CharField(max_length=20, choices=TIPOS_EVENTO, default='CONSULTA')
    status = models.CharField(max_length=20, choices=STATUS, default='AGENDADO')

    # Data/Hora
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField()
    dia_inteiro = models.BooleanField(default=False)
    recorrente = models.BooleanField(default=False)
    regra_recorrencia = models.CharField(max_length=200, blank=True, help_text="Ex: FREQ=WEEKLY;BYDAY=MO,WE,FR")

    # Localização
    local = models.CharField(max_length=300, blank=True)
    local_online = models.BooleanField(default=False)
    link_reuniao = models.URLField(blank=True, help_text="Google Meet, Zoom, etc")

    # Participantes
    criado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='eventos_criados')
    participantes = models.ManyToManyField(User, through='Participante', related_name='eventos', blank=True)

    # Relacionamentos
    cliente = models.ForeignKey('crm.Cliente', on_delete=models.SET_NULL, null=True, blank=True, related_name='eventos')
    processo = models.CharField(max_length=100, blank=True, help_text="Número do processo")

    # Lembretes
    lembrete_email = models.BooleanField(default=True)
    lembrete_sms = models.BooleanField(default=False)
    lembrete_whatsapp = models.BooleanField(default=True)
    minutos_antes_lembrete = models.IntegerField(default=30, help_text="Minutos antes para enviar lembrete")

    # Integração
    google_event_id = models.CharField(max_length=200, blank=True)

    # Metadata
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    cancelado_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['data_inicio']
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'

    def __str__(self):
        return f"{self.titulo} - {self.data_inicio.strftime('%d/%m/%Y %H:%M')}"

    def duracao_minutos(self):
        """Retorna duração em minutos"""
        delta = self.data_fim - self.data_inicio
        return int(delta.total_seconds() / 60)

    def is_hoje(self):
        """Verifica se é hoje"""
        return self.data_inicio.date() == timezone.now().date()

    def is_amanha(self):
        """Verifica se é amanhã"""
        amanha = timezone.now().date() + timedelta(days=1)
        return self.data_inicio.date() == amanha

    def is_proximo(self):
        """Verifica se está próximo (nas próximas 2 horas)"""
        agora = timezone.now()
        daqui_2h = agora + timedelta(hours=2)
        return agora <= self.data_inicio <= daqui_2h

    def cancelar(self, motivo: str = None):
        """Cancela evento"""
        self.status = 'CANCELADO'
        self.cancelado_em = timezone.now()
        self.save()

        # Notificar participantes
        for participante in self.participantes.all():
            # TODO: Enviar notificação
            pass


class Participante(models.Model):
    """Participantes de eventos"""

    STATUS_CONFIRMACAO = [
        ('PENDENTE', 'Pendente'),
        ('CONFIRMADO', 'Confirmado'),
        ('RECUSADO', 'Recusado'),
        ('TALVEZ', 'Talvez')
    ]

    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='confirmacoes')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CONFIRMACAO, default='PENDENTE')
    obrigatorio = models.BooleanField(default=False)

    confirmado_em = models.DateTimeField(null=True, blank=True)
    notificado = models.BooleanField(default=False)

    class Meta:
        unique_together = ['evento', 'usuario']

    def confirmar(self):
        """Confirma participação"""
        self.status = 'CONFIRMADO'
        self.confirmado_em = timezone.now()
        self.save()

    def recusar(self):
        """Recusa participação"""
        self.status = 'RECUSADO'
        self.save()


class DisponibilidadeAdvogado(models.Model):
    """Disponibilidade semanal do advogado"""

    DIAS_SEMANA = [
        (0, 'Segunda-feira'),
        (1, 'Terça-feira'),
        (2, 'Quarta-feira'),
        (3, 'Quinta-feira'),
        (4, 'Sexta-feira'),
        (5, 'Sábado'),
        (6, 'Domingo')
    ]

    advogado = models.ForeignKey(User, on_delete=models.CASCADE, related_name='disponibilidades')
    dia_semana = models.IntegerField(choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ['dia_semana', 'hora_inicio']
        unique_together = ['advogado', 'dia_semana', 'hora_inicio']

    def __str__(self):
        return f"{self.advogado.username} - {self.get_dia_semana_display()} {self.hora_inicio}-{self.hora_fim}"


class BloqueioAgenda(models.Model):
    """Bloqueios de agenda (férias, feriados, etc)"""

    advogado = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bloqueios')
    motivo = models.CharField(max_length=200)
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField()
    dia_inteiro = models.BooleanField(default=True)

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['data_inicio']

    def __str__(self):
        return f"{self.advogado.username} - {self.motivo}"


class ConfiguracaoAgenda(models.Model):
    """Configurações de agenda do usuário"""

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='config_agenda')

    # Horários padrão
    hora_inicio_expediente = models.TimeField(default='09:00')
    hora_fim_expediente = models.TimeField(default='18:00')
    duracao_padrao_consulta = models.IntegerField(default=60, help_text="Minutos")
    intervalo_entre_consultas = models.IntegerField(default=15, help_text="Minutos")

    # Notificações
    notificar_email = models.BooleanField(default=True)
    notificar_whatsapp = models.BooleanField(default=True)
    notificar_push = models.BooleanField(default=True)

    # Agendamento online
    permitir_agendamento_online = models.BooleanField(default=False)
    antecedencia_minima_horas = models.IntegerField(default=24)
    antecedencia_maxima_dias = models.IntegerField(default=30)

    # Fuso horário
    timezone = models.CharField(max_length=100, default='America/Sao_Paulo')

    class Meta:
        verbose_name = 'Configuração de Agenda'
        verbose_name_plural = 'Configurações de Agenda'

    def __str__(self):
        return f"Config - {self.usuario.username}"


# ==================== FUNÇÕES AUXILIARES ====================

def verificar_disponibilidade(advogado: User, data_inicio, data_fim):
    """
    Verifica se advogado está disponível no horário

    Returns:
        (bool, str): (disponível, motivo se não disponível)
    """
    # Verificar se já tem evento no horário
    conflitos = Evento.objects.filter(
        calendario__proprietario=advogado,
        data_inicio__lt=data_fim,
        data_fim__gt=data_inicio,
        status__in=['AGENDADO', 'CONFIRMADO']
    )

    if conflitos.exists():
        return False, f"Já existe {conflitos.count()} evento(s) agendado(s) neste horário"

    # Verificar bloqueios
    bloqueios = BloqueioAgenda.objects.filter(
        advogado=advogado,
        data_inicio__lte=data_fim,
        data_fim__gte=data_inicio
    )

    if bloqueios.exists():
        return False, f"Bloqueio: {bloqueios.first().motivo}"

    # Verificar disponibilidade semanal
    dia_semana = data_inicio.weekday()
    hora_inicio = data_inicio.time()

    disponibilidades = DisponibilidadeAdvogado.objects.filter(
        advogado=advogado,
        dia_semana=dia_semana,
        ativo=True
    )

    if not disponibilidades.exists():
        return False, "Advogado não trabalha neste dia"

    # Verificar se está dentro do horário de trabalho
    dentro_horario = any(
        d.hora_inicio <= hora_inicio < d.hora_fim
        for d in disponibilidades
    )

    if not dentro_horario:
        return False, "Fora do horário de expediente"

    return True, "Disponível"


def sugerir_horarios(advogado: User, data, duracao_minutos=60):
    """
    Sugere horários disponíveis para um dia

    Args:
        advogado: Usuário advogado
        data: Data para buscar horários
        duracao_minutos: Duração desejada em minutos

    Returns:
        List de horários disponíveis (datetime)
    """
    dia_semana = data.weekday()

    # Buscar disponibilidades do dia
    disponibilidades = DisponibilidadeAdvogado.objects.filter(
        advogado=advogado,
        dia_semana=dia_semana,
        ativo=True
    )

    if not disponibilidades.exists():
        return []

    horarios_disponiveis = []

    for disp in disponibilidades:
        hora_atual = disp.hora_inicio

        while hora_atual < disp.hora_fim:
            data_hora = timezone.make_aware(
                timezone.datetime.combine(data, hora_atual)
            )
            data_fim = data_hora + timedelta(minutes=duracao_minutos)

            disponivel, _ = verificar_disponibilidade(advogado, data_hora, data_fim)

            if disponivel:
                horarios_disponiveis.append(data_hora)

            # Próximo slot (intervalo de 30min)
            hora_atual = (timezone.datetime.combine(data, hora_atual) + timedelta(minutes=30)).time()

    return horarios_disponiveis
