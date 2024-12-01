import json
from datetime import timedelta, datetime

from django.db.models.functions import Cast
from django.urls import path
from django.utils.translation import gettext_lazy as _

from django import forms
from django.contrib import admin
from django.shortcuts import render, redirect
from django_admin_search.admin import AdvancedSearchAdmin

from orcamento.models import HorariosPadroes, ValoresTransporte, Orcamento, OrcamentoPeriodo, \
    ValoresPadrao, OrcamentoMonitor, SeuModeloAdminForm, OrcamentoOpicional, CadastroHorariosPadroesAdmin, TaxaPeriodo, \
    OrcamentosPromocionais, CategoriaOpcionais, SubcategoriaOpcionais, TiposDePacote, DadosDePacotes

from django.forms import ModelForm, Form
from django.forms import DateField, CharField, ChoiceField, TextInput


class YourFormSearch(Form):
    style = """
        width: 60%; background-color: #fff; border: 1px solid #ced4da; border-radius: 5px;
        appearance: none; padding: 5px; font-size: 1.2em;',
    """
    nome = CharField(required=False, widget=TextInput(attrs={
        'filter_method': '__icontains',
    }))
    inicio_vigencia = DateField(required=False, widget=TextInput(
        attrs={
            'type': 'date',
            'style': style,
            'class': 'date-form'
        }
    ))
    final_vigencia = DateField(required=False, widget=TextInput(
        attrs={
            'type': 'date',
            'style': style,
        }
    ))


class DuplicarEmMassaForm(forms.Form):
    data_inicio = forms.DateField(
        label="Data de Início",
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    data_fim = forms.DateField(
        label="Data de Fim",
        widget=forms.DateInput(attrs={'type': 'date'})
    )


class DuplicarEmMassaAdmin(admin.ModelAdmin):
    actions = ['duplicar_em_massa']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('duplicar-em-massa/', self.admin_site.admin_view(self.duplicar_em_massa_view),
                 name='duplicar_em_massa'),
        ]

        return custom_urls + urls

    def duplicar_em_massa(self, request, queryset):
        # Redirecionar para a URL personalizada passando o queryset
        selected_ids = ",".join(str(obj.pk) for obj in queryset)
        return redirect(f"{request.path}duplicar-em-massa/?ids={selected_ids}")

    def duplicar_em_massa_view(self, request):
        ids = request.GET.get('ids').split(',')
        queryset = self.get_queryset(request).filter(pk__in=ids)

        if 'aplicar' in request.POST:
            form = DuplicarEmMassaForm(request.POST)

            if form.is_valid():
                data_inicio = form.cleaned_data['data_inicio']
                data_fim = form.cleaned_data['data_fim']

                for item in queryset:
                    item.pk = None

                    if hasattr(item, 'inicio_vigencia'):
                        item.inicio_vigencia = data_inicio
                        item.final_vigencia = data_fim
                    elif hasattr(item, 'inicio_validade'):
                        item.inicio_validade = data_inicio
                        item.final_validade = data_fim

                    item.liberado = False
                    item.save()

                self.message_user(request, f"{queryset.count()} registros duplicados com sucesso!")
                return redirect('..')
        else:
            form = DuplicarEmMassaForm()

        return render(request, 'admin/duplicar_em_massa.html', {
            'items': queryset,
            'form': form,
            'title': "Duplicar registros em massa",
        })


@admin.action(description="Duplicar Orçamentos Promocionais (avançar períodos e vencimento em 1 ano)")
def duplicar_orcamentos_promocionais(modeladmin, request, queryset):
    for orcamento_promocional in queryset:
        orcamento = orcamento_promocional.orcamento
        dados_pacote = orcamento_promocional.dados_pacote

        # Duplicar DadosDePacotes com períodos ajustados
        novos_periodos = dados_pacote.ajustar_periodos()
        novo_dados_pacote = DadosDePacotes.objects.create(
            nome_do_pacote=dados_pacote.nome_do_pacote,
            minimo_de_pagantes=dados_pacote.minimo_de_pagantes,
            tipos_de_pacote_elegivel=dados_pacote.tipos_de_pacote_elegivel,
            monitoria_fechado=dados_pacote.monitoria_fechado,
            transporte_fechado=dados_pacote.transporte_fechado,
            opcionais_fechado=dados_pacote.opcionais_fechado,
            cortesia=dados_pacote.cortesia,
            regra_cortesia=dados_pacote.regra_cortesia,
            periodos_aplicaveis=novos_periodos,
            descricao=dados_pacote.descricao,
        )

        # Duplicar Orcamento com data de vencimento ajustada
        novo_orcamento = Orcamento.objects.create(
            apelido=orcamento.apelido,
            check_in=orcamento.check_in + timedelta(days=365),
            check_out=orcamento.check_out + timedelta(days=365),
            tipo_de_pacote=orcamento.tipo_de_pacote,
            tipo_monitoria=orcamento.tipo_monitoria,
            transporte=orcamento.transporte,
            desconto=0,
            valor=orcamento.valor,
            colaborador=orcamento.colaborador,
            observacoes=orcamento.observacoes,
            promocional=True,
            status_orcamento=orcamento.status_orcamento,
            objeto_orcamento=orcamento.objeto_orcamento,
            objeto_gerencia=orcamento.objeto_gerencia,
            previa=False,
            data_preenchimento=datetime.today().date(),
            data_ultima_edicao=datetime.today().date(),
            data_vencimento=orcamento.data_vencimento + timedelta(days=365),
        )
        data_pagamento_antigo = datetime.strptime(novo_orcamento.objeto_gerencia['data_pagamento'], '%Y-%m-%d')
        data_vencimento_antigo = datetime.strptime(novo_orcamento.objeto_gerencia['data_vencimento'], '%Y-%m-%d')
        novo_orcamento.objeto_gerencia['data_pagamento'] = (data_pagamento_antigo + timedelta(days=365)).strftime('%Y-%m-%d')
        novo_orcamento.objeto_gerencia['data_vencimento'] = (data_vencimento_antigo + timedelta(days=365)).strftime('%Y-%m-%d')
        novo_orcamento.save()
        novo_orcamento.opcionais.set(orcamento.opcionais.all())

        # Criar novo OrcamentosPromocionais
        OrcamentosPromocionais.objects.create(
            dados_pacote=novo_dados_pacote,
            orcamento=novo_orcamento,
            liberados_para_venda=orcamento_promocional.liberados_para_venda,
        )
    modeladmin.message_user(request, "Duplicação concluída com sucesso!")



@admin.register(HorariosPadroes)
class HorariosPadroesAdmin(admin.ModelAdmin):
    list_display = ('refeicao', 'tipo', 'hora', 'horario_final', 'descritivo')
    ordering = ('-entrada_saida', 'horario')
    form = CadastroHorariosPadroesAdmin


@admin.register(Orcamento)
class OrcamentoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'cliente', 'responsavel', 'check_in', 'check_out', 'data_vencimento')
    list_display_links = ('cliente',)
    list_filter = ('promocional',)

    # def check_in_formatado(self, obj):
    #     return obj.check_in.strftime("%d/%m/%Y %H:%M")  # Formato de data desejado
    #
    # def check_out_formatado(self, obj):
    #     return obj.check_out.strftime("%d/%m/%Y %H:%M")  # Formato de data desejado
    #
    # def data_vencimento_formatado(self, obj):
    #     try:
    #         return obj.data_vencimento.strftime("%d/%m/%Y")  # Formato de data desejado
    #     except AttributeError:
    #         return ''
    #
    # check_in_formatado.short_description = 'Check in'
    # check_out_formatado.short_description = 'Check out'
    # data_vencimento_formatado.short_description = 'Data de vencimento'


@admin.register(OrcamentosPromocionais)
class OrcamentosPromocionaisAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'valor_base', 'validade', 'liberado_para_venda')
    list_editable = ('liberado_para_venda',)
    actions = [duplicar_orcamentos_promocionais]


@admin.register(TaxaPeriodo)
class OrcamentoDiariaAdmin(admin.ModelAdmin):
    list_display = ('inicio_vigencia', 'final_vigencia', 'descricao', 'valor')

    # def inicio_vigencia_formatado(self, obj):
    #     return obj.inicio_vigencia.strftime("%d/%m/%Y")  # Formato de data desejado
    #
    # def final_vigencia_formatado(self, obj):
    #     return obj.final_vigencia.strftime("%d/%m/%Y")  # Formato de data desejado
    #
    # inicio_vigencia_formatado.short_description = 'Inicio vigência'
    # final_vigencia_formatado.short_description = 'Final vigência'


@admin.register(ValoresTransporte)
class ValoresTransporteAdmin(DuplicarEmMassaAdmin):
    list_display = (
        'titulo_transporte',
        'inicio_vigencia',
        'final_vigencia',
        'valor_1_dia',
        'valor_final_1_dia',
        'valor_2_dia',
        'valor_final_2_dia',
        'valor_3_dia',
        'valor_final_3_dia',
        'liberado'
    )
    list_editable = ('liberado',)
    ordering = ('-inicio_vigencia', 'titulo_transporte')

    # def inicio_vigencia_formatado(self, obj):
    #     return obj.inicio_vigencia.strftime("%d/%m/%Y")  # Formato de data desejado
    #
    # def final_vigencia_formatado(self, obj):
    #     return obj.final_vigencia.strftime("%d/%m/%Y")  # Formato de data desejado
    #
    # inicio_vigencia_formatado.short_description = 'Inicio vigência'
    # final_vigencia_formatado.short_description = 'Final vigência'


@admin.register(OrcamentoMonitor)
class OrcamentoMonitorAdmin(DuplicarEmMassaAdmin):
    list_display = (
        'nome_monitoria',
        'valor',
        'valor_final',
        'descricao_monitoria',
        'inicio_vigencia',
        'final_vigencia',
        'liberado'
    )
    ordering = ('-inicio_vigencia', 'nome_monitoria')
    list_editable = ('liberado',)

    # def inicio_vigencia_formatado(self, obj):
    #     return obj.inicio_vigencia.strftime("%d/%m/%Y")  # Formato de data desejado
    #
    # def final_vigencia_formatado(self, obj):
    #     return obj.final_vigencia.strftime("%d/%m/%Y")  # Formato de data desejado
    #
    # inicio_vigencia_formatado.short_description = 'Inicio vigência'
    # final_vigencia_formatado.short_description = 'Final vigência'


@admin.register(OrcamentoPeriodo)
class PeriodosAdmin(DuplicarEmMassaAdmin):
    list_display = (
    'nome_periodo', 'inicio_vigencia', 'final_vigencia', 'valor', 'valor_final', 'descricao', 'liberado')
    ordering = ('-inicio_vigencia', 'nome_periodo')
    list_editable = ('liberado',)
    form = SeuModeloAdminForm

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'dias_semana_validos':
            kwargs['widget'] = forms.CheckboxSelectMultiple

        return super().formfield_for_dbfield(db_field, request, **kwargs)


@admin.register(ValoresPadrao)
class ValoresPadraoAdmin(admin.ModelAdmin):
    list_display = ('nome_taxa', 'valor_padrao', 'descricao')
    ordering = ('nome_taxa',)


@admin.register(CategoriaOpcionais)
class CategoriaOpcionaisAdmin(admin.ModelAdmin):
    list_display = ('nome_categoria',)


@admin.register(SubcategoriaOpcionais)
class SubategoriaOpcionaisAdmin(admin.ModelAdmin):
    list_display = ('nome_sub_categoria',)


@admin.register(OrcamentoOpicional)
class OrcamentoOpicionalAdmin(AdvancedSearchAdmin, DuplicarEmMassaAdmin):
    list_display = ('nome', 'categoria', 'sub_categoria', 'valor', 'valor_final', 'inicio_vigencia',
                    'final_vigencia', 'liberado')
    ordering = ('nome', 'categoria', 'inicio_vigencia', 'final_vigencia')
    list_editable = ('valor', 'categoria', 'liberado', 'sub_categoria')
    list_per_page = 20
    search_fields = ('nome',)
    list_filter = ('categoria', 'sub_categoria', 'final_vigencia')
    readonly_fields = ('valor_final',)
    save_as = True
    search_form = YourFormSearch

    # def inicio_vigencia_formatado(self, obj):
    #     return obj.inicio_vigencia.strftime("%d/%m/%Y")  # Formato de data desejado
    #
    # def final_vigencia_formatado(self, obj):
    #     return obj.final_vigencia.strftime("%d/%m/%Y")  # Formato de data desejado
    #
    # inicio_vigencia_formatado.short_description = 'Inicio vigência'
    # final_vigencia_formatado.short_description = 'Final vigência'


@admin.register(TiposDePacote)
class TiposDePacoteAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'descricao')
    ordering = ('titulo',)
