from django.urls import path

import projetoCEU
from . import views

urlpatterns = [
    path('', views.calc_budget, name='orcamento'),
    path('<int:id_orcamento>/', projetoCEU.gerar_pdf.pdf_orcamento, name='pdf_orcamento'),
    path('verificar_gerencia/', views.veriricar_gerencia, name='verificar_gerencia')
]
