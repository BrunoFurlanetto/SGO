from django.contrib import admin
from cadastro.models import Professores, Tipo, Atividades, OrdemDeServico
from escala.models import Escala
from fichaAvaliacao.models import FichaDeAvaliacao


class OrdemDeServicoAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'instituicao', 'coordenador', 'data_atendimento', 'solicitado')
    list_editable = ('solicitado', )
    list_display_links = ('instituicao', )
    list_filter = ('instituicao', 'coordenador')
    list_per_page = 10


class FichaDeAvaliacaoAdmin(admin.ModelAdmin):
    list_display = ('instituicao', )

admin.site.register(Professores)
admin.site.register(Tipo)
admin.site.register(Atividades)
admin.site.register(Escala)
admin.site.register(OrdemDeServico, OrdemDeServicoAdmin)
admin.site.register(FichaDeAvaliacao, FichaDeAvaliacaoAdmin)
