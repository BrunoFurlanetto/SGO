from django.contrib import admin

from orcamento.models import HorariosPadroes, ValoresTransporte, Orcamento, OrcamentoDiaria


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
    list_display = ('id', 'periodo')
