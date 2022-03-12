from django.contrib import admin
from peraltas.models import Monitor

from peraltas.models import Vendedor


@admin.register(Monitor)
class ProfessoresAdmin(admin.ModelAdmin):
    list_display = ('nome',)


@admin.register(Vendedor)
class VendedorAdmin(admin.ModelAdmin):
    list_display = ('nome_vendedor',)
