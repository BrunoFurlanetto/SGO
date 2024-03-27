from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from ceu.models import Professores, Atividades, Locaveis, Limitacoes, Estruturas, ReembolsosProfessores
from peraltas.admin import VendedorInline, MonitorInline, EnfermeiraInline


class ProfessorInline(admin.StackedInline):
    model = Professores
    can_delete = False
    verbose_name = 'Professor'
    extra = 0


class UserAdmin(BaseUserAdmin):
    inlines = (ProfessorInline, VendedorInline, MonitorInline, EnfermeiraInline)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Professores)
class ProfessoresAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'telefone_formatado', 'diarista')
    search_fields = ('usuario__first_name', 'usuario__last_name',)

    def telefone_formatado(self, obj):
        return f'({obj.telefone[0:2]}) {obj.telefone[2:7]} - {obj.telefone[7:]}'

    telefone_formatado.short_description = 'Telefone'


@admin.register(Atividades)
class AtividadesAdmin(admin.ModelAdmin):
    filter_horizontal = ('limitacao',)
    search_fields = ('atividade',)


@admin.register(Locaveis)
class LocaveisAdmin(admin.ModelAdmin):
    list_display = ('local', )


# @admin.register(ReembolsosProfessores)
# class ReembolsosProfessoresAdmin(admin.ModelAdmin):
#     list_display = ('usuario_professor', 'valor_reembolso')


admin.site.register(Limitacoes)
admin.site.register(Estruturas)
