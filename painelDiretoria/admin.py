from django.contrib import admin

from painelDiretoria.models import Metas


@admin.register(Metas)
class MetasAdmin(admin.ModelAdmin):
    list_display = ('id', 'pax_mon', 'min_media_diarias', 'max_media_diarias')
    list_editable = ('pax_mon', 'min_media_diarias', 'max_media_diarias')
