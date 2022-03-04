from django.contrib import admin
from escala.models import Escala, Disponibilidade


class EscalaAdmin(admin.ModelAdmin):
    list_display = ('equipe', 'data')
    # date_hierarchy = 'data'


class DisponibilidadeAdmin(admin.ModelAdmin):
    list_display = ('professor', 'mes', 'ano', 'n_dias')


admin.site.register(Escala, EscalaAdmin)
admin.site.register(Disponibilidade, DisponibilidadeAdmin)
