from datetime import datetime

from django.contrib import admin

from cozinha.models import Cozinheiro, RegistroVisualizacoes


class CozinheiroInline(admin.StackedInline):
    model = Cozinheiro
    can_delete = False
    verbose_name = 'Cozinheiro'
    extra = 0


@admin.register(Cozinheiro)
class CozinheiroAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'funcao')


@admin.register(RegistroVisualizacoes)
class RegistroVisualizacoesAdmin(admin.ModelAdmin):
    list_display = ('nome_cozinheiro', 'data_refeicoes', 'data_hora_visualizacao')
    readonly_fields = ('usuario', 'data_refeicoes', 'data_hora_visualizacao')
    search_fields = ('usuario__first_name', 'usuario__last_name', 'data_refeicoes')

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
