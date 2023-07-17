from django.contrib import admin

from orcamento.models import HorariosPadroes, ValoresTransporte


@admin.register(HorariosPadroes)
class HorariosPadroesAdmin(admin.ModelAdmin):
    list_display = ('refeicao', 'horario')
