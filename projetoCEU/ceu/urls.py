from django.urls import path
from . import views

urlpatterns = [
    path('resumo-financeiro/', views.resumo_financeiro_ceu, name='resumo_financeiro_ceu'),
    path('detector-de-bomba/', views.detector_de_bombas, name='detector')
]
