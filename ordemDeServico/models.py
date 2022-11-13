import os.path

from django import forms
from django.db import models

from peraltas.models import Monitor, AtividadesEco, AtividadePeraltas, FichaDeEvento, GrupoAtividade

from peraltas.models import Vendedor


class OrdemDeServico(models.Model):
    tipo_choice = (
        ('Colégio', 'Colégio'),
        ('Empresa', 'Empresa')
    )

    empresa_choices = (
        ('Peraltas', 'Peraltas'),
        ('CEU', 'Fundação CEU')
    )

    tipo = models.CharField(choices=tipo_choice, max_length=7)
    ficha_de_evento = models.ForeignKey(FichaDeEvento, on_delete=models.DO_NOTHING)
    instituicao = models.CharField(max_length=300)
    cidade = models.CharField(max_length=255)
    check_in = models.DateTimeField()
    check_out = models.DateTimeField()
    n_participantes = models.IntegerField()
    serie = models.CharField(max_length=255, blank=True, null=True)
    n_professores = models.IntegerField(blank=True, null=True)
    responsavel_grupo = models.CharField(max_length=255)
    vendedor = models.ForeignKey(Vendedor, on_delete=models.DO_NOTHING)
    empresa = models.CharField(choices=empresa_choices, max_length=15)
    monitor_responsavel = models.ForeignKey(Monitor, on_delete=models.DO_NOTHING)
    monitor_embarque = models.ForeignKey(Monitor, blank=True, null=True, on_delete=models.DO_NOTHING,
                                         related_name='monitor_embarque')
    check_in_ceu = models.DateTimeField(blank=True, null=True)
    check_out_ceu = models.DateTimeField(blank=True, null=True)
    atividades_eco = models.JSONField(blank=True, null=True)
    atividades_peraltas = models.ManyToManyField(AtividadePeraltas, blank=True)
    atividades_ceu = models.JSONField(blank=True, null=True)
    locacao_ceu = models.JSONField(blank=True, null=True)
    cronograma_peraltas = models.FileField(blank=True, upload_to='cronogramas/%Y/%m/%d')
    observacoes = models.TextField(blank=True, null=True)
    relatorio_ceu_entregue = models.BooleanField(default=False)
    ficha_avaliacao = models.BooleanField(default=False)
    escala_ceu = models.BooleanField(default=False)
    escala = models.BooleanField(default=False)

    def dividir_atividades_ceu(self):
        atividades = []

        for atividade in self.atividades_ceu.values():
            atividades.append(atividade)

        return atividades

    def dividir_locacoes_ceu(self):
        locacoes = []

        for locacao in self.locacao_ceu.values():
            locacoes.append(locacao)

        return locacoes

    def dividir_atividades_eco(self):
        atividades = []

        for atividade in self.atividades_eco.values():
            atividades.append(atividade)

        return atividades


class CadastroOrdemDeServico(forms.ModelForm):
    class Meta:
        model = OrdemDeServico
        exclude = ()

        widgets = {
            'check_in': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'check_out': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'check_in_ceu': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'check_out_ceu': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'tipo': forms.Select(attrs={'onchange': 'verifica_colegio_empresa(this)', 'onclick': 'mostrar_check()'})
        }

    def __init__(self, *args, **kwargs):
        super(CadastroOrdemDeServico, self).__init__(*args, **kwargs)
        self.fields['atividades_peraltas'].choices = self.opt_groups()
        self.fields['instituicao'].widget.attrs['readonly'] = True
        self.fields['cidade'].widget.attrs['readonly'] = True
        self.fields['responsavel_grupo'].widget.attrs['readonly'] = True

    @staticmethod
    def opt_groups():
        grupos = []

        for grupo in GrupoAtividade.objects.all():
            novo_grupo = []
            sub_grupo = []

            for atividade in AtividadePeraltas.objects.all():
                if atividade.grupo == grupo:
                    sub_grupo.append([atividade.id, atividade.nome_atividade])

            novo_grupo = [grupo, sub_grupo]
            grupos.append(novo_grupo)

        return grupos
