from datetime import datetime

from django.contrib import admin
from cadastro.models import RelatorioDeAtendimentoPublicoCeu, RelatorioDeAtendimentoColegioCeu, \
    RelatorioDeAtendimentoEmpresaCeu
from ceu.models import Professores
from ordemDeServico.models import OrdemDeServico


@admin.register(RelatorioDeAtendimentoPublicoCeu)
class RelatorioDeAtendimentoPublicoCeuAdmin(admin.ModelAdmin):
    list_display = ('data_atendimento_formataado', 'pegar_equipe')
    list_display_links = ('data_atendimento_formataado',)
    search_fields = ('data_atendimento',)
    list_filter = ('data_atendimento',)
    list_per_page = 10

    def pegar_equipe(self, obj):
        return [Professores.objects.get(pk=professor) for professor in obj.equipe.values()]

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

    def data_atendimento_formataado(self, obj):
        return obj.data_atendimento.strftime("%d/%m/%Y")  # Formato de data desejado

    pegar_equipe.short_description = 'Equipe'
    data_atendimento_formataado.short_description = 'Data do atendimento'


@admin.register(RelatorioDeAtendimentoColegioCeu)
class RelatorioDeAtendimentoColegioCeuAdmin(admin.ModelAdmin):
    list_display = ('check_in_formataado', 'pegar_equipe', 'instituicao')
    list_display_links = ('check_in_formataado',)
    search_fields = ('heck_in',)
    list_filter = ('check_in',)
    list_per_page = 20

    def pegar_equipe(self, obj):
        try:
            return [Professores.objects.get(pk=professor) for professor in obj.equipe.values()]
        except Exception as e:
            return []

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

    def check_in_formataado(self, obj):
        return obj.check_in.strftime("%d/%m/%Y")  # Formato de data desejado

    pegar_equipe.short_description = 'Equipe'
    check_in_formataado.short_description = 'Check in do grupo'


@admin.register(RelatorioDeAtendimentoEmpresaCeu)
class RelatorioDeAtendimentoEmpresaCeuAdmin(admin.ModelAdmin):
    list_display = ('check_in_formataado', 'pegar_equipe', 'instituicao')
    list_display_links = ('check_in_formataado',)
    search_fields = ('check_in',)
    list_filter = ('check_in',)
    list_per_page = 20

    def pegar_equipe(self, obj):
        try:
            return [Professores.objects.get(pk=professor) for professor in obj.equipe.values()]
        except Exception as e:
            return []

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

    def check_in_formataado(self, obj):
        return obj.check_in.strftime("%d/%m/%Y")  # Formato de data desejado

    pegar_equipe.short_description = 'Equipe'
    check_in_formataado.short_description = 'Check in do grupo'


@admin.register(OrdemDeServico)
class OrdemDeServicoAdmin(admin.ModelAdmin):
    list_display = ('instituicao', 'check_in_formatado', 'check_out_formatado', 'racional_coordenadores', 'permicao_coordenadores')
    list_editable = ('racional_coordenadores', 'permicao_coordenadores')
    readonly_fields = ('dados_transporte',)
    list_display_links = ('instituicao',)
    list_filter = ('check_in',)
    search_fields = ('instituicao',)
    list_per_page = 20

    def check_in_formatado(self, obj):
        return obj.check_in.strftime("%d/%m/%Y %H:%M")  # Formato de data desejado

    def check_out_formatado(self, obj):
        return obj.check_out.strftime("%d/%m/%Y %H:%M")  # Formato de data desejado

    check_in_formatado.short_description = 'Check in'
    check_out_formatado.short_description = 'Check out'
