from django.contrib import admin

from ordemDeServico.models import DadosTransporte
from peraltas.models import (Monitor, ProdutosPeraltas, PerfilsParticipantes, ClienteColegio,
                             Responsavel, InformacoesAdcionais, AtividadesEco, CodigosApp,
                             FichaDeEvento, AtividadePeraltas, EmpresaOnibus, OpcionaisGerais,
                             OpcionaisFormatura, NivelMonitoria, TipoAtividade, GrupoAtividade,
                             Enfermeira, ListaDeCargos, ProdutoCorporativo, EventosCancelados, Eventos)
from peraltas.models import Vendedor


@admin.register(TipoAtividade)
class TipoAtividadeAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo_atividade')


@admin.register(GrupoAtividade)
class GrupoAtividadeAdmin(admin.ModelAdmin):
    list_display = ('id', 'grupo')


@admin.register(AtividadePeraltas)
class AtividadePeraltasAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome_atividade')


@admin.register(AtividadesEco)
class AtividadeEcoAdmin(admin.ModelAdmin):
    list_display = ('nome_atividade_eco',)


class MonitorInline(admin.StackedInline):
    model = Monitor
    can_delete = False
    verbose_name = 'Monitor(a)'
    extra = 0


@admin.register(NivelMonitoria)
class NivelMonitoriaAdmin(admin.ModelAdmin):
    list_display = ('nivel',)


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


class EnfermeiraInline(admin.StackedInline):
    model = Enfermeira
    can_delete = False
    verbose_name = 'Enfermeira'
    extra = 0


@admin.register(Enfermeira)
class EnfermeiraAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'telefone')


@admin.register(EmpresaOnibus)
class EmpresaOnibusAdmin(admin.ModelAdmin):
    list_display = ('viacao', 'cnpj')


@admin.register(FichaDeEvento)
class FichaDeEventoAdmin(admin.ModelAdmin):
    list_display = ('vendedora', 'cliente', 'check_in', 'check_out', 'qtd_convidada', 'data_preenchimento')
    list_filter = ('pre_reserva', 'data_preenchimento')


@admin.register(ProdutosPeraltas)
class ProdutosPeraltasAdmin(admin.ModelAdmin):
    list_display = ('produto',)


@admin.register(ProdutoCorporativo)
class ProdutoCorporativoAdmin(admin.ModelAdmin):
    list_display = ('produto', 'hora_padrao_check_in', 'hora_padrao_check_out')
    list_editable = ('hora_padrao_check_in', 'hora_padrao_check_out')


@admin.register(ListaDeCargos)
class ListaDeCargosAdmin(admin.ModelAdmin):
    list_display = ('cargo', )


@admin.register(PerfilsParticipantes)
class PerfilParticipantesAdmin(admin.ModelAdmin):
    list_display = ('fase', 'idade', 'ano')
    list_editable = ('ano',)
    list_filter = ('fase',)


@admin.register(ClienteColegio)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome_fantasia', 'razao_social', 'cnpj', 'responsavel_cadastro', 'responsavel_alteracao')


@admin.register(Responsavel)
class ResponsavelAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'responsavel_por', 'responsavel_cadastro', 'responsavel_atualizacao')


@admin.register(OpcionaisGerais)
class OpcionaisGeraisAdmin(admin.ModelAdmin):
    list_display = ('id', 'opcional_geral')


@admin.register(OpcionaisFormatura)
class OpcionaisFormaturaAdmin(admin.ModelAdmin):
    list_display = ('id', 'opcional_formatura')


@admin.register(DadosTransporte)
class DadosTransporteAdmin(admin.ModelAdmin):
    list_display = ('id', )


@admin.register(InformacoesAdcionais)
class InformacoesAdicionaisAdmin(admin.ModelAdmin):
    list_display = ('id',)


@admin.register(CodigosApp)
class CodigosAppAdmin(admin.ModelAdmin):
    list_display = ('cliente_pj',)


@admin.register(EventosCancelados)
class EventosCanceladosAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'estagio_evento', 'atendente', 'motivo_cancelamento')
    list_filter = ('estagio_evento', 'atendente')


@admin.register(Eventos)
class EventosAdmin(admin.ModelAdmin):
    list_display = (
        'vendedor', 'cliente', 'check_in', 'check_out', 'qtd_previa',
        'qtd_confirmada', 'data_preenchimento', 'estagio_evento'
    )
    list_display_links = ('cliente', )
    list_per_page = 10
