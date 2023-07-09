from django.apps import AppConfig


class PeraltasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'peraltas'

    def ready(self):
        import peraltas.signals
