from django.contrib import admin

from coreFinanceiro.models import ClassificacoesItens
from financeiro.models import FichaFinanceira
from peraltas.models import TiposPagamentos


# Register your models here.
@admin.register(ClassificacoesItens)
class ClassificacoesItensAdmin(admin.ModelAdmin):
    list_display = ('codigo_padrao',)
