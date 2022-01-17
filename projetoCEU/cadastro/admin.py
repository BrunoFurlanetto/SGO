from django.contrib import admin
from cadastro.models import OrdemDeServico, Professores, Tipo, Atividades


class OrdemDeServicoAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'instituicao', 'coordenador', 'data_atendimento', 'solicitado', 'entregue')
    list_editable = ('solicitado', )
    list_display_links = ('tipo',)
    list_filter = ('instituicao', 'coordenador')
    list_per_page = 10


admin.site.register(Professores)
admin.site.register(Tipo)
admin.site.register(Atividades)
admin.site.register(OrdemDeServico, OrdemDeServicoAdmin)
