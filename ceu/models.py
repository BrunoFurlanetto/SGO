from django.contrib.auth.models import User
from django.db import models
from django import forms


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
    a_definir = models.BooleanField(default=False)
    sem_atividade = models.BooleanField(default=False)

    def __str__(self):
        return self.atividade


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
