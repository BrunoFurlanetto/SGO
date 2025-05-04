from django.urls import path

from . import views

urlpatterns = [
    path('coordenacao/monitoria/evento/<int:id_ordem_de_servico>', views.avaliacao_coordenacao_monitoria, name='avaliacao_coordenacao_monitoria')
]
