from django.contrib import admin
from .models import Professores, Tipo, Atividades, OrdemDeServico


class OrdemDeServicoAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'instituicao', 'coordenador_ceu', 'data_atendimento')
    list_display_links = ('tipo', 'instituicao')
    list_filter = ('instituicao', 'coordenador_ceu')
    list_per_page = 10


admin.site.register(Professores)
admin.site.register(Tipo)
admin.site.register(Atividades)
admin.site.register(OrdemDeServico, OrdemDeServicoAdmin)
