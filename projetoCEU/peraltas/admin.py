from django.contrib import admin
from peraltas.models import Monitor


@admin.register(Monitor)
class ProfessoresAdmin(admin.ModelAdmin):
    list_display = ('nome',)
