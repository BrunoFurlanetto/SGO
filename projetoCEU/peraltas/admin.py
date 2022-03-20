from django.contrib import admin
from peraltas.models import Monitor, ProdutosPeraltas, PerfilsParticipantes, ClienteColegio

from peraltas.models import Vendedor


@admin.register(Monitor)
class ProfessoresAdmin(admin.ModelAdmin):
    list_display = ('nome',)


@admin.register(Vendedor)
class VendedorAdmin(admin.ModelAdmin):
    list_display = ('nome_vendedor',)


@admin.register(ProdutosPeraltas)
class ProdutosPeraltasAdmin(admin.ModelAdmin):
    list_display = ('produto',)


@admin.register(PerfilsParticipantes)
class PerfilParticipantesAdmin(admin.ModelAdmin):
    list_display = ('fase', 'idade', 'ano')
    list_editable = ('ano',)
    list_filter = ('fase',)


@admin.register(ClienteColegio)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome_fantasia', 'razao_social', 'cnpj')
