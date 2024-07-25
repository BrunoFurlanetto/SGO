from django import forms
from django.contrib import admin

from orcamento.models import HorariosPadroes, ValoresTransporte, Orcamento, OrcamentoPeriodo, \
    ValoresPadrao, OrcamentoMonitor, SeuModeloAdminForm, OrcamentoOpicional, CadastroHorariosPadroesAdmin, TaxaPeriodo, \
    OrcamentosPromocionais, CategoriaOpcionais


@admin.register(HorariosPadroes)
class HorariosPadroesAdmin(admin.ModelAdmin):
    list_display = ('refeicao', 'tipo', 'hora', 'horario_final', 'descritivo')
    ordering = ('-entrada_saida', 'horario')
    form = CadastroHorariosPadroesAdmin


@admin.register(Orcamento)
class OrcamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'responsavel', 'check_in_formatado', 'check_out_formatado', 'data_vencimento_formatado')
    list_display_links = ('cliente',)
    list_filter = ('promocional',)

    def check_in_formatado(self, obj):
        return obj.check_in.strftime("%d/%m/%Y %H:%M")  # Formato de data desejado

    def check_out_formatado(self, obj):
        return obj.check_out.strftime("%d/%m/%Y %H:%M")  # Formato de data desejado

    def data_vencimento_formatado(self, obj):
        try:
            return obj.data_vencimento.strftime("%d/%m/%Y")  # Formato de data desejado
        except AttributeError:
            return ''

    check_in_formatado.short_description = 'Check in'
    check_out_formatado.short_description = 'Check out'
    data_vencimento_formatado.short_description = 'Data de vencimento'


@admin.register(OrcamentosPromocionais)
class OrcamentosPromocionaisAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'valor_base', 'validade')


@admin.register(TaxaPeriodo)
class OrcamentoDiariaAdmin(admin.ModelAdmin):
    list_display = ('inicio_vigencia_formatado', 'final_vigencia_formatado', 'descricao', 'valor')

    def inicio_vigencia_formatado(self, obj):
        return obj.inicio_vigencia.strftime("%d/%m/%Y")  # Formato de data desejado

    def final_vigencia_formatado(self, obj):
        return obj.final_vigencia.strftime("%d/%m/%Y")  # Formato de data desejado

    inicio_vigencia_formatado.short_description = 'Inicio vigência'
    final_vigencia_formatado.short_description = 'Final vigência'


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


@admin.register(CategoriaOpcionais)
class CategoriaOpcionaisAdmin(admin.ModelAdmin):
    list_display = ('nome_categoria',)


@admin.register(OrcamentoOpicional)
class OrcamentoOpicionalAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'categoria', 'descricao', 'valor', 'inicio_vigencia_formatado', 'final_vigencia_formatado')
    ordering = ('nome', 'categoria', 'inicio_vigencia', 'final_vigencia')
    list_editable = ('valor',)
    list_per_page = 20
    search_fields = ('nome',)
    list_filter = ('categoria', 'final_vigencia')

    def inicio_vigencia_formatado(self, obj):
        return obj.inicio_vigencia.strftime("%d/%m/%Y")  # Formato de data desejado

    def final_vigencia_formatado(self, obj):
        return obj.final_vigencia.strftime("%d/%m/%Y")  # Formato de data desejado

    inicio_vigencia_formatado.short_description = 'Inicio vigência'
    final_vigencia_formatado.short_description = 'Final vigência'
