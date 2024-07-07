from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='painel_diretoria'),
    path('infos_clientes_mes_estagios/', views.infos_clientes_mes_estagios, name='infos_clientes_mes_estagios'),
]
