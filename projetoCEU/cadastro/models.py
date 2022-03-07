from django.db import models
from django import forms

from peraltas.models import Monitor


# ----------------------- Model para cadsatro de atendimento ao público ----------------------------------------
class RelatorioDeAtendimentoPublicoCeu(models.Model):
    tipo = models.CharField(max_length=7, default='Público')
    participantes_previa = models.IntegerField()
    participantes_confirmados = models.IntegerField(blank=True, null=True)
    data_atendimento = models.DateField()
    equipe = models.JSONField(blank=True)  # dict{'coordenador':, 'professor_2':, 'professor_3':, 'professor_4':}
    atividades = models.JSONField(blank=True)  # dict{['atividade':, 'profs_ativ':[], 'data_hora_ativ':,
    # 'n_participantes':]}
    relatorio = models.TextField(max_length=400, default='Atividades realizadas com sucesso')

    class Meta:
        verbose_name_plural = "Relatórios de atendimento ao público (CEU)"

    def __str__(self):
        return f'Relatório de atendimento do Público do dia {self.data_atendimento}'

    # ------------------------------ Funções para vizualização no template -------------------------------------
    def equipe_escalada(self):
        professores = []
        for professor in self.equipe.values():
            professores.append(professor)

        return ', '.join(professores)
# --------------------------------------------------------------------------------------------------------------


# ------------------------ Formulario para cadastro de atendimento ao público ----------------------------------
class RelatorioPublico(forms.ModelForm):
    class Meta:
        model = RelatorioDeAtendimentoPublicoCeu
        exclude = ()

        widgets = {'participantes_previa': forms.NumberInput(attrs={'placeholder': 'Prévia'}),
                   'participantes_confirmados': forms.NumberInput(attrs={'placeholder': 'Confirmados'}),
                   'data_atendimento': forms.DateTimeInput(attrs={'type': 'date'}),
                   }


# --------------------------------------------------------------------------------------------------------------
# --------------------------- Model para cadsatro do atendimento com comlégio -----------------------------------
# --------------------------------------------------------------------------------------------------------------
class RelatorioDeAtendimentoColegioCeu(models.Model):
    tipo = models.CharField(max_length=7, default='Colégio')
    instituicao = models.CharField(max_length=255)
    participantes_previa = models.IntegerField()
    participantes_confirmados = models.IntegerField(blank=True, null=True)
    check_in = models.DateTimeField()
    check_out = models.DateTimeField()
    responsaveis = models.IntegerField(blank=True, null=True)
    serie = models.CharField(max_length=100, blank=True)
    coordenador_peraltas = models.ForeignKey(Monitor, on_delete=models.DO_NOTHING)
    equipe = models.JSONField(blank=True)  # dict{'coordenador':, 'professor_2':, 'professor_3':, 'professor_4':}
    atividades = models.JSONField(blank=True)  # dict{['atividade':, 'profs_ativ':[], 'data_hora_ativ':,
    # 'n_participantes':]}
    locacoes = models.JSONField(blank=True, null=True)  # dict{['local':, 'profs_acompanhando':, 'data_hora_entrada':,
    # 'data_hora_saida':, 'soma_horas':, 'soma_horas_total':]}
    relatorio = models.TextField(max_length=400, default='Atividades realizadas com sucesso')
    solicitado = models.BooleanField(default=False)
    entregue = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Relatórios de atendimento com colégio (CEU)"

    def __str__(self):
        return f'Relatório de atendimento do colégio do dia {self.instituicao}'

    # ------------------------------ Funções para vizualização no template -------------------------------------
    def equipe_escalada(self):
        professores = []
        for professor in self.equipe.values():
            professores.append(professor)

        return ', '.join(professores)
# --------------------------------------------------------------------------------------------------------------


# --------------------------- Formulário para cadastro de atendimento à colégio --------------------------------
class RelatorioColegio(forms.ModelForm):
    class Meta:
        model = RelatorioDeAtendimentoColegioCeu
        exclude = ()

        widgets = {'participantes_previa': forms.NumberInput(attrs={'placeholder': 'Prévia'}),
                   'participantes_confirmados': forms.NumberInput(attrs={'placeholder': 'Confirmados'}),
                   }
# --------------------------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------------------
# --------------------------- Model para cadsatro do atendimento com empresa -----------------------------------
# --------------------------------------------------------------------------------------------------------------
class RelatorioDeAtendimentoEmpresaCeu(models.Model):
    tipo = models.CharField(max_length=7, default='Empresa')
    instituicao = models.CharField(max_length=255)
    participantes_previa = models.IntegerField()
    participantes_confirmados = models.IntegerField(blank=True, null=True)
    check_in = models.DateTimeField()
    check_out = models.DateTimeField()
    coordenador_peraltas = models.ForeignKey(Monitor, on_delete=models.DO_NOTHING)
    equipe = models.JSONField(blank=True)  # dict{'coordenador':, 'professor_2':, 'professor_3':, 'professor_4':}
    atividades = models.JSONField(blank=True)  # dict{['atividade':, 'profs_ativ':[], 'data_hora_ativ':,
    # 'n_participantes':]}
    locacoes = models.JSONField(blank=True, null=True)  # dict{['local':, 'profs_acompanhando':, 'data_hora_entrada':,
    # 'data_hora_saida':, 'soma_horas':, 'soma_horas_total':]}
    relatorio = models.TextField(max_length=400, default='Atividades realizadas com sucesso')

    class Meta:
        verbose_name_plural = "Relatórios de atendimento à empresa (CEU)"

    def __str__(self):
        return f'Relatório de atendimento à empresa do dia {self.instituicao}'

    # ------------------------------ Funções para vizualização no template -----------------------------------------
    def equipe_escalada(self):
        professores = []
        for professor in self.equipe.values():
            professores.append(professor)

        return ', '.join(professores)
# --------------------------------------------------------------------------------------------------------------


# ----------------------------- Formulário para atendimento com empresa ----------------------------------------
class RelatorioEmpresa(forms.ModelForm):
    class Meta:
        model = RelatorioDeAtendimentoEmpresaCeu
        exclude = ()

        widgets = {'instituicao': forms.TimeInput(attrs={'onClick': 'verificarObrigatoriedade()'}),
                   'participantes_previa': forms.NumberInput(attrs={'placeholder': 'Prévia'}),
                   'participantes_confirmados': forms.NumberInput(attrs={'placeholder': 'Confirmados'}),
                   }
