from django.shortcuts import render, redirect

from cadastro.models import RelatorioDeAtendimentoPublicoCeu, RelatorioDeAtendimentoColegioCeu, \
    RelatorioDeAtendimentoEmpresaCeu


def verDocumento(request, id_documento, tipo_atendimento):

    if tipo_atendimento == 'Público':
        return redirect('verRelatorioPublico', id_documento)
    elif tipo_atendimento == 'Colégio':
        return redirect('verRelatorioColegio', id_documento)
    elif tipo_atendimento == 'Empresa':
        return redirect('verRelatorioEmpresa', id_documento)


def verRelatorioPublico(request, id_relatorio):
    print(id_relatorio)


def verRelatorioColegio(request, id_relatorio):
    ...


def verRelatorioEmpresa(request, id_relatorio):
    ...


def verOrdemDeServico(request):
    ...
