from django.db import models
from django.forms import forms
from django.utils import timezone


class Professores(models.Model):
    nome = models.CharField(max_length=20)
    diarista = models.BooleanField(default=False)

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


class Locaveis(models.Model):
    locaveis = models.CharField(max_length=100)


class OrdemDeServico(models.Model):
    tipo = models.ForeignKey(Tipo, on_delete=models.DO_NOTHING)
    instituicao = models.CharField(max_length=255)
    participantes_previa = models.IntegerField()
    participantes_confirmados = models.IntegerField(blank=True, null=True)
    responsaveis = models.IntegerField(blank=True, null=True)
    serie = models.CharField(max_length=100, blank=True)
    coordenador_peraltas = models.CharField(max_length=100, blank=True)
    data_atendimento = models.DateField(default=timezone.now)
    coordenador = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='coordenador')
    professor_2 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING,
                                    related_name='professor_2', blank=True, null=True)
    professor_3 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING,
                                    related_name='professor_3', blank=True, null=True)
    professor_4 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING,
                                    related_name='professor_4', blank=True, null=True)
    hora_entrada = models.TimeField(blank=True, null=True)

    # ------------------------------------------ CAMPOS DA ATIVIDADE 1 -----------------------------------------
    atividade_1 = models.ForeignKey(Atividades, on_delete=models.DO_NOTHING, blank=True, Null=True,
                                    related_name='atividade_1')
    hora_atividade_1 = models.TimeField()
    professores_atividade_1 = models.CharField(max_length=255)
    locacao_1 = models.ForeignKey(Locaveis, on_delete=models.DO_NOTHING, blank=True, null=True)
    horarios_locacao_1 = models.TimeField(blank=True, null=True)
    professor_locacao_1 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='prof_locacao_1',
                                            blank=True, null=True)
    soma_horas_1 = models.DurationField(blank=True, null=True)

    # ------------------------------------------ CAMPOS DA ATIVIDADE 2 -----------------------------------------
    atividade_2 = models.ForeignKey(Atividades, on_delete=models.DO_NOTHING,
                                    related_name='atividade_2', blank=True, null=True)
    hora_atividade_2 = models.TimeField(blank=True, null=True)
    professores_atividade_2 = models.CharField(max_length=255)
    locacao_2 = models.ForeignKey(Locaveis, on_delete=models.DO_NOTHING, blank=True, null=True)
    horarios_locacao_2 = models.TimeField(blank=True, null=True)
    professor_locacao_2 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='prof_locacao_2',
                                            blank=True, null=True)
    soma_horas_2 = models.DurationField(blank=True, null=True)

    # ------------------------------------------ CAMPOS DA ATIVIDADE 3 -----------------------------------------
    atividade_3 = models.ForeignKey(Atividades, on_delete=models.DO_NOTHING,
                                    related_name='atividade_3', blank=True, null=True)
    hora_atividade_3 = models.TimeField(blank=True, null=True)
    professores_atividade_3 = models.CharField(max_length=255)
    locacao_3 = models.ForeignKey(Locaveis, on_delete=models.DO_NOTHING, blank=True, null=True)
    horarios_locacao_3 = models.TimeField(blank=True, null=True)
    professor_locacao_3 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='prof_locacao_3',
                                            blank=True, null=True)
    soma_horas_3 = models.DurationField(blank=True, null=True)

    # ------------------------------------------ CAMPOS DA ATIVIDADE 4 -----------------------------------------
    atividade_4 = models.ForeignKey(Atividades, on_delete=models.DO_NOTHING,
                                    related_name='atividade_4', blank=True, null=True)
    hora_atividade_4 = models.TimeField(blank=True, null=True)
    professores_atividade_4 = models.CharField(max_length=255)
    locacao_4 = models.ForeignKey(Locaveis, on_delete=models.DO_NOTHING, blank=True, null=True)
    horarios_locacao_4 = models.TimeField(blank=True, null=True)
    professor_locacao_4 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='prof_locacao_4',
                                            blank=True, null=True)

    # ------------------------------------------ CAMPOS DA ATIVIDADE 5 -----------------------------------------
    atividade_5 = models.ForeignKey(Atividades, on_delete=models.DO_NOTHING,
                                    related_name='atividade_5', blank=True, null=True)
    hora_atividade_5 = models.TimeField(blank=True, null=True)
    professores_atividade_5 = models.CharField(max_length=255)
    locacao_5 = models.ForeignKey(Locaveis, on_delete=models.DO_NOTHING, blank=True, null=True)
    horarios_locacao_5 = models.TimeField(blank=True, null=True)
    professor_locacao_5 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='prof_locacao_4',
                                            blank=True, null=True)

    # ------------------------------------------ FINALIZAÇÕES --------------------------------------------------
    horas_totais = models.DurationField(blank=True, null=True)
    relatorio = models.TextField(max_length=400, default='Atividades realizadas com sucesso')
    solicitado = models.BooleanField(default=False)
    entregue = models.BooleanField(default=False)

    def __str__(self):
        return f'Ordem de serviço de {self.tipo}'

