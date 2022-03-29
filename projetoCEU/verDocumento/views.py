from datetime import datetime

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect

from cadastro.funcoesColegio import salvar_equipe_colegio, salvar_locacoes_empresa, salvar_atividades_colegio
from cadastro.funcoesPublico import salvar_equipe, salvar_atividades
from .funcoes import is_ajax, requests_ajax

from cadastro.models import RelatorioDeAtendimentoPublicoCeu, RelatorioDeAtendimentoColegioCeu, \
    RelatorioDeAtendimentoEmpresaCeu, RelatorioPublico, RelatorioColegio, RelatorioEmpresa
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
    colegio = RelatorioDeAtendimentoColegioCeu.objects.get(id=int(id_relatorio))
    relatorio_colegio = RelatorioColegio(instance=colegio)
    relatorio_colegio.id = int(id_relatorio)
    relatorio_colegio.tipo = colegio.tipo
    professores = Professores.objects.all()
    editar = datetime.now().day - colegio.data_hora_salvo.day < 2 and request.user.first_name == colegio.equipe['coordenador']

    if request.method != 'POST':
        return render(request, 'verDocumento/ver-relatorios-colegio.html', {'formulario': relatorio_colegio,
                                                                            'professores': professores,
                                                                            'editar': editar})

    if is_ajax(request):
        return JsonResponse(requests_ajax(request.POST))

    if request.POST.get('acao'):
        colegio.delete()
        messages.success(request, 'Relatório excluido com sucesso!')
        return redirect('dashboard')

    relatorio_colegio = RelatorioColegio(request.POST, instance=colegio)

    if relatorio_colegio.is_valid():
        relatorio = relatorio_colegio.save(commit=False)
        salvar_equipe_colegio(request.POST, relatorio)
        salvar_atividades_colegio(request.POST, relatorio)

        try:
            relatorio_colegio.save()
        except:
            messages.error(request, 'Houve um erro insperado, por favor tente novamente mais tarde!')
            relatorio_colegio = RelatorioColegio()
            return render(request, 'cadastro/colegio.html', {'formulario': relatorio_colegio,
                                                             'professores': professores})
        else:
            messages.success(request, 'Relatório de atendimento salvo com sucesso!')
            return redirect('dashboard')

    else:
        messages.warning(request, relatorio_colegio.errors)
        return render(request, 'cadastro/colegio.html', {'formulario': relatorio_colegio,
                                                         'professores': professores})


def verRelatorioEmpresa(request, id_relatorio):
    empresa = RelatorioDeAtendimentoEmpresaCeu.objects.get(id=int(id_relatorio))
    relatorio_empresa = RelatorioEmpresa(instance=empresa)
    relatorio_empresa.id = int(id_relatorio)
    relatorio_empresa.tipo = empresa.tipo
    professores = Professores.objects.all()
    editar = datetime.now().day - empresa.data_hora_salvo.day < 2 and request.user.first_name == empresa.equipe[
        'coordenador']

    if request.method != 'POST':
        return render(request, 'verDocumento/ver-relatorios-empresa.html', {'formulario': relatorio_empresa,
                                                                            'professores': professores,
                                                                            'editar': editar})

    if is_ajax(request):
        return JsonResponse(requests_ajax(request.POST))

    if request.POST.get('acao'):
        empresa.delete()
        messages.success(request, 'Relatório excluido com sucesso!')
        return redirect('dashboard')

    relatorio_empresa = RelatorioEmpresa(request.POST, instance=empresa)

    if relatorio_empresa.is_valid():
        relatorio = relatorio_empresa.save(commit=False)
        salvar_equipe_colegio(request.POST, relatorio)
        salvar_locacoes_empresa(request.POST, relatorio)

        if request.POST.get('ativ_1'):
            salvar_atividades_colegio(request.POST, relatorio)

        try:
            relatorio_empresa.save()
        except:
            messages.error(request, 'Houve um erro inesperado, por favor, tente mais tarde')
            relatorio_empresa = RelatorioEmpresa()
            return render(request, 'cadastro/empresa.html', {'formulario': relatorio_empresa,
                                                             'professores': professores})
        else:
            messages.success(request, 'Relatório de atendimento atualizado com sucesso!')
            return redirect('dashboard')
    else:
        messages.warning(request, relatorio_empresa.errors)
        return render(request, 'cadastro/empresa.html', {'formulario': relatorio_empresa,
                                                         'professores': professores,})


def verOrdemDeServico(request):
    ...
