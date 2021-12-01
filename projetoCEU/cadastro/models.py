from django.db import models
from django.utils import timezone


class Professores(models.Model):
    nome = models.CharField(max_length=20)

    def __str__(self):
        return self.nome


class Tipo(models.Model):
    tipo = models.CharField(max_length=100)

    def __str__(self):
        return self.tipo


class Atividades(models.Model):
    atividade = models.CharField(max_length=100)

    def __str__(self):
        return self.atividade


class OrdemDeServico(models.Model):
    tipo = models.ForeignKey(Tipo, on_delete=models.DO_NOTHING)
    instituicao = models.CharField(max_length=255)
    participantes_previa = models.IntegerField()
    participantes_confirmados = models.IntegerField(blank=True)
    responsaveis = models.IntegerField(blank=True, null=True)
    serie = models.CharField(max_length=100, blank=True)
    coordenador_peraltas = models.CharField(max_length=100, blank=True)
    data_atendimento = models.DateField(default=timezone.now)
    coordenador_ceu = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='coordenador')
    professor_2 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='professor2')
    professor_3 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='professor3', blank=True,
                                   null=True)
    professor_4 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='professor4', blank=True,
                                   null=True)
    atividade_1 = models.ForeignKey(Atividades, on_delete=models.DO_NOTHING)
    relatorio = models.TextField(max_length=400, default='Atividades realizadas com sucesso')
