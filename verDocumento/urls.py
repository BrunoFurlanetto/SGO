from django.urls import path
from . import views

urlpatterns = [
    path('<str:tipo_atendimento>/<int:id_documento>', views.verDocumento, name='verDocumento'),
    path('relatorio-de-atendimento/colegio/<int:id_relatorio>', views.verRelatorioColegio, name='verRelatorioColegio'),
    path('relatorio-de-atendimento/empresa/<int:id_relatorio>', views.verRelatorioEmpresa, name='verRelatorioEmpresa'),
]
