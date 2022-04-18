from django.contrib import admin
from peraltas.models import Monitor, ProdutosPeraltas, PerfilsParticipantes, ClienteColegio, Responsavel, \
    InformacoesAdcionais, AtividadesEco, CodigosApp, FichaDeEvento, AtividadePeraltas

from peraltas.models import Vendedor


@admin.register(AtividadePeraltas)
class AtividadePeraltasAdmin(admin.ModelAdmin):
    list_display = ('id', 'atividade')


@admin.register(AtividadesEco)
class AtividadeEcoAdmin(admin.ModelAdmin):
    list_display = ('atividade',)


class MonitorInline(admin.StackedInline):
    model = Monitor
    can_delete = False
    verbose_name = 'Monitor(a)'
    extra = 0


@admin.register(Monitor)
class MonitorAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'telefone')


class VendedorInline(admin.StackedInline):
    model = Vendedor
    can_delete = False
    verbose_name = 'Vendedor(a)'
    extra = 0


@admin.register(Vendedor)
class VendedorAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'telefone')


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
