from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from ceu.models import Professores, Atividades, Locaveis, Limitacoes, Estruturas, ReembolsosProfessores
from peraltas.admin import VendedorInline, MonitorInline, EnfermeiraInline, ColaboradorExternoInline


class ProfessorInline(admin.StackedInline):
    model = Professores
    can_delete = False
    verbose_name = 'Professor'
    extra = 0


class UserAdmin(BaseUserAdmin):
    inlines = (ProfessorInline, VendedorInline, MonitorInline, EnfermeiraInline, ColaboradorExternoInline)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Professores)
class ProfessoresAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'telefone')


@admin.register(Atividades)
class AtividadesAdmin(admin.ModelAdmin):
    filter_horizontal = ('limitacao', 'serie', 'tipo_pacote', 'intencao_atividade', 'disciplinas_secundarias')


@admin.register(Locaveis)
class LocaveisAdmin(admin.ModelAdmin):
    list_display = ('id', 'local')


@admin.register(ReembolsosProfessores)
class ReembolsosProfessoresAdmin(admin.ModelAdmin):
    list_display = ('usuario_professor', 'valor_reembolso')


admin.site.register(Limitacoes)
admin.site.register(Estruturas)
