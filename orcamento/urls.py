from django.urls import path

from . import views

urlpatterns = [
    path('', views.calc_budget, name='orcamento'),
    path('nova_tratativa/<str:id_tratativa>/', views.calc_budget, name='nova_tratativa'),
    path('verificar_gerencia/', views.veriricar_gerencia, name='verificar_gerencia'),
    path('pdf_orcamento/<str:id_tratativa>', views.gerar_pdf, name='pdf_orcamento'),
]
