from django.contrib import admin
from cadastro.models import Professores, Tipo, Atividades, OrdemDeServico


class OrdemDeServicoAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'instituicao', 'coordenador', 'data_atendimento')
    list_display_links = ('tipo', 'instituicao')
    list_filter = ('instituicao', 'coordenador')
    list_per_page = 10


admin.site.register(Professores)
admin.site.register(Tipo)
admin.site.register(Atividades)
admin.site.register(OrdemDeServico, OrdemDeServicoAdmin)
