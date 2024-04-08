from datetime import datetime

from django import forms
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse

from orcamento.models import HorariosPadroes, ValoresTransporte, Orcamento, OrcamentoDiaria, OrcamentoPeriodo, \
    ValoresPadrao, OrcamentoMonitor, SeuModeloAdminForm, OrcamentoOpicional, CadastroHorariosPadroesAdmin


@admin.register(HorariosPadroes)
class HorariosPadroesAdmin(admin.ModelAdmin):
    list_display = ('refeicao', 'hora')
    ordering = ('horario',)
    form = CadastroHorariosPadroesAdmin


@admin.register(Orcamento)
class OrcamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'responsavel', 'check_in', 'aprovado', 'necessita_aprovacao_gerencia')
    list_editable = ('necessita_aprovacao_gerencia',)
    list_display_links = ('cliente',)


# @admin.register(OrcamentoDiaria)
# class OrcamentoDiariaAdmin(admin.ModelAdmin):
#     list_display = ('id', 'periodo')


@admin.register(ValoresTransporte)
class ValoresTransporteAdmin(admin.ModelAdmin):
    list_display = ('titulo_transporte', 'inicio_vigencia', 'final_vigencia', 'descricao')


@admin.register(OrcamentoMonitor)
class OrcamentoMonitorAdmin(admin.ModelAdmin):
    list_display = ('nome_monitoria', 'valor', 'descricao_monitoria', 'inicio_vigencia_formatado', 'final_vigencia_formatado')

    def inicio_vigencia_formatado(self, obj):
        return obj.inicio_vigencia.strftime("%d/%m/%Y")  # Formato de data desejado

    def final_vigencia_formatado(self, obj):
        return obj.final_vigencia.strftime("%d/%m/%Y")  # Formato de data desejado

    inicio_vigencia_formatado.short_description = 'Inicio vigência'
    final_vigencia_formatado.short_description = 'Final vigência'


@admin.register(OrcamentoPeriodo)
class PeriodosAdmin(admin.ModelAdmin):
    list_display = ('nome_periodo', 'valor', 'descricao')
    form = SeuModeloAdminForm

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'dias_semana_validos':
            kwargs['widget'] = forms.CheckboxSelectMultiple

        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change:
            valores_selecionados = form.cleaned_data['dias_semana_validos']
            dias_selecionados = [dia.id_dia for dia in valores_selecionados]
            parte_1 = form.cleaned_data['inicio_vigencia'].strftime('%Y%m%d')
            parte_2 = form.cleaned_data['final_vigencia'].strftime('%Y%m%d')
            parte_3 = ''.join(list(map(str, dias_selecionados)))
            obj.id_periodo = f'{parte_1}{parte_2}DSV{parte_3}'

        super().save_model(request, obj, form, change)


@admin.register(ValoresPadrao)
class ValoresPadraoAdmin(admin.ModelAdmin):
    list_display = ('nome_taxa', 'valor_padrao', 'descricao')
    ordering = ('nome_taxa',)


@admin.register(OrcamentoOpicional)
class OrcamentoOpicionalAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao', 'valor')
