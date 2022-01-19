from django.contrib import admin
from escala.models import Escala


class EscalaAdmin(admin.ModelAdmin):
    list_display = ('equipe', 'data')


admin.site.register(Escala, EscalaAdmin)
