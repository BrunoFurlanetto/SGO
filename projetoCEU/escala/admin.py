from django.contrib import admin
from escala.models import Escala, Disponibilidade
from peraltas.models import DisponibilidadeAcampamento, DisponibilidadeHotelaria


@admin.register(Escala)
class EscalaAdmin(admin.ModelAdmin):
    list_display = ('equipe', 'data')
    date_hierarchy = 'data'
    list_per_page = 15


@admin.register(Disponibilidade)
class DisponibilidadeAdmin(admin.ModelAdmin):
    list_display = ('professor', 'mes', 'ano', 'n_dias')
    list_filter = ('mes', 'ano')
    list_per_page = 10


@admin.register(DisponibilidadeAcampamento)
class DisponibilidadeAcampamentoAdmin(admin.ModelAdmin):
    list_display = ('monitor', 'mes', 'ano', 'n_dias')
    list_filter = ('mes', 'ano')
    list_per_page = 10


@admin.register(DisponibilidadeHotelaria)
class DisponibilidadeHotelariaAdmin(admin.ModelAdmin):
    list_display = ('monitor', 'mes', 'ano', 'n_dias')
    list_filter = ('mes', 'ano')
    list_per_page = 10
