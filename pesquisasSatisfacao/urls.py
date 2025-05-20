from django.urls import path

from . import views

urlpatterns = [
    path(
        'coordenacao/monitoria/evento/<int:id_ordem_de_servico>',
        views.avaliacao_coordenacao_monitoria,
        name='avaliacao_coordenacao_monitoria'
    ),
    path(
        'monitoria/coordenacao/evento/<int:id_ordem_de_servico>',
        views.avaliacao_monitoria_coordenacao,
        name='avaliacao_monitoria_coordenacao'
    ),
]
