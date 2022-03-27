from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from ceu.models import Professores, Atividades, Locaveis, Limitacoes, Estruturas


class ProfessorInline(admin.StackedInline):
    model = Professores
    can_delete = False
    verbose_name = 'Professor'
    extra = 0


class UserAdmin(BaseUserAdmin):
    inlines = (ProfessorInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Professores)
class ProfessoresAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'telefone')


@admin.register(Atividades)
class AtividadesAdmin(admin.ModelAdmin):
    filter_horizontal = ('limitacao',)


@admin.register(Locaveis)
class LocaveisAdmin(admin.ModelAdmin):
    list_display = ('id', 'local')

admin.site.register(Limitacoes)
admin.site.register(Estruturas)
