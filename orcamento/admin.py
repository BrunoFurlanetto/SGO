from datetime import datetime

from django import forms
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse

from orcamento.models import HorariosPadroes, ValoresTransporte, Orcamento, OrcamentoDiaria, OrcamentoPeriodo, \
    ValoresPadrao, OrcamentoMonitor, SeuModeloAdminForm


@admin.register(HorariosPadroes)
class HorariosPadroesAdmin(admin.ModelAdmin):
    list_display = ('refeicao', 'horario')


@admin.register(Orcamento)
class OrcamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'responsavel', 'check_in', 'aprovado', 'necessita_aprovacao_gerencia')
    list_editable = ('necessita_aprovacao_gerencia',)
    list_display_links = ('cliente',)


@admin.register(OrcamentoDiaria)
class OrcamentoDiariaAdmin(admin.ModelAdmin):
    list_display = ('id', 'periodo')


@admin.register(ValoresTransporte)
class ValoresTransporteAdmin(admin.ModelAdmin):
    list_display = ('id',)


@admin.register(OrcamentoMonitor)
class OrcamentoMonitorAdmin(admin.ModelAdmin):
    list_display = ('nome_monitoria', 'valor', 'descricao_monitoria')


@admin.register(OrcamentoPeriodo)
class PeriodosAdmin(admin.ModelAdmin):
    list_display = ('id_periodo', 'nome_periodo')
    form = SeuModeloAdminForm

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'dias_semana_validos':
            kwargs['widget'] = forms.CheckboxSelectMultiple

        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        valores_selecionados = form.cleaned_data['dias_semana_validos']
        dias_selecionados = [dia.id_dia for dia in valores_selecionados]
        parte_1 = form.cleaned_data['inicio_vigencia'].strftime('%Y%m%d')
        parte_2 = form.cleaned_data['final_vigencia'].strftime('%Y%m%d')
        parte_3 = '_'.join(list(map(str, dias_selecionados)))
        obj.id_periodo = f'{parte_1}{parte_2}{parte_3}'

        super().save_model(request, obj, form, change)


@admin.register(ValoresPadrao)
class ValoresPadraoAdmin(admin.ModelAdmin):
    list_display = ('nome_taxa', 'valor', 'descricao')
