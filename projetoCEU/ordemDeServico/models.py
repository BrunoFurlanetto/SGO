import os.path

import form as form
from django import forms
from django.db import models

from peraltas.models import Monitor

from peraltas.models import Vendedor


class OrdemDeServico(models.Model):
    tipo_choice = (
        ('Colégio', 'Colégio'),
        ('Empresa', 'Empresa')
    )

    empresa_choices = (
        ('Peraltas', 'Peraltas'),
        ('Fundação CEU', 'Fundação CEU')
    )

    tipo = models.CharField(choices=tipo_choice, max_length=7)
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
    check_in_ceu = models.DateTimeField(blank=True, null=True)
    check_out_ceu = models.DateTimeField(blank=True, null=True)
    atividades_ceu = models.JSONField(blank=True, null=True)
    loacao_ceu = models.JSONField(blank=True, null=True)
    cronograma_peraltas = models.FileField(blank=True, upload_to='cronogramas/%Y/%m/%d')
    observacoes = models.TextField(blank=True, null=True)


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

