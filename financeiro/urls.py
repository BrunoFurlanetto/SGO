from django.urls import path

from . import views

urlpatterns = [
    path('orcamento/<int:id_orcamento>/', views.ficha_financeira, name='ficha_financeira'),
    path('orcamento/<int:id_orcamento>/salvar/', views.salvar_ficha_financeiro, name='salvar_ficha_financeira'),
]
