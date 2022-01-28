from django.contrib import admin
from fichaAvaliacao.models import FichaDeAvaliacao


class FichaDeAvaliacaoAdmin(admin.ModelAdmin):
    list_display = ('instituicao', 'data_preenchimento')


admin.site.register(FichaDeAvaliacao, FichaDeAvaliacaoAdmin)
