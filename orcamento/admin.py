from django.contrib import admin

from orcamento.models import HorariosPadroes, ValoresTransporte


@admin.register(HorariosPadroes)
class HorariosPadroesAdmin(admin.ModelAdmin):
    list_display = ('refeicao', 'horario')


@admin.register(ValoresTransporte)
class ValoresTransporteAdmin(admin.ModelAdmin):
    list_display = ('viacao', 'tipo_transporte')
