from django.contrib import admin
from cadastro.models import RelatorioDeAtendimentoPublicoCeu, RelatorioDeAtendimentoColegioCeu, \
    RelatorioDeAtendimentoEmpresaCeu
from ordemDeServico.models import OrdemDeServico


@admin.register(RelatorioDeAtendimentoPublicoCeu)
class RelatorioDeAtendimentoPublicoCeuAdmin(admin.ModelAdmin):
    list_display = ('id', 'data_atendimento', 'equipe')
    list_display_links = ('data_atendimento',)
    list_per_page = 10


@admin.register(RelatorioDeAtendimentoColegioCeu)
class RelatorioDeAtendimentoColegioCeuAdmin(admin.ModelAdmin):
    list_display = ('id', 'check_in', 'equipe')
    list_display_links = ('check_in',)
    list_per_page = 10


@admin.register(RelatorioDeAtendimentoEmpresaCeu)
class RelatorioDeAtendimentoEmpresaCeuAdmin(admin.ModelAdmin):
    list_display = ('id', 'check_in', 'equipe')
    list_display_links = ('check_in',)
    list_per_page = 10


@admin.register(OrdemDeServico)
class OrdemDeServico(admin.ModelAdmin):
    list_display = ('id', 'instituicao', 'check_in', 'check_out', 'monitor_responsavel')
    list_display_links = ()
    list_editable = ('monitor_responsavel',)
    list_per_page = 10
