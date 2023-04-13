from django.urls import path
from . import views

urlpatterns = [
    path('', views.calc_budget, name='teste_orcamento')
]
