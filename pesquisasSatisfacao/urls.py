from django.urls import path

from . import views

urlpatterns = [
    path(
        'coordenacao/monitoria/evento/<int:id_ordem_de_servico>',
        views.avaliacao_coordenacao_monitoria,
        name='avaliacao_coordenacao_monitoria'
    ),
    path(
        'coordenacao/monitoria/visualizacao/evento/<int:id_avaliacao>',
        views.ver_avaliacao_monitores,
        name='ver_avaliacao_monitores'
    ),
    path(
        'monitoria/coordenacao/evento/<int:id_ordem_de_servico>',
        views.avaliacao_monitoria_coordenacao,
        name='avaliacao_monitoria_coordenacao'
    ),
    path(
        'monitoria/coordenacao/visualizacao/evento/<int:id_avaliacao>',
        views.ver_avaliacao_coordenadores,
        name='ver_avaliacao_coordenadores'
    ),
    path(
        'colegio/evento/<int:id_ordem_de_servico>',
        views.avaliacao_colegio,
        name='avaliacao_colegio'
    ),
    path(
        'colegio/visualizacao/evento/<int:id_avaliacao>',
        views.ver_avaliacao_colegio,
        name='ver_avaliacao_colegio'
    ),
    path(
        'corporativo/evento/<int:id_ordem_de_servico>',
        views.avaliacao_corporativo,
        name='avaliacao_corporativo'
    ),
    path(
        'corporativo/visualizacao/evento/<int:id_avaliacao>',
        views.ver_avaliacao_corporativo,
        name='ver_avaliacao_corporativo'
    ),
]
