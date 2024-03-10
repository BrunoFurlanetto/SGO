from django.urls import path

from . import views

urlpatterns = [
    path('orcamento/<int:id_orcamento>/', views.ficha_financeira, name='ficha_financeira'),
    path('orcamento/<int:id_orcamento>/salvar/', views.salvar_ficha_financeiro, name='salvar_ficha_financeira'),
    path('<int:id_ficha_financeira>/revisar/', views.revisar_ficha_financeira, name='revisar_ficha_financeira'),
    path('<int:id_ficha_financeira>/negar/', views.negar_ficha_financeira, name='negar_ficha_financeira'),
    path('<int:id_ficha_financeira>/aprovar/', views.aprovar_ficha_financeira, name='aprovar_ficha_financeira'),
    path('<int:id_ficha_financeira>/editar/', views.editar_ficha_financeira, name='editar_ficha_financeira'),
    path('<int:id_ficha_financeira>/faturar/', views.faturar_ficha_financeira, name='faturar_ficha_financeira'),
    path('orcamento/<int:id_orcamento>/editar/<int:id_ficha_financeira>/salvar/', views.salvar_ficha_financeiro, name='salvar_edicao_ficha_financeira'),
]
