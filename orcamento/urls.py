from django.urls import path

import projetoCEU
from . import views

urlpatterns = [
    path('', views.calc_budget, name='orcamento'),
    path('nova_tratativa/<str:id_tratativa>/', views.calc_budget, name='nova_tratativa'),
    path('verificar_gerencia/', views.veriricar_gerencia, name='verificar_gerencia')
]
