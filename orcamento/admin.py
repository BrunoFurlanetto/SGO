from django.db.models.functions import Cast
from django.urls import path
from django.utils.translation import gettext_lazy as _

from django import forms
from django.contrib import admin
from django.shortcuts import render, redirect
from django_admin_search.admin import AdvancedSearchAdmin

from orcamento.models import HorariosPadroes, ValoresTransporte, Orcamento, OrcamentoPeriodo, \
    ValoresPadrao, OrcamentoMonitor, SeuModeloAdminForm, OrcamentoOpicional, CadastroHorariosPadroesAdmin, TaxaPeriodo, \
    OrcamentosPromocionais, CategoriaOpcionais, SubcategoriaOpcionais


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
    list_display = ('__str__', 'valor_base', 'validade')


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
