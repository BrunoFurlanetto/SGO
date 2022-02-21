from django.contrib import admin
from cadastro.models import RelatorioDeAtendimentoCeu, Professores, Tipo, Atividades, Locaveis, Limitacoes


class RelatorioDeAtendimentoCeuAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'instituicao', 'solicitado', 'entregue')
    list_display_links = ('tipo',)
    list_editable = ('solicitado', 'entregue')
    list_filter = ('tipo', 'instituicao')
    list_per_page = 10


class ProfessoresAdmin(admin.ModelAdmin):
    list_display = ('primeiro_nome', 'sobrenome', 'email', 'telefone')


class AtividadesAdmin(admin.ModelAdmin):
    filter_horizontal = ('limitacao',)


admin.site.register(Limitacoes)
admin.site.register(Professores, ProfessoresAdmin)
admin.site.register(Tipo)
admin.site.register(Atividades, AtividadesAdmin)
admin.site.register(Locaveis)
admin.site.register(RelatorioDeAtendimentoCeu, RelatorioDeAtendimentoCeuAdmin)
