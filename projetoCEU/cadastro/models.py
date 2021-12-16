from django.db import models
from django.utils import timezone
from django import forms


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
    coordenador = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='coordenador')
    professor_2 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING,
                                    related_name='professor_2', blank=True, null=True)
    professor_3 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING,
                                    related_name='professor_3', blank=True, null=True)
    professor_4 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING,
                                    related_name='professor_4', blank=True, null=True)
    hora_entrada = models.TimeField()
    atividade_1 = models.ForeignKey(Atividades, on_delete=models.DO_NOTHING, related_name='atividade_1')
    hora_atividade_1 = models.TimeField()
    prf_1_atv_1 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='prf_1_atv_1')
    prf_2_atv_1 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='prf_2_atv_1',
                                    blank=True, null=True)
    prf_3_atv_1 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='prf_3_atv_1',
                                    blank=True, null=True)
    prf_4_atv_1 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='prf_4_atv_1',
                                    blank=True, null=True)
    atividade_2 = models.ForeignKey(Atividades, on_delete=models.DO_NOTHING,
                                    related_name='atividade_2', blank=True, null=True)
    hora_atividade_2 = models.TimeField(blank=True, null=True)
    prf_1_atv_2 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='prf_1_atv_2',
                                    blank=True, null=True)
    prf_2_atv_2 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='prf_2_atv_2',
                                    blank=True, null=True)
    prf_3_atv_2 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='prf_3_atv_2',
                                    blank=True, null=True)
    prf_4_atv_2 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='prf_4_atv_2',
                                    blank=True, null=True)
    atividade_3 = models.ForeignKey(Atividades, on_delete=models.DO_NOTHING,
                                    related_name='atividade_3', blank=True, null=True)
    hora_atividade_3 = models.TimeField(blank=True, null=True)
    prf_1_atv_3 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='prf_1_atv_3',
                                    blank=True, null=True)
    prf_2_atv_3 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='prf_2_atv_3',
                                    blank=True, null=True)
    prf_3_atv_3 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='prf_3_atv_3',
                                    blank=True, null=True)
    prf_4_atv_3 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='prf_4_atv_3',
                                    blank=True, null=True)
    atividade_4 = models.ForeignKey(Atividades, on_delete=models.DO_NOTHING,
                                    related_name='atividade_4', blank=True, null=True)
    hora_atividade_4 = models.TimeField(blank=True, null=True)
    prf_1_atv_4 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='prf_1_atv_4',
                                    blank=True, null=True)
    prf_2_atv_4 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='prf_2_atv_4',
                                    blank=True, null=True)
    prf_3_atv_4 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='prf_3_atv_4',
                                    blank=True, null=True)
    prf_4_atv_4 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='prf_4_atv_4',
                                    blank=True, null=True)
    atividade_5 = models.ForeignKey(Atividades, on_delete=models.DO_NOTHING,
                                    related_name='atividade_5', blank=True, null=True)
    hora_atividade_5 = models.TimeField(blank=True, null=True)
    prf_1_atv_5 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='prf_1_atv_5',
                                    blank=True, null=True)
    prf_2_atv_5 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='prf_2_atv_5',
                                    blank=True, null=True)
    prf_3_atv_5 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='prf_3_atv_5',
                                    blank=True, null=True)
    prf_4_atv_5 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='prf_4_atv_5',
                                    blank=True, null=True)
    relatorio = models.TextField(max_length=400, default='Atividades realizadas com sucesso')


class FormularioOrdem(forms.ModelForm):
    class Meta:
        model = OrdemDeServico
        exclude = ('responsaveis', 'serie', 'coordenador_peraltas')
