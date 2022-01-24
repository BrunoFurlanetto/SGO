from django.contrib import admin
from escala.models import Escala, Disponibilidade


class EscalaAdmin(admin.ModelAdmin):
    list_display = ('equipe', 'data')


class DisponibilidadeAdmin(admin.ModelAdmin):
    list_display = ('professor', 'mes_referencia', 'n_dias')


admin.site.register(Escala, EscalaAdmin)
admin.site.register(Disponibilidade, DisponibilidadeAdmin)
