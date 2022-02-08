from django.contrib import admin
from cadastro.models import OrdemDeServico, Professores, Tipo, Atividades, Locaveis


class OrdemDeServicoAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'instituicao', 'coordenador', 'data_atendimento', 'solicitado', 'entregue')
    list_display_links = ('tipo',)
    list_editable = ('solicitado', 'entregue')
    list_filter = ('tipo', 'instituicao', 'coordenador')
    list_per_page = 10


admin.site.register(Professores)
admin.site.register(Tipo)
admin.site.register(Atividades)
admin.site.register(Locaveis)
admin.site.register(OrdemDeServico, OrdemDeServicoAdmin)
