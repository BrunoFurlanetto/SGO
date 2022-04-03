from django.contrib import admin
from peraltas.models import Monitor, ProdutosPeraltas, PerfilsParticipantes, ClienteColegio, Responsavel, \
    InformacoesAdcionais, AtividadesEco, CodigosApp, FichaDeEvento, AtividadePeraltas

from peraltas.models import Vendedor


@admin.register(Monitor)
class ProfessoresAdmin(admin.ModelAdmin):
    list_display = ('nome',)


@admin.register(AtividadePeraltas)
class AtividadePeraltasAdmin(admin.ModelAdmin):
    list_display = ('id', 'atividade')


@admin.register(AtividadesEco)
class AtividadeEcoAdmin(admin.ModelAdmin):
    list_display = ('atividade',)


@admin.register(Vendedor)
class VendedorAdmin(admin.ModelAdmin):
    list_display = ('nome_vendedor',)


@admin.register(FichaDeEvento)
class FichaDeEventoAdmin(admin.ModelAdmin):
    list_display = ('vendedora',)


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
    list_display = ('id', 'nome_fantasia', 'razao_social', 'cnpj')


@admin.register(Responsavel)
class ResponsavelAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome',)


@admin.register(InformacoesAdcionais)
class InformacoesAdicionaisAdmin(admin.ModelAdmin):
    list_display = ('id',)


@admin.register(CodigosApp)
class CodigosAppAdmin(admin.ModelAdmin):
    list_display = ('cliente_pj',)
