from django.contrib import admin
from escala.models import Escala, Disponibilidade, DiaLimite
from peraltas.models import DisponibilidadeAcampamento, DisponibilidadeHotelaria, EscalaAcampamento, EscalaHotelaria


@admin.register(Escala)
class EscalaAdmin(admin.ModelAdmin):
    list_display = ('check_in_grupo', 'cliente')
    date_hierarchy = 'check_in_grupo'
    list_per_page = 15


@admin.register(DiaLimite)
class DiaLimiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'dia_limite')


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


@admin.register(EscalaAcampamento)
class EscalaAcampamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente')


@admin.register(EscalaHotelaria)
class EscalaHotelariaAdmin(admin.ModelAdmin):
    list_display = ('id',)


@admin.register(DisponibilidadeHotelaria)
class DisponibilidadeHotelariaAdmin(admin.ModelAdmin):
    list_display = ('monitor', 'mes', 'ano', 'n_dias')
    list_filter = ('mes', 'ano')
    list_per_page = 10
