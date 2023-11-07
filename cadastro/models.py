import json
from datetime import datetime

from django.db import models
from django import forms

from ceu.models import Professores
from peraltas.models import Monitor

from ordemDeServico.models import OrdemDeServico


class RelatorioDeAtendimentoPublicoCeu(models.Model):
    tipo = models.CharField(max_length=7, default='publico', blank=True)
    participantes_previa = models.IntegerField()
    participantes_confirmados = models.IntegerField(blank=True, null=True)
    data_atendimento = models.DateField()
    equipe = models.JSONField(
        blank=True)  # dict{'coordenador': ID, 'professor_2': ID, 'professor_3': ID, 'professor_4': ID}
    atividades = models.JSONField(
        blank=True)  # dict{['atividade': ID, 'profs_ativ':[IDs], 'data_hora_ativ':, 'n_participantes':]}
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
        equipe = [Professores.objects.get(pk=id_professor).usuario.get_full_name() for id_professor in
                  self.equipe.values()]
        return equipe[0]

    def nome_professores(self):
        equipe = [Professores.objects.get(pk=id_professor).usuario.get_full_name() for id_professor in
                  self.equipe.values()]

        return ', '.join(equipe)


# --------------------------------------------------------------------------------------------------------------
# --------------------------- Model para cadsatro do atendimento com colégio -----------------------------------
# --------------------------------------------------------------------------------------------------------------
class RelatorioDeAtendimentoColegioCeu(models.Model):
    tipo = models.CharField(max_length=7, default='colegio', blank=True)
    instituicao = models.CharField(max_length=255)
    ordem = models.ForeignKey(OrdemDeServico, on_delete=models.CASCADE)
    participantes_previa = models.IntegerField()
    participantes_confirmados = models.IntegerField(blank=True, null=True)
    check_in = models.DateTimeField(blank=True)
    check_out = models.DateTimeField(blank=True)
    responsaveis = models.IntegerField(blank=True, null=True)
    serie = models.CharField(max_length=100, blank=True)
    coordenador_peraltas = models.ManyToManyField(Monitor)
    equipe = models.JSONField(blank=True)  # dict{'coordenador':, 'professor_2':, 'professor_3':, 'professor_4':}
    atividades = models.JSONField(blank=True)  # dict{['atividade':, 'profs_ativ':[], 'data_hora_ativ':,
    # 'n_participantes':]}
    locacoes = models.JSONField(blank=True, null=True)  # dict{['local':, 'profs_acompanhando':, 'data_hora_entrada':,
    # 'data_hora_saida':, 'soma_horas':}]}
    horas_totais_locacoes = models.DurationField(blank=True, null=True)
    relatorio = models.TextField(max_length=400, default='Atividades realizadas com sucesso')
    data_hora_salvo = models.DateTimeField(default=datetime.now, blank=True)
    ficha_avaliacao = models.BooleanField(default=False)

    @staticmethod
    def dados_iniciais(ordem):
        return {
            'ordem': ordem.id,
            'instituicao': ordem.ficha_de_evento.cliente,
            'participantes_previa': ordem.n_participantes,
            'check_in': ordem.check_in,
            'check_out': ordem.check_out,
            'responsaveis': ordem.n_professores,
            'serie': ordem.serie,
            'coordenador_peraltas': ordem.monitor_responsavel.all(),
        }

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

        return coordenador.usuario.first_name

    def nome_professores(self):
        professores = []

        for id_professor in self.equipe.values():
            nome_professor = Professores.objects.get(pk=id_professor).usuario.first_name
            professores.append(nome_professor)

        return ', '.join(professores)

    def dividir_atividades(self):
        atividades = []

        for atividade in self.atividades.values():
            atividades.append(atividade)

        return atividades

    def dividir_locacoes_ceu(self):
        locacoes = []

        for locacao in self.locacoes.values():
            locacoes.append(locacao)
        print(locacoes)
        return locacoes


# --------------------------------------------------------------------------------------------------------------
# --------------------------- Model para cadsatro do atendimento com empresa -----------------------------------
# --------------------------------------------------------------------------------------------------------------
class RelatorioDeAtendimentoEmpresaCeu(models.Model):
    tipo = models.CharField(max_length=7, default='empresa', blank=True)
    instituicao = models.CharField(max_length=255)
    ordem = models.ForeignKey(OrdemDeServico, on_delete=models.CASCADE)
    participantes_previa = models.IntegerField()
    participantes_confirmados = models.IntegerField(blank=True, null=True)
    check_in = models.DateTimeField()
    check_out = models.DateTimeField()
    coordenador_peraltas = models.ManyToManyField(Monitor)
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

    @staticmethod
    def dados_iniciais(ordem):
        return {
            'instituicao': ordem.ficha_de_evento.cliente,
            'check_in': ordem.check_in_ceu,
            'check_out': ordem.check_out_ceu,
            'ordem': ordem.id,
            'participantes_previa': ordem.n_participantes,
            'coordenador_peraltas': ordem.monitor_responsavel.all()
        }

    # ------------------------------ Funções para vizualização no template -----------------------------------------
    def nome_professores(self):
        professores = []

        for id_professor in self.equipe.values():
            nome_professor = Professores.objects.get(pk=id_professor).usuario.first_name
            professores.append(nome_professor)

        return ', '.join(professores)

    def coordenador_escalado(self):
        coordenador = Professores.objects.get(id=self.equipe['coordenador'])

        return coordenador.usuario.first_name

    def dividir_atividades(self):
        atividades = []

        for atividade in self.atividades.values():
            atividades.append(atividade)

        return atividades

    def dividir_locacoes_ceu(self):
        locacoes = []

        for locacao in self.locacoes.values():
            locacoes.append(locacao)

        return locacoes


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

        widgets = {
            'participantes_previa': forms.NumberInput(attrs={'placeholder': 'Prévia', 'readonly': True}),
            'participantes_confirmados': forms.NumberInput(attrs={'placeholder': 'Confirmados'}),
            'serie': forms.TextInput(attrs={'readonly': True}),
            'responsaveis': forms.TextInput(attrs={'readonly': True}),
        }


class RelatorioEmpresa(forms.ModelForm):
    class Meta:
        model = RelatorioDeAtendimentoEmpresaCeu
        exclude = ()

        widgets = {
            'instituicao': forms.TimeInput(attrs={'onClick': 'verificarObrigatoriedade()'}),
            'participantes_previa': forms.NumberInput(attrs={'placeholder': 'Prévia'}),
            'participantes_confirmados': forms.NumberInput(attrs={'placeholder': 'Confirmados'}),
        }
