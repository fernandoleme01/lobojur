"""
Sistema Kanban - Gestão de Tarefas e Processos
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Board(models.Model):
    """Quadro Kanban"""

    BOARD_TYPES = [
        ('PESSOAL', 'Tarefas Pessoais'),
        ('PROCESSOS', 'Gestão de Processos'),
        ('VENDAS', 'Pipeline de Vendas'),
        ('PROJETOS', 'Projetos'),
        ('CUSTOMIZADO', 'Customizado')
    ]

    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    tipo = models.CharField(max_length=20, choices=BOARD_TYPES, default='PESSOAL')
    cor = models.CharField(max_length=7, default='#3B82F6')  # Hex color
    icone = models.CharField(max_length=50, default='📋')

    # Permissões
    criado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='boards_criados')
    membros = models.ManyToManyField(User, related_name='boards', blank=True)
    publico = models.BooleanField(default=False)

    # Metadata
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    arquivado = models.BooleanField(default=False)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Quadro Kanban'
        verbose_name_plural = 'Quadros Kanban'

    def __str__(self):
        return f"{self.icone} {self.nome}"


class Column(models.Model):
    """Coluna do Kanban"""

    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='colunas')
    nome = models.CharField(max_length=100)
    cor = models.CharField(max_length=7, default='#E5E7EB')
    ordem = models.IntegerField(default=0)
    limite_wip = models.IntegerField(null=True, blank=True, help_text="Limite de Work in Progress")

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['ordem']
        unique_together = ['board', 'ordem']

    def __str__(self):
        return f"{self.board.nome} - {self.nome}"

    def get_total_cards(self):
        """Total de cards na coluna"""
        return self.cards.filter(arquivado=False).count()

    def is_wip_exceeded(self):
        """Verifica se excedeu limite WIP"""
        if self.limite_wip:
            return self.get_total_cards() > self.limite_wip
        return False


class Card(models.Model):
    """Card/Tarefa do Kanban"""

    PRIORIDADES = [
        ('BAIXA', '🟢 Baixa'),
        ('MEDIA', '🟡 Média'),
        ('ALTA', '🟠 Alta'),
        ('URGENTE', '🔴 Urgente')
    ]

    coluna = models.ForeignKey(Column, on_delete=models.CASCADE, related_name='cards')
    titulo = models.CharField(max_length=300)
    descricao = models.TextField(blank=True)

    # Prioridade e Status
    prioridade = models.CharField(max_length=10, choices=PRIORIDADES, default='MEDIA')
    ordem = models.IntegerField(default=0)
    progresso = models.IntegerField(default=0, help_text="Progresso em %")

    # Responsáveis
    responsavel = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cards_responsavel'
    )
    participantes = models.ManyToManyField(User, related_name='cards_participante', blank=True)

    # Prazos
    data_inicio = models.DateField(null=True, blank=True)
    data_vencimento = models.DateField(null=True, blank=True)
    data_conclusao = models.DateTimeField(null=True, blank=True)

    # Tags e Labels
    tags = models.ManyToManyField('Tag', related_name='cards', blank=True)
    cor_label = models.CharField(max_length=7, blank=True)

    # Relacionamentos
    processo_relacionado = models.CharField(max_length=100, blank=True, help_text="Número do processo")
    cliente_relacionado = models.ForeignKey(
        'crm.Cliente',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cards'
    )

    # Metadata
    criado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cards_criados')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    arquivado = models.BooleanField(default=False)

    class Meta:
        ordering = ['ordem', '-prioridade']

    def __str__(self):
        return self.titulo

    def is_atrasado(self):
        """Verifica se está atrasado"""
        if self.data_vencimento and not self.data_conclusao:
            return timezone.now().date() > self.data_vencimento
        return False

    def dias_restantes(self):
        """Calcula dias restantes"""
        if self.data_vencimento and not self.data_conclusao:
            delta = self.data_vencimento - timezone.now().date()
            return delta.days
        return None

    def marcar_concluido(self):
        """Marca card como concluído"""
        self.data_conclusao = timezone.now()
        self.progresso = 100
        self.save()


class Tag(models.Model):
    """Tags para categorização"""

    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='tags')
    nome = models.CharField(max_length=50)
    cor = models.CharField(max_length=7, default='#3B82F6')

    class Meta:
        unique_together = ['board', 'nome']

    def __str__(self):
        return self.nome


class Checklist(models.Model):
    """Checklist dentro de um card"""

    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='checklists')
    titulo = models.CharField(max_length=200)
    ordem = models.IntegerField(default=0)

    class Meta:
        ordering = ['ordem']

    def __str__(self):
        return f"{self.card.titulo} - {self.titulo}"

    def get_progresso(self):
        """Calcula progresso do checklist"""
        total = self.itens.count()
        if total == 0:
            return 0
        concluidos = self.itens.filter(concluido=True).count()
        return int((concluidos / total) * 100)


class ChecklistItem(models.Model):
    """Item de checklist"""

    checklist = models.ForeignKey(Checklist, on_delete=models.CASCADE, related_name='itens')
    texto = models.CharField(max_length=300)
    concluido = models.BooleanField(default=False)
    ordem = models.IntegerField(default=0)
    responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['ordem']

    def __str__(self):
        status = "✅" if self.concluido else "⬜"
        return f"{status} {self.texto}"


class Comentario(models.Model):
    """Comentários em cards"""

    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    texto = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)
    editado_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.autor.username} - {self.texto[:50]}"


class Anexo(models.Model):
    """Anexos em cards"""

    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='anexos')
    arquivo = models.FileField(upload_to='kanban/anexos/%Y/%m/%d/')
    nome_original = models.CharField(max_length=300)
    tamanho = models.IntegerField(help_text="Tamanho em bytes")
    tipo_arquivo = models.CharField(max_length=100)

    enviado_por = models.ForeignKey(User, on_delete=models.CASCADE)
    enviado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-enviado_em']

    def __str__(self):
        return self.nome_original


class Atividade(models.Model):
    """Log de atividades do card"""

    TIPOS_ACAO = [
        ('CRIADO', 'Card criado'),
        ('MOVIDO', 'Movido para outra coluna'),
        ('EDITADO', 'Editado'),
        ('COMENTARIO', 'Comentário adicionado'),
        ('ANEXO', 'Anexo adicionado'),
        ('RESPONSAVEL', 'Responsável alterado'),
        ('PRAZO', 'Prazo alterado'),
        ('CONCLUIDO', 'Marcado como concluído'),
        ('ARQUIVADO', 'Arquivado')
    ]

    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='atividades')
    tipo = models.CharField(max_length=20, choices=TIPOS_ACAO)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    descricao = models.TextField()
    dados_anteriores = models.JSONField(null=True, blank=True)
    dados_novos = models.JSONField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Atividade'
        verbose_name_plural = 'Atividades'

    def __str__(self):
        return f"{self.usuario.username} - {self.tipo} - {self.criado_em}"


# ==================== TEMPLATES DE BOARDS ====================

def criar_board_processos(usuario):
    """Cria board padrão para gestão de processos"""
    board = Board.objects.create(
        nome="Gestão de Processos",
        tipo="PROCESSOS",
        icone="⚖️",
        criado_por=usuario
    )

    colunas = [
        ("📥 Novo", "#E5E7EB", 0),
        ("📋 Análise", "#DBEAFE", 1),
        ("📝 Elaboração", "#FEF3C7", 2),
        ("✍️ Revisão", "#FECACA", 3),
        ("📤 Protocolado", "#D1FAE5", 4),
        ("✅ Concluído", "#10B981", 5),
    ]

    for nome, cor, ordem in colunas:
        Column.objects.create(
            board=board,
            nome=nome,
            cor=cor,
            ordem=ordem
        )

    return board


def criar_board_vendas(usuario):
    """Cria board padrão para pipeline de vendas"""
    board = Board.objects.create(
        nome="Pipeline de Vendas",
        tipo="VENDAS",
        icone="💰",
        criado_por=usuario
    )

    colunas = [
        ("🎯 Lead", "#E5E7EB", 0, 50),
        ("📞 Contato", "#DBEAFE", 1, 30),
        ("💬 Qualificado", "#FEF3C7", 2, 20),
        ("📋 Proposta", "#FECACA", 3, 10),
        ("💰 Negociação", "#DDD6FE", 4, 5),
        ("✅ Ganho", "#10B981", 5, None),
        ("❌ Perdido", "#EF4444", 6, None),
    ]

    for dados in colunas:
        nome, cor, ordem = dados[:3]
        limite_wip = dados[3] if len(dados) > 3 else None

        Column.objects.create(
            board=board,
            nome=nome,
            cor=cor,
            ordem=ordem,
            limite_wip=limite_wip
        )

    return board
