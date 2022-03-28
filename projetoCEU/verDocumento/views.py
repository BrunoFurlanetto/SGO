from datetime import datetime

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect

from cadastro.funcoesPublico import salvar_equipe, salvar_atividades
from .funcoes import is_ajax, requests_ajax

from cadastro.models import RelatorioDeAtendimentoPublicoCeu, RelatorioDeAtendimentoColegioCeu, \
    RelatorioDeAtendimentoEmpresaCeu, RelatorioPublico
from ceu.models import Atividades, Professores


def verDocumento(request, id_documento, tipo_atendimento):
    if tipo_atendimento == 'Público':
        return redirect('verRelatorioPublico', id_documento)
    elif tipo_atendimento == 'Colégio':
        return redirect('verRelatorioColegio', id_documento)
    elif tipo_atendimento == 'Empresa':
        return redirect('verRelatorioEmpresa', id_documento)


def verRelatorioPublico(request, id_relatorio):
    relatorio = RelatorioDeAtendimentoPublicoCeu.objects.get(id=int(id_relatorio))
    relatorio_publico = RelatorioPublico(instance=relatorio)
    relatorio_publico.id = int(id_relatorio)
    atividades = Atividades.objects.filter(publico=True)
    professores = Professores.objects.all()
    editar = datetime.now().day - relatorio.data_hora_salvo.day < 2
    range_i = range(1, 6)
    range_j = range(1, 5)

    if is_ajax(request):
        return JsonResponse(requests_ajax(request.POST))

    if request.method != 'POST':
        return render(request, 'verDocumento/ver-relatorios-publico.html', {'formulario': relatorio_publico,
                                                                            'rangei': range_i,
                                                                            'rangej': range_j,
                                                                            'atividades': atividades,
                                                                            'professores': professores,
                                                                            'editar': editar})

    if request.POST.get('acao'):
        relatorio.delete()
        messages.success(request, 'Relatório excluido com sucesso!')
        return redirect('dashboard')

    relatorio_publico = RelatorioPublico(request.POST, instance=relatorio)

    if relatorio_publico.is_valid():
        update = relatorio_publico.save(commit=False)
        salvar_equipe(request.POST, update)
        salvar_atividades(request.POST, update)

        try:
            relatorio.save()
        except:
            messages.error(request, 'Houve um erro inesperado, por favor tente mais tarde')
            return render(request, 'verDocumento/ver-relatorios-publico.html', {'formulario': relatorio_publico,
                                                                                'rangei': range_i,
                                                                                'rangej': range_j,
                                                                                'atividades': atividades,
                                                                                'professores': professores,
                                                                                'editar': editar})
        else:
            messages.success(request, 'Relatório de atendimento ao público alterado com sucesso')
            return redirect('dashboard')


def verRelatorioColegio(request, id_relatorio):
    ...


def verRelatorioEmpresa(request, id_relatorio):
    ...


def verOrdemDeServico(request):
    ...
