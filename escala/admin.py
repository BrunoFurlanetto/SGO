from datetime import datetime

from django.contrib import admin
from escala.models import Escala, Disponibilidade, DiaLimite
from peraltas.models import DisponibilidadePeraltas, EscalaAcampamento, EscalaHotelaria


@admin.register(Escala)
class EscalaAdmin(admin.ModelAdmin):
    list_display = ('data_escala_formatado', 'get_equipe')
    list_filter = ('ano', 'mes')
    search_fields = ('data_escala',)
    list_per_page = 15

    def get_search_results(self, request, queryset, search_term):
        search_term = self.format_search_date(search_term)
        return super().get_search_results(request, queryset, search_term)

    def format_search_date(self, search_term):
        # Tente converter o termo de pesquisa do formato d/m/Y para Y-m-d
        try:
            return datetime.strptime(search_term, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            # Se a conversão falhar, retorne o termo de pesquisa original
            return search_term

    def data_escala_formatado(self, obj):
        return obj.data_escala.strftime("%d/%m/%Y")  # Formato de data desejado

    def get_equipe(self, obj):
        return obj.pegar_equipe()

    get_equipe.short_description = 'Equipe'
    data_escala_formatado.short_description = 'Data da escala'


@admin.register(DiaLimite)
class DiaLimiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'dia_limite')


@admin.register(Disponibilidade)
class DisponibilidadeAdmin(admin.ModelAdmin):
    list_display = ('professor', 'mes', 'ano', 'n_dias')
    list_filter = ('mes', 'ano')
    search_fields = ('professor__usuario__first_name',)
    list_per_page = 10


@admin.register(DisponibilidadePeraltas)
class DisponibilidadePeraltasAdmin(admin.ModelAdmin):
    list_display = ('monitor_enfermeira', 'mes', 'ano', 'n_dias')
    list_filter = ('mes', 'ano')
    search_fields = ('enfermeira__usuario__first_name', 'monitor__usuario__first_name')
    list_per_page = 20


@admin.register(EscalaAcampamento)
class EscalaAcampamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'racional_monitores')
    list_display_links = ('cliente',)
    list_editable = ('racional_monitores',)
    search_fields = ('cliente__nome_fantasia',)


@admin.register(EscalaHotelaria)
class EscalaHotelariaAdmin(admin.ModelAdmin):
    list_display = ('data_escala', 'coordenadores_escala')
    list_filter = ('data',)
