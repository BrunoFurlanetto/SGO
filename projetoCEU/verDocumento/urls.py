from django.urls import path
from . import views

urlpatterns = [
    path('<str:tipo_atendimento>/<int:id_documento>', views.verDocumento, name='verDocumento'),
    path('relatorio-de-atendimento/publico/<int:id_relatorio>', views.verRelatorioPublico, name='verRelatorioPublico'),
    path('relatorio-de-atendimento/colegio/<int:id_relatorio>', views.verRelatorioColegio, name='verRelatorioColegio'),
    path('relatorio-de-atendimento/empresa/<int:id_relatorio>', views.verRelatorioEmpresa, name='verRelatorioEmpresa'),
    path('ordem/servico/<int:id_ordemDeServico>', views.verOrdemDeServico, name='verOrdemDeServico'),
]
