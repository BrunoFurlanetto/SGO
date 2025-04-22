from django.contrib import admin

from coreFinanceiro.models import ClassificacoesItens, TiposPagamentos
from financeiro.models import FichaFinanceira


# Register your models here.
@admin.register(ClassificacoesItens)
class ClassificacoesItensAdmin(admin.ModelAdmin):
    list_display = ('codigo_padrao', 'codigo_simplificado', 'sintetico_analitico', 'ativado', 'descritivo')


@admin.register(TiposPagamentos)
class TiposPagamentosAdmin(admin.ModelAdmin):
    list_display = ('tipo_pagamento', 'offline')
