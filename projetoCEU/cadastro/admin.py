from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from cadastro.models import RelatorioDeAtendimentoPublicoCeu, RelatorioDeAtendimentoColegioCeu, \
    RelatorioDeAtendimentoEmpresaCeu


@admin.register(RelatorioDeAtendimentoPublicoCeu)
class RelatorioDeAtendimentoPublicoCeuAdmin(admin.ModelAdmin):
    list_display = ('data_atendimento', 'equipe')
    list_display_links = ('data_atendimento',)
    list_per_page = 10


@admin.register(RelatorioDeAtendimentoColegioCeu)
class RelatorioDeAtendimentoColegioCeuAdmin(admin.ModelAdmin):
    list_display = ('check_in', 'equipe')
    list_display_links = ('check_in',)
    list_per_page = 10


@admin.register(RelatorioDeAtendimentoEmpresaCeu)
class RelatorioDeAtendimentoEmpresaCeuAdmin(admin.ModelAdmin):
    list_display = ('check_in', 'equipe')
    list_display_links = ('check_in',)
    list_per_page = 10
