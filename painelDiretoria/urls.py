from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='painel_diretoria'),
    path('estatisticas/monitoria/diarias/', views.estatisticas_monitoria, name='estatisticas_monitoria'),
    path('infos_clientes_mes_estagios/', views.infos_clientes_mes_estagios, name='infos_clientes_mes_estagios'),
    path('infos_produtos_estagios/', views.infos_produtos_estagios, name='infos_produtos_estagios'),
]
