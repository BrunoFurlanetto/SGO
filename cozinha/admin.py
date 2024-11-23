from django.contrib import admin

from cozinha.models import Cozinheiro


class CozinheiroInline(admin.StackedInline):
    model = Cozinheiro
    can_delete = False
    verbose_name = 'Cozinheiro'
    extra = 0


@admin.register(Cozinheiro)
class CozinheiroAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'funcao')
