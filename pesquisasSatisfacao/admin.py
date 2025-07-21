from django.contrib import admin

from pesquisasSatisfacao.models import OpcoesMotivacao


@admin.register(OpcoesMotivacao)
class OpcoesMotivacaoAdmin(admin.ModelAdmin):
    list_display = ('motivo',)
