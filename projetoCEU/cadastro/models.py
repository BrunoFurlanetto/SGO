from django.db import models
from django import forms
from django.utils import timezone


class Professores(models.Model):
    nome = models.CharField(max_length=20)
    diarista = models.BooleanField(default=False)
    nota = models.FloatField(default=0.00)

    def __str__(self):
        return self.nome


class Tipo(models.Model):
    tipo = models.CharField(max_length=100)

    def __str__(self):
        return self.tipo


class Atividades(models.Model):
    atividade = models.CharField(max_length=100)
    publico = models.BooleanField(default=False)

    def __str__(self):
        return self.atividade


class Locaveis(models.Model):
    estrutura = models.CharField(max_length=100)

    def __str__(self):
        return self.estrutura


class OrdemDeServico(models.Model):
    tipo = models.ForeignKey(Tipo, on_delete=models.DO_NOTHING, blank=True, null=True)
    instituicao = models.CharField(max_length=255)
    participantes_previa = models.IntegerField()
    participantes_confirmados = models.IntegerField(blank=True, null=True)
    responsaveis = models.IntegerField(blank=True, null=True)
    serie = models.CharField(max_length=100, blank=True)
    coordenador_peraltas = models.CharField(max_length=100, blank=True)
    data_atendimento = models.DateField()
    coordenador = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='coordenador')
    professor_2 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING,
                                    related_name='professor_2', blank=True, null=True)
    professor_3 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING,
                                    related_name='professor_3', blank=True, null=True)
    professor_4 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING,
                                    related_name='professor_4', blank=True, null=True)
    hora_entrada = models.TimeField(blank=True, null=True)

    # ------------------------------------------ CAMPOS DA ATIVIDADE 1 -----------------------------------------
    atividade_1 = models.ForeignKey(Atividades, on_delete=models.DO_NOTHING,
                                    related_name='atividade_1', blank=True, null=True)
    hora_atividade_1 = models.TimeField(blank=True, null=True)
    professores_atividade_1 = models.CharField(max_length=255, blank=True)
    locacao_1 = models.ForeignKey(Locaveis, on_delete=models.DO_NOTHING, blank=True, null=True,
                                  related_name='locacao_1')
    horarios_locacao_1 = models.CharField(max_length=200, blank=True, null=True)
    professores_locacao_1 = models.CharField(max_length=255, blank=True, null=True)
    soma_horas_1 = models.DurationField(blank=True, null=True)

    # ------------------------------------------ CAMPOS DA ATIVIDADE 2 -----------------------------------------
    atividade_2 = models.ForeignKey(Atividades, on_delete=models.DO_NOTHING,
                                    related_name='atividade_2', blank=True, null=True)
    hora_atividade_2 = models.TimeField(blank=True, null=True)
    professores_atividade_2 = models.CharField(max_length=255, blank=True)
    locacao_2 = models.ForeignKey(Locaveis, on_delete=models.DO_NOTHING, blank=True, null=True,
                                  related_name='locacao_2')
    horarios_locacao_2 = models.CharField(max_length=200, blank=True, null=True)
    professores_locacao_2 = models.CharField(max_length=255, blank=True, null=True)
    soma_horas_2 = models.DurationField(blank=True, null=True)

    # ------------------------------------------ CAMPOS DA ATIVIDADE 3 -----------------------------------------
    atividade_3 = models.ForeignKey(Atividades, on_delete=models.DO_NOTHING,
                                    related_name='atividade_3', blank=True, null=True)
    hora_atividade_3 = models.TimeField(blank=True, null=True)
    professores_atividade_3 = models.CharField(max_length=255, blank=True)
    locacao_3 = models.ForeignKey(Locaveis, on_delete=models.DO_NOTHING, blank=True, null=True,
                                  related_name='locacao_3')
    horarios_locacao_3 = models.TimeField(max_length=200, blank=True, null=True)
    professores_locacao_3 = models.CharField(max_length=255, blank=True, null=True)
    soma_horas_3 = models.DurationField(blank=True, null=True)

    # ------------------------------------------ CAMPOS DA ATIVIDADE 4 -----------------------------------------
    atividade_4 = models.ForeignKey(Atividades, on_delete=models.DO_NOTHING,
                                    related_name='atividade_4', blank=True, null=True)
    hora_atividade_4 = models.TimeField(blank=True, null=True)
    professores_atividade_4 = models.CharField(max_length=255, blank=True)

    # ------------------------------------------ CAMPOS DA ATIVIDADE 5 -----------------------------------------
    atividade_5 = models.ForeignKey(Atividades, on_delete=models.DO_NOTHING,
                                    related_name='atividade_5', blank=True, null=True)
    hora_atividade_5 = models.TimeField(blank=True, null=True)
    professores_atividade_5 = models.CharField(max_length=255, blank=True)

    # ------------------------------------------ FINALIZAÇÕES --------------------------------------------------
    horas_totais = models.DurationField(blank=True, null=True)
    relatorio = models.TextField(max_length=400, default='Atividades realizadas com sucesso')
    solicitado = models.BooleanField(default=False)
    entregue = models.BooleanField(default=False)

    def __str__(self):
        return f'Ordem de serviço de {self.tipo}'


class OrdemDeServicoPublico(forms.ModelForm):
    class Meta:
        model = OrdemDeServico
        exclude = ('instituicao', 'responsaveis', 'serie', 'coordenador_peraltas',
                   'locacao_1', 'horarios_locacao_1', 'professores_locacao_1', 'soma_horas_1',
                   'locacao_2', 'horarios_locacao_2', 'professores_locacao_2', 'soma_horas_2',
                   'locacao_3', 'horarios_locacao_3', 'professores_locacao_3', 'soma_horas_3',
                   'horas_totais', 'solicitado', 'entregue')

        widgets = {'participantes_previa': forms.NumberInput(attrs={'placeholder': 'Prévia'}),
                   'participantes_confirmados': forms.NumberInput(attrs={'placeholder': 'Confirmados'}),
                   'data_atendimento': forms.DateTimeInput(attrs={'type': 'date'}),
                   'hora_entrada': forms.TimeInput(attrs={'type': 'time'}),
                   }


class OrdemDeServicoColegio(forms.ModelForm):
    class Meta:
        model = OrdemDeServico
        exclude = ()

        widgets = {'participantes_previa': forms.NumberInput(attrs={'placeholder': 'Prévia'}),
                   'participantes_confirmados': forms.NumberInput(attrs={'placeholder': 'Confirmados'}),
                   'data_atendimento': forms.DateTimeInput(attrs={'type': 'date'}),
                   'hora_entrada': forms.TimeInput(attrs={'type': 'time'}),
                   'hora_atividade_1': forms.TimeInput(attrs={'type': 'time'}),
                   'hora_atividade_2': forms.TimeInput(attrs={'type': 'time'}),
                   'hora_atividade_3': forms.TimeInput(attrs={'type': 'time'}),
                   'hora_atividade_4': forms.TimeInput(attrs={'type': 'time'}),
                   'hora_atividade_5': forms.TimeInput(attrs={'type': 'time'}),
                   'coordenador': forms.Select(attrs={'onchange': 'equipe(this)'}),
                   'professor_2': forms.Select(attrs={'onchange': 'equipe(this)'}),
                   'professor_3': forms.Select(attrs={'onchange': 'equipe(this)'}),
                   'professor_4': forms.Select(attrs={'onchange': 'equipe(this)'}),
                   }


class OrdemDeServicoEmpresa(forms.ModelForm):
    class Meta:
        model = OrdemDeServico
        exclude = ('responsaveis', 'serie', 'hora_entrada',
                   'atividade_4', 'hora_atividade_4', 'professores_atividade_4',
                   'atividade_5', 'hora_atividade_5', 'professores_atividade_5',
                   'solicitado', 'entregue')
