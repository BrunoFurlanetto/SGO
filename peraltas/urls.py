from django.urls import path
from . import views

urlpatterns = [
    path('sgo/empresas/', views.empresas_sgo, name='retornar_empresas_sgo'),
    path('sgo/responsaveis/', views.responsaveis_sgo, name='retornar_responsaveis_sgo'),
    path('sgo/fichas_evento/', views.fichas_sgo, name='retornar_fichas_sgo'),
]
