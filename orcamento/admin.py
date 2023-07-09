from django.contrib import admin

from orcamento.models import HorariosPadroes


@admin.register(HorariosPadroes)
class HorariosPadroesAdmin(admin.ModelAdmin):
    list_display = ('refeicao', 'horario')
