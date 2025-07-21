from django.apps import AppConfig


class OrdemdeservicoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ordemDeServico'

    def ready(self):
        import ordemDeServico.signals