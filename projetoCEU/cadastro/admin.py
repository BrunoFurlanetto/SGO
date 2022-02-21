from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from cadastro.models import RelatorioDeAtendimentoCeu

@admin.register(RelatorioDeAtendimentoCeu)
class RelatorioDeAtendimentoCeuAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'instituicao', 'solicitado', 'entregue')
    list_display_links = ('tipo',)
    list_editable = ('solicitado', 'entregue')
    list_filter = ('tipo', 'instituicao')
    list_per_page = 10
