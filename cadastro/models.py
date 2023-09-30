import json
from datetime import datetime
from json import JSONEncoder

from django.db import models
from django import forms
from django.forms import DateField

from ceu.models import Professores
from peraltas.models import Monitor

# ----------------------- Model para cadsatro de atendimento ao público ----------------------------------------
from projetoCEU import settings


class RelatorioDeAtendimentoPublicoCeu(models.Model):
    tipo = models.CharField(max_length=7, default='Público', blank=True)
    participantes_previa = models.IntegerField()
    participantes_confirmados = models.IntegerField(blank=True, null=True)
    data_atendimento = models.DateField()
    equipe = models.JSONField(blank=True)  # dict{'coordenador': ID, 'professor_2': ID, 'professor_3': ID, 'professor_4': ID}
    atividades = models.JSONField(blank=True)  # dict{['atividade': ID, 'profs_ativ':[IDs], 'data_hora_ativ':, 'n_participantes':]}
    relatorio = models.TextField(max_length=400, default='Atividades realizadas com sucesso')
    data_hora_salvo = models.DateTimeField(default=datetime.now, blank=True)

    class Meta:
        verbose_name_plural = "Relatórios de atendimento ao público (CEU)"

    def __str__(self):
        return f'Relatório de atendimento do Público do dia {self.data_atendimento}'

    # ------------------------------ Funções para vizualização no template -------------------------------------
    def equipe_escalada(self):
        return list(self.equipe.values())

    def listar_atividades(self):
        print(list(self.atividades.values()))
        return list(self.atividades.values())

    def coordenador_escalado(self):
        equipe = [Professores.objects.get(pk=id_professor).usuario.get_full_name() for id_professor in self.equipe.values()]
        return equipe[0]

    def nome_professores(self):
        equipe = [Professores.objects.get(pk=id_professor).usuario.get_full_name() for id_professor in self.equipe.values()]

        return ', '.join(equipe)


# --------------------------------------------------------------------------------------------------------------
# --------------------------- Model para cadsatro do atendimento com colégio -----------------------------------
# --------------------------------------------------------------------------------------------------------------
class RelatorioDeAtendimentoColegioCeu(models.Model):
    tipo = models.CharField(max_length=7, default='Colégio', blank=True)
    instituicao = models.CharField(max_length=255)
    participantes_previa = models.IntegerField()
    participantes_confirmados = models.IntegerField(blank=True, null=True)
    check_in = models.DateTimeField(blank=True)
    check_out = models.DateTimeField(blank=True)
    responsaveis = models.IntegerField(blank=True, null=True)
    serie = models.CharField(max_length=100, blank=True)
    coordenador_peraltas = models.ForeignKey(Monitor, on_delete=models.DO_NOTHING)
    equipe = models.JSONField(blank=True)  # dict{'coordenador':, 'professor_2':, 'professor_3':, 'professor_4':}
    atividades = models.JSONField(blank=True)  # dict{['atividade':, 'profs_ativ':[], 'data_hora_ativ':,
    # 'n_participantes':]}
    locacoes = models.JSONField(blank=True, null=True)  # dict{['local':, 'profs_acompanhando':, 'data_hora_entrada':,
    # 'data_hora_saida':, 'soma_horas':}]}
    horas_totais_locacoes = models.DurationField(blank=True, null=True)
    relatorio = models.TextField(max_length=400, default='Atividades realizadas com sucesso')
    data_hora_salvo = models.DateTimeField(default=datetime.now, blank=True)
    ficha_avaliacao = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Relatórios de atendimento com colégio (CEU)"

    def __str__(self):
        return f'Relatório de atendimento do colégio do dia {self.instituicao}'

    # ------------------------------ Funções para vizualização no template -------------------------------------
    def equipe_escalada(self):
        professores = []
        for id_professor in self.equipe.values():
            professor = Professores.objects.get(id=id_professor)
            professores.append(professor.usuario.first_name)

        return ', '.join(professores)

    def coordenador_escalado(self):
        coordenador = Professores.objects.get(id=self.equipe['coordenador'])
        print(coordenador.usuario.first_name)
        return coordenador.usuario.first_name


# --------------------------------------------------------------------------------------------------------------
# --------------------------- Model para cadsatro do atendimento com empresa -----------------------------------
# --------------------------------------------------------------------------------------------------------------
class RelatorioDeAtendimentoEmpresaCeu(models.Model):
    tipo = models.CharField(max_length=7, default='Empresa', blank=True)
    instituicao = models.CharField(max_length=255)
    participantes_previa = models.IntegerField()
    participantes_confirmados = models.IntegerField(blank=True, null=True)
    check_in = models.DateTimeField()
    check_out = models.DateTimeField()
    coordenador_peraltas = models.ForeignKey(Monitor, on_delete=models.DO_NOTHING)
    equipe = models.JSONField(blank=True)  # dict{'coordenador':, 'professor_2':, 'professor_3':, 'professor_4':}
    atividades = models.JSONField(blank=True, null=True)  # dict{['atividade':, 'profs_ativ':[], 'data_hora_ativ':,
    # 'n_participantes':]}
    locacoes = models.JSONField(blank=True, null=True)  # dict{['local':, 'professor':, 'data_hora_entrada':,
    # 'data_hora_saida':, 'soma_horas':, 'participantes:}]}
    horas_totais_locacoes = models.DurationField(blank=True, null=True)
    data_hora_salvo = models.DateTimeField(default=datetime.now, blank=True)
    relatorio = models.TextField(max_length=400, default='Atividades realizadas com sucesso')

    class Meta:
        verbose_name_plural = "Relatórios de atendimento à empresa (CEU)"

    def __str__(self):
        return f'Relatório de atendimento à empresa do dia {self.instituicao}'

    # ------------------------------ Funções para vizualização no template -----------------------------------------
    def equipe_escalada(self):
        professores = []
        for id_professor in self.equipe.values():
            professor = Professores.objects.get(id=id_professor)
            professores.append(professor.usuario.first_name)

        return ', '.join(professores)

    def coordenador_escalado(self):
        coordenador = Professores.objects.get(id=self.equipe['coordenador'])
        print(coordenador.usuario.first_name)
        return coordenador.usuario.first_name


# ---------------------------------------------- Forms -----------------------------------------------------------------
class RelatorioPublico(forms.ModelForm):
    class Meta:
        model = RelatorioDeAtendimentoPublicoCeu
        exclude = ()

        widgets = {
            'participantes_previa': forms.NumberInput(attrs={'placeholder': 'Prévia'}),
            'participantes_confirmados': forms.NumberInput(attrs={'placeholder': 'Confirmados'}),
            'data_atendimento': forms.DateInput(attrs={'type': 'date'})
        }


class RelatorioColegio(forms.ModelForm):
    class Meta:
        model = RelatorioDeAtendimentoColegioCeu
        exclude = ()

        widgets = {'participantes_previa': forms.NumberInput(attrs={'placeholder': 'Prévia'}),
                   'participantes_confirmados': forms.NumberInput(attrs={'placeholder': 'Confirmados'}),
                   }


class RelatorioEmpresa(forms.ModelForm):
    class Meta:
        model = RelatorioDeAtendimentoEmpresaCeu
        exclude = ()

        widgets = {'instituicao': forms.TimeInput(attrs={'onClick': 'verificarObrigatoriedade()'}),
                   'participantes_previa': forms.NumberInput(attrs={'placeholder': 'Prévia'}),
                   'participantes_confirmados': forms.NumberInput(attrs={'placeholder': 'Confirmados'}),
                   }
