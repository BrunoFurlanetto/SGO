from datetime import datetime

from django.contrib import admin

from ordemDeServico.models import DadosTransporte, TipoVeiculo
from peraltas.models import (Monitor, ProdutosPeraltas, PerfilsParticipantes, ClienteColegio,
                             Responsavel, InformacoesAdcionais, AtividadesEco, CodigosApp,
                             FichaDeEvento, AtividadePeraltas, EmpresaOnibus, OpcionaisGerais,
                             OpcionaisFormatura, NivelMonitoria, TipoAtividade, GrupoAtividade,
                             Enfermeira, ListaDeCargos, ProdutoCorporativo, EventosCancelados, Eventos, CodigosPadrao,
                             TiposPagamentos, RelacaoClienteResponsavel)
from peraltas.models import Vendedor


@admin.register(TipoAtividade)
class TipoAtividadeAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo_atividade')
    list_display_links = ('tipo_atividade',)


@admin.register(GrupoAtividade)
class GrupoAtividadeAdmin(admin.ModelAdmin):
    list_display = ('id', 'grupo', 'obrigatoria')
    list_editable = ('obrigatoria',)


@admin.register(AtividadePeraltas)
class AtividadePeraltasAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome_atividade')
    search_fields = ('nome_atividade',)


@admin.register(AtividadesEco)
class AtividadeEcoAdmin(admin.ModelAdmin):
    list_display = ('nome_atividade_eco',)
    search_fields = ('nome_atividade_eco',)


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
    list_display = ('nome_completo', 'biologo', 'tecnica', 'fixo', 'telefone_formatado')
    search_fields = ('usuario__first_name', 'usuario__last_name',)

    def telefone_formatado(self, obj):
        return f'({obj.telefone[0:2]}) {obj.telefone[2:7]} - {obj.telefone[7:]}'

    telefone_formatado.short_description = 'Telefone'


class VendedorInline(admin.StackedInline):
    model = Vendedor
    can_delete = False
    verbose_name = 'Vendedor(a)'
    extra = 0


@admin.register(Vendedor)
class VendedorAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'telefone_formatado', 'supervisor')
    search_fields = ('usuario__first_name',)

    def telefone_formatado(self, obj):
        return f'({obj.telefone[0:2]}) {obj.telefone[2:7]} - {obj.telefone[7:]}'

    telefone_formatado.short_description = 'Telefone'


class EnfermeiraInline(admin.StackedInline):
    model = Enfermeira
    can_delete = False
    verbose_name = 'Enfermeira'
    extra = 0


@admin.register(Enfermeira)
class EnfermeiraAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'telefone_formatado')
    search_fields = ('usuario__first_name',)

    def telefone_formatado(self, obj):
        return f'({obj.telefone[0:2]}) {obj.telefone[2:7]} - {obj.telefone[7:]}'

    telefone_formatado.short_description = 'Telefone'


@admin.register(EmpresaOnibus)
class EmpresaOnibusAdmin(admin.ModelAdmin):
    list_display = ('viacao', 'cnpj')


@admin.register(FichaDeEvento)
class FichaDeEventoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'vendedora', 'check_in_formatado', 'check_out_formatado', 'qtd_convidada', 'data_preenchimento_formatado')
    list_filter = ('pre_reserva', 'data_preenchimento')
    search_fields = ('cliente', 'vendedora')

    def check_in_formatado(self, obj):
        return obj.check_in.strftime("%d/%m/%Y %H:%M")  # Formato de data desejado

    def check_out_formatado(self, obj):
        return obj.check_out.strftime("%d/%m/%Y %H:%M")  # Formato de data desejado

    def data_preenchimento_formatado(self, obj):
        try:
            return obj.data_preenchimento.strftime("%d/%m/%Y")  # Formato de data desejado
        except AttributeError:
            return ''

    check_in_formatado.short_description = 'Check in'
    check_out_formatado.short_description = 'Check out'
    data_preenchimento_formatado.short_description = 'Data de preenchimento'


@admin.register(ProdutosPeraltas)
class ProdutosPeraltasAdmin(admin.ModelAdmin):
    list_display = ('produto',)


@admin.register(ProdutoCorporativo)
class ProdutoCorporativoAdmin(admin.ModelAdmin):
    list_display = ('produto', 'hora_padrao_check_in', 'hora_padrao_check_out')
    list_editable = ('hora_padrao_check_in', 'hora_padrao_check_out')


@admin.register(ListaDeCargos)
class ListaDeCargosAdmin(admin.ModelAdmin):
    list_display = ('cargo',)
    search_fields = ('cargo',)


@admin.register(PerfilsParticipantes)
class PerfilParticipantesAdmin(admin.ModelAdmin):
    list_display = ('fase', 'idade', 'ano')
    list_editable = ('ano',)
    list_filter = ('fase',)


@admin.register(ClienteColegio)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome_fantasia', 'razao_social', 'cnpj', 'responsavel_cadastro', 'responsavel_alteracao', 'codigo_app_pj')
    list_display_links = ('nome_fantasia',)
    search_fields = ('nome_fantasia', 'razao_social', 'cnpj', 'codigo_app_pj')


@admin.register(Responsavel)
class ResponsavelAdmin(admin.ModelAdmin):
    list_display = ('nome', 'responsavel_por', 'responsavel_cadastro', 'responsavel_atualizacao')
    search_fields = ('nome',)

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        if search_term:
            relacoes = RelacaoClienteResponsavel.objects.filter(cliente__nome_fantasia__icontains=search_term)
            responsaveis_ids = relacoes.values_list('responsavel__id', flat=True)
            queryset |= self.model.objects.filter(id__in=responsaveis_ids)

        return queryset, use_distinct


@admin.register(OpcionaisGerais)
class OpcionaisGeraisAdmin(admin.ModelAdmin):
    list_display = ('id', 'opcional_geral')
    list_display_links = ('opcional_geral',)
    search_fields = ('opcional_geral',)


@admin.register(OpcionaisFormatura)
class OpcionaisFormaturaAdmin(admin.ModelAdmin):
    list_display = ('id', 'opcional_formatura')
    list_display_links = ('opcional_formatura',)
    search_fields = ('opcional_formatura',)


@admin.register(TipoVeiculo)
class TipoVeiculoAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo_veiculo')
    list_display_links = ('tipo_veiculo',)


# @admin.register(DadosTransporte)
# class DadosTransporteAdmin(admin.ModelAdmin):
#     list_display = ('id',)


# @admin.register(InformacoesAdcionais)
# class InformacoesAdicionaisAdmin(admin.ModelAdmin):
#     list_display = ('id',)


@admin.register(CodigosPadrao)
class CodigosPadraoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'codigo')


@admin.register(CodigosApp)
class CodigosAppAdmin(admin.ModelAdmin):
    list_display = ('cliente_pj',)


@admin.register(TiposPagamentos)
class TiposPagamentosAdmin(admin.ModelAdmin):
    list_display = ('tipo_pagamento', 'offline')


@admin.register(EventosCancelados)
class EventosCanceladosAdmin(admin.ModelAdmin):
    list_display = (
        'cliente',
        'estagio_evento',
        'atendente',
        'motivo_cancelamento',
        'data_entrada',
        'data_saida',
        'data_evento',
        'participantes',
        'tipo_evento',
        'colaborador_excluiu'
    )
    list_filter = ('estagio_evento', 'atendente')
    search_fields = ('cliente', 'atendente')


@admin.register(Eventos)
class EventosAdmin(admin.ModelAdmin):
    list_display = (
        'vendedor', 'cliente', 'check_in', 'check_out', 'qtd_previa',
        'qtd_confirmada', 'data_preenchimento', 'estagio_evento', 'codigo_pagamento',
        'produto_peraltas', 'produto_corporativo', 'tipo_evento', 'dias_evento', 'adesao_evento'
    )
    list_display_links = ('cliente',)
    list_filter = ('ficha_de_evento__pre_reserva', 'ficha_de_evento__agendado', 'ficha_de_evento__check_in')
    list_per_page = 100

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

    search_fields = (
        'ficha_de_evento__cliente__nome_fantasia',
        'ficha_de_evento__vendedora__usuario__first_name',
        'ficha_de_evento__check_in',
        'ficha_de_evento__codigos_app__eficha',
        'ficha_de_evento__produto__produto',
    )
