from django.db import models
from django import forms
from ceu.models import Tipo


class RelatorioDeAtendimentoCeu(models.Model):
    tipo = models.ForeignKey(Tipo, on_delete=models.DO_NOTHING, blank=True, null=True)
    instituicao = models.CharField(max_length=255)
    participantes_previa = models.IntegerField()
    participantes_confirmados = models.IntegerField(blank=True, null=True)
    responsaveis = models.IntegerField(blank=True, null=True)
    serie = models.CharField(max_length=100, blank=True)
    coordenador_peraltas = models.CharField(max_length=100, blank=True)
    equipe = models.JSONField()  # dict{'coordenador':, 'professor_2':, 'professor_3':, 'professor_4':}
    atividades = models.JSONField()  # dict{['atividade':, 'profs_ativ':[], 'data_hora_ativ':, 'n_participantes':]}
    locacoes = models.JSONField(blank=True, null=True)  # dict{['local':, 'profs_acompanhando':, 'data_hora_entrada':,
    # 'data_hora_saida':, 'soma_horas':, 'soma_horas_total':]}
    relatorio = models.TextField(max_length=400, default='Atividades realizadas com sucesso')
    solicitado = models.BooleanField(default=False)
    entregue = models.BooleanField(default=False)

    def __str__(self):
        return f'Relatório de {self.tipo}'


class RelatorioPublico(forms.ModelForm):
    class Meta:
        model = RelatorioDeAtendimentoCeu
        exclude = ('instituicao', 'responsaveis', 'serie', 'coordenador_peraltas',
                   'locacoes', 'solicitado', 'entregue')

        widgets = {'participantes_previa': forms.NumberInput(attrs={'placeholder': 'Prévia'}),
                   'participantes_confirmados': forms.NumberInput(attrs={'placeholder': 'Confirmados'}),
                   'data_atendimento': forms.DateTimeInput(attrs={'type': 'date'}),
                   }


class RelatorioColegio(forms.ModelForm):
    class Meta:
        model = RelatorioDeAtendimentoCeu
        exclude = ()

        widgets = {'participantes_previa': forms.NumberInput(attrs={'placeholder': 'Prévia'}),
                   'participantes_confirmados': forms.NumberInput(attrs={'placeholder': 'Confirmados'}),
                   }


class RelatorioEmpresa(forms.ModelForm):
    class Meta:
        model = RelatorioDeAtendimentoCeu
        exclude = ('responsaveis', 'serie', 'solicitado', 'entregue')

        widgets = {'instituicao': forms.TimeInput(attrs={'onClick': 'verificarObrigatoriedade()'}),
                   'participantes_previa': forms.NumberInput(attrs={'placeholder': 'Prévia'}),
                   'participantes_confirmados': forms.NumberInput(attrs={'placeholder': 'Confirmados'}),
                   }
