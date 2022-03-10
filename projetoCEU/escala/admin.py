from django.contrib import admin
from escala.models import Escala, Disponibilidade


class EscalaAdmin(admin.ModelAdmin):
    list_display = ('equipe', 'data')
    date_hierarchy = 'data'
    list_per_page = 15


class DisponibilidadeAdmin(admin.ModelAdmin):
    list_display = ('professor', 'mes', 'ano', 'n_dias')
    list_filter = ('mes', 'ano')
    list_per_page = 10


admin.site.register(Escala, EscalaAdmin)
admin.site.register(Disponibilidade, DisponibilidadeAdmin)
