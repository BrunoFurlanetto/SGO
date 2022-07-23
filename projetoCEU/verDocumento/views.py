from datetime import datetime

from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect

from cadastro.funcoesColegio import salvar_equipe_colegio, salvar_locacoes_empresa, salvar_atividades_colegio
from cadastro.funcoesFichaEvento import salvar_atividades_ceu, check_in_and_check_out_atividade, salvar_locacoes_ceu
from cadastro.funcoesPublico import salvar_equipe, salvar_atividades
import cadastro.funcoes
from ordemDeServico.models import OrdemDeServico, CadastroOrdemDeServico
from peraltas.models import FichaDeEvento, CadastroFichaDeEvento, InformacoesAdcionais, CodigosApp, \
    CadastroInfoAdicionais, CadastroCodigoApp
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
    elif tipo_atendimento == 'ordem':
        return redirect('verOrdemDeServico', id_documento)
    elif tipo_atendimento == 'ficha':
        return redirect('verFichaDeEvento', id_documento)


def verRelatorioPublico(request, id_relatorio):
    relatorio = RelatorioDeAtendimentoPublicoCeu.objects.get(id=int(id_relatorio))
    relatorio_publico = RelatorioPublico(instance=relatorio)
    relatorio_publico.id = int(id_relatorio)
    atividades = Atividades.objects.filter(publico=True)
    professores = Professores.objects.all()
    editar = datetime.now().day - relatorio.data_hora_salvo.day < 2 and request.user.first_name == relatorio.equipe[
        'coordenador']
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
    editar = datetime.now().day - colegio.data_hora_salvo.day < 2 and request.user.first_name == colegio.equipe[
        'coordenador']

    if request.method != 'POST':
        return render(request, 'verDocumento/ver-relatorios-colegio.html', {'formulario': relatorio_colegio,
                                                                            'professores': professores,
                                                                            'editar': editar})

    if is_ajax(request):
        return JsonResponse(requests_ajax(request.POST))

    if request.POST.get('acao'):
        ordem = OrdemDeServico.objects.get(instituicao=colegio.instituicao)
        ordem.relatorio_ceu_entregue = False
        ordem.save()

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
            messages.success(request, 'Relatório de atendimento atualizado com sucesso!')
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
        ordem = OrdemDeServico.objects.get(instituicao=empresa.instituicao)
        ordem.relatorio_ceu_entregue = False
        ordem.save()

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
            return render(request, 'verDocumento/ver-relatorios-empresa.html', {'formulario': relatorio_empresa,
                                                                                'professores': professores})
        else:
            messages.success(request, 'Relatório de atendimento atualizado com sucesso!')
            return redirect('dashboard')
    else:
        messages.warning(request, relatorio_empresa.errors)
        return render(request, 'verDocumento/ver-relatorios-empresa.html', {'formulario': relatorio_empresa,
                                                                            'professores': professores, })


def verOrdemDeServico(request, id_ordemDeServico):
    ordem = OrdemDeServico.objects.get(id=int(id_ordemDeServico))
    ordens_de_servico = CadastroOrdemDeServico(instance=ordem)
    ordens_de_servico.id = ordem.id
    id_ficha_de_evento = ordem.ficha_de_evento.id
    coordenador_grupo = request.user == ordem.monitor_responsavel.usuario
    atividades_eco = []
    atividades_peraltas = []

    operacional = User.objects.filter(pk=request.user.id, groups__name='Operacional').exists()

    for atividade in ordem.atividades_eco.all():
        atividades_eco.append(atividade.atividade)

    for atividade in ordem.atividades_peraltas.all():
        atividades_peraltas.append(atividade.atividade)

    atividades_eco = ', '.join(atividades_eco)
    atividades_peraltas = ', '.join(atividades_peraltas)

    if is_ajax(request):
        if request.POST.get('tipo'):
            return JsonResponse(cadastro.funcoes.requests_ajax(request.POST))

        return JsonResponse(requests_ajax(request.POST))

    if request.method != 'POST':
        return render(request, 'verDocumento/ver-ordem-de-servico.html', {'form': ordens_de_servico,
                                                                          'coordenador_grupo': coordenador_grupo,
                                                                          'id_ficha': id_ficha_de_evento,
                                                                          'atividades_eco': atividades_eco,
                                                                          'atividades_peraltas': atividades_peraltas,
                                                                          'colegio': ordem.tipo == 'Colégio',
                                                                          'operacional': operacional})

    if request.POST.get('acao') == 'Sim':
        ficha = FichaDeEvento.objects.get(id=int(ordem.ficha_de_evento.id))
        ficha.os = False
        ficha.save()

        ordem.delete()
        messages.success(request, 'Ordem de serviço excluida com sucesso!')
        return redirect('dashboard')

    ordens_de_servico = CadastroOrdemDeServico(request.POST, request.FILES, instance=ordem)

    if ordens_de_servico.is_valid():
        ordem_de_servico = ordens_de_servico.save(commit=False)

        try:
            salvar_atividades_ceu(request.POST, ordem_de_servico)
            check_in_and_check_out_atividade(ordem_de_servico)
            salvar_locacoes_ceu(request.POST, ordem_de_servico)
            ordens_de_servico.save()
        except:
            messages.error(request, 'Houve um erro inesperado, por favor tente mais tarde.')
            return redirect('dashboard')
        else:
            messages.success(request, 'Ordem de serviço atualizada com sucesso!')
            return redirect('verOrdemDeServico', ordem.id)

    else:
        messages.warning(request, ordens_de_servico.errors)
        return render(request, 'verDocumento/ver-ordem-de-servico.html', {'form': ordens_de_servico,
                                                                          'id_ficha': id_ficha_de_evento,
                                                                          'atividades_eco': atividades_eco,
                                                                          'atividades_peraltas': atividades_peraltas,
                                                                          'colegio': ordem.tipo == 'Colégio',
                                                                          'adm_peraltas': adm_peraltas})


def verFichaDeEvento(request, id_fichaDeEvento):
    ficha = FichaDeEvento.objects.get(id=int(id_fichaDeEvento))
    informacoes = InformacoesAdcionais.objects.get(id=ficha.informacoes_adcionais.id)
    app = CodigosApp.objects.get(id=ficha.codigos_app.id)

    ficha_de_evento = CadastroFichaDeEvento(instance=ficha)
    informacoes_adicionais = CadastroInfoAdicionais(instance=informacoes)
    codigos_app = CadastroCodigoApp(instance=app)

    ficha_de_evento.id = ficha.id
    informacoes_adicionais.lista_de_segurados = ficha.informacoes_adcionais.lista_segurados
    comercial = User.objects.filter(pk=request.user.id, groups__name='Comercial').exists()
    operacional = User.objects.filter(pk=request.user.id, groups__name='Operacional').exists()

    if request.method != 'POST':
        return render(request, 'verDocumento/ver-ficha-de-evento.html', {'form': ficha_de_evento,
                                                                         'formAdicionais': informacoes_adicionais,
                                                                         'formApp': codigos_app,
                                                                         'comercial': comercial,
                                                                         'operacional': operacional})

    if is_ajax(request):
        if request.POST.get('id_ficha_de_evento'):
            return JsonResponse(requests_ajax(request.POST))

        return JsonResponse(cadastro.funcoes.requests_ajax(request.POST))

    if request.POST.get('excluir') == 'Sim':
        try:
            ficha.delete()
            informacoes.delete()
            app.delete()
        except Exception as e:
            messages.error(request, f'Ficha de evento não exlcuida: {e}')
            return redirect('verFichaDeEvento', ficha.id)
        else:
            messages.success(request, 'Ficha de evento excluida com sucesso!')
            return redirect('calendario_eventos')

    ficha_de_evento = CadastroFichaDeEvento(request.POST, instance=ficha)

    if ficha_de_evento.is_valid():

        nova_ficha = ficha_de_evento.save(commit=False)
        nova_ficha.refeicoes = cadastro.funcoes.pegar_refeicoes(request.POST)

        try:
            ficha_de_evento.save()
        except:
            messages.error(request, 'Houve um erro inesperado, por favor tente mais tarde.')
            return redirect('dashboard')
        else:
            messages.success(request, 'Ficha de evento salva com sucesso')
            return redirect('verFichaDeEvento', ficha.id)

    else:
        messages.warning(request, ficha_de_evento.errors)
        return render(request, 'verDocumento/ver-ficha-de-evento.html', {'form': ficha_de_evento,
                                                                         'formAdicionais': informacoes_adicionais,
                                                                         'formApp': codigos_app,
                                                                         'comercial': comercial,
                                                                         'operacional': operacional})
