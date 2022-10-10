from django.contrib import admin

from detector.models import DetectorDeBombas


@admin.register(DetectorDeBombas)
class DetectorDeBombasAdmin(admin.ModelAdmin):
    list_display = ('id',)
