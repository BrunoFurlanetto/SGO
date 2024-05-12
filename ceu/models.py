from django.contrib.auth.models import User
from django.db import models


class Professores(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    telefone = models.CharField(max_length=11)
    diarista = models.BooleanField(default=False)
    nota = models.FloatField(default=0.00)
    n_avaliacoes = models.IntegerField(default=0)

    def __str__(self):
        return self.usuario.get_full_name()

    def nome_completo(self):
        return self.usuario.get_full_name()


# class TipoAtividadesCeu(models.Model):
#     tipo_atividade = models.CharField(max_length=255, verbose_name='Tipo de Atividade')
#
#     def str_tipo_atividade(self):
#         return self.tipo_atividade
#
#     def __str__(self):
#         return self.tipo_atividade


class Estruturas(models.Model):
    estrutura = models.CharField(max_length=100)
    locavel = models.BooleanField(default=False)
    lotacao = models.IntegerField()

    def __str__(self):
        return self.estrutura


class Locaveis(models.Model):
    local = models.OneToOneField(Estruturas, on_delete=models.CASCADE, unique=True)

    def __str__(self):
        return self.local.estrutura


class Limitacoes(models.Model):
    limitacao = models.CharField(max_length=100)

    def __str__(self):
        return self.limitacao


class Atividades(models.Model):
    atividade = models.CharField(max_length=100, verbose_name='Nome da atividade')
    local_da_atividade = models.ForeignKey(Estruturas, on_delete=models.DO_NOTHING, related_name='local')
    numero_de_participantes_minimo = models.IntegerField()
    numero_de_participantes_maximo = models.IntegerField()
    duracao = models.DurationField()
    nota = models.FloatField(default=0.00)
    n_avaliacoes = models.IntegerField(default=0)
    limitacao = models.ManyToManyField(Limitacoes, blank=True)
    publico = models.BooleanField(default=False)
    valor = models.DecimalField(decimal_places=2, max_digits=5, default=0.00)
    intencao_atividade = models.ManyToManyField('peraltas.IntencaoAtividade', blank=True)
    disciplina_primaria = models.ForeignKey(
        'peraltas.Disciplinas',
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name='disciplina_primaria_ceu',
        verbose_name='Disciplina Primaria',
    )
    disciplinas = models.ManyToManyField(
        'peraltas.Disciplinas',
        blank=True,
        verbose_name='Disciplnas trabalhadas',
        related_name='disciplinas_secundarias_ceu',
    )
    serie = models.ManyToManyField('peraltas.PerfilsParticipantes', blank=True)
    tipo_pacote = models.ManyToManyField('peraltas.ProdutosPeraltas', blank=True)

    def __str__(self):
        return self.atividade

    def informacoes_atividade(self):
        return {
            'id': self.id,
            'nome': self.atividade,
            'disciplina_primaria': self.disciplina_primaria.disciplina,
            'cor': self.disciplina_primaria.cor,
            'intencao': 'estudo',
            'series': ', '.join([serie.ano for serie in self.serie.all()]),
            'pacotes': ', '.join([pacote.produto for pacote in self.tipo_pacote.all()]),
        }


class Valores(models.Model):
    tipo = models.CharField(max_length=100)
    valor_pago = models.FloatField(default=0.00)


class ReembolsosProfessores(models.Model):
    meses = (
        (1, 'janeiro'), (2, 'Fevereiro'), (3, 'Março'),
        (4, 'Abril'), (5, 'Maio'), (6, 'Junho'),
        (7, 'Julho'), (8, 'Agosto'), (9, 'Setembro'),
        (10, 'Outubro'), (11, 'Novemmbro'), (12, 'Dezembro')
    )

    usuario_professor = models.ForeignKey(Professores, on_delete=models.DO_NOTHING)
    mes_referente = models.IntegerField(choices=meses)
    ano_referente = models.IntegerField()
    valores = models.CharField(max_length=255)
    valor_reembolso = models.FloatField()
    comprovante_reembolso = models.FileField(upload_to=f'comprovantes/{usuario_professor}/%Y/%m')
