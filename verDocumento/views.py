from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect

from cadastro.funcoesColegio import salvar_equipe_colegio, salvar_locacoes_empresa, salvar_atividades_colegio
from cadastro.funcoesFichaEvento import salvar_atividades_ceu, check_in_and_check_out_atividade, salvar_locacoes_ceu
from cadastro.funcoesPublico import salvar_equipe, salvar_atividades
import cadastro.funcoes
from ordemDeServico.models import OrdemDeServico, CadastroOrdemDeServico
from peraltas.models import FichaDeEvento, CadastroFichaDeEvento, InformacoesAdcionais, CodigosApp, \
    CadastroInfoAdicionais, CadastroCodigoApp, GrupoAtividade, DadosTransporte, CadastroDadosTransporte
from projetoCEU.utils import verificar_grupo, email_error
from .funcoes import is_ajax, requests_ajax, pegar_atividades_e_professores

from cadastro.models import RelatorioDeAtendimentoPublicoCeu, RelatorioDeAtendimentoColegioCeu, \
    RelatorioDeAtendimentoEmpresaCeu, RelatorioPublico, RelatorioColegio, RelatorioEmpresa
from ceu.models import Atividades, Professores, Locaveis


@login_required(login_url='login')
def verDocumento(request, id_documento, tipo_atendimento):
    if tipo_atendimento == 'Público':
        return redirect('verRelatorioPublico', id_documento)
    elif tipo_atendimento == 'Colégio':
        return redirect('verRelatorioColegio', id_documento)
    elif tipo_atendimento == 'Empresa':
        return redirect('verRelatorioEmpresa', id_documento)
    elif tipo_atendimento == 'ficha':
        return redirect('verFichaDeEvento', id_documento)


@login_required(login_url='login')
def verRelatorioPublico(request, id_relatorio):
    relatorio = RelatorioDeAtendimentoPublicoCeu.objects.get(id=int(id_relatorio))
    relatorio_publico = RelatorioPublico(instance=relatorio)
    relatorio_publico.id = int(id_relatorio)
    atividades = Atividades.objects.filter(publico=True)
    professores = Professores.objects.all()
    grupos = verificar_grupo(request.user.groups.all())
    range_j = range(1, 5)
    relatorio_publico.dados_atividades = pegar_atividades_e_professores(relatorio.atividades, 'publico')

    try:
        professor_logado = Professores.objects.get(usuario=request.user)
    except Professores.DoesNotExists:
        editar = False
    except Exception as e:
        email_error(request.user.get_full_name(), e, __name__)
        messages.error(request, f'Houve um erro inesperado: {e}. Tente novamente mais tarde!')
        return redirect('dashboard')
    else:
        editar = datetime.now().day - relatorio.data_hora_salvo.day < 2 and professor_logado.id == relatorio.equipe[
            'coordenador']

    if is_ajax(request):
        return JsonResponse(requests_ajax(request.POST))

    if request.method != 'POST':
        return render(request, 'verDocumento/ver-relatorios-publico.html', {'formulario': relatorio_publico,
                                                                            'equipe': relatorio.equipe,
                                                                            'rangej': range_j,
                                                                            'atividades': atividades,
                                                                            'professores': professores,
                                                                            'editar': editar,
                                                                            'grupos': grupos})

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
        except Exception as e:
            email_error(request.user.get_full_name(), e, __name__)
            messages.error(request, 'Houve um erro inesperado, por favor tente mais tarde')
            return render(request, 'verDocumento/ver-relatorios-publico.html', {'formulario': relatorio_publico,
                                                                                'equipe': relatorio.equipe,
                                                                                'rangej': range_j,
                                                                                'atividades': atividades,
                                                                                'professores': professores,
                                                                                'editar': editar,
                                                                                'grupos': grupos})
        else:
            messages.success(request, 'Relatório de atendimento ao público alterado com sucesso')
            return redirect('dashboard')


@login_required(login_url='login')
def verRelatorioColegio(request, id_relatorio):
    colegio = RelatorioDeAtendimentoColegioCeu.objects.get(id=int(id_relatorio))
    relatorio_colegio = RelatorioColegio(instance=colegio)
    relatorio_colegio.id = int(id_relatorio)
    relatorio_colegio.tipo = colegio.tipo
    professores = Professores.objects.all()
    atividades = Atividades.objects.all()
    locaveis = Locaveis.objects.all()
    grupos = verificar_grupo(request.user.groups.all())
    ativ_realizadas = pegar_atividades_e_professores(colegio.atividades, 'colegio')
    relatorio_colegio.locacoes_realizadas = pegar_atividades_e_professores(dados_atividades=None,
                                                                           tipo_relatorio='empresa',
                                                                           dados_locacoes=colegio.locacoes)

    try:
        professor_logado = Professores.objects.get(usuario=request.user)
    except Professores.DoesNotExists:
        professor_logado = None

    editar = datetime.now().day - colegio.data_hora_salvo.day < 2 and professor_logado.id == colegio.equipe[
        'coordenador']

    if request.method != 'POST':
        return render(request, 'verDocumento/ver-relatorios-colegio.html', {'formulario': relatorio_colegio,
                                                                            'equipe': colegio.equipe,
                                                                            'relatorio_atividades': ativ_realizadas,
                                                                            'professores': professores,
                                                                            'atividades': atividades,
                                                                            'locaveis': locaveis,
                                                                            'editar': editar,
                                                                            'grupos': grupos})

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

        if request.POST.get('loc_1'):
            salvar_locacoes_empresa(request.POST, relatorio)

        try:
            relatorio_colegio.save()
        except Exception as e:
            email_error(request.user.get_full_name(), e, __name__)
            messages.error(request, 'Houve um erro insperado, por favor tente novamente mais tarde!')
            relatorio_colegio = RelatorioColegio()
            return render(request, 'verDocumento/ver-relatorios-colegio.html', {'formulario': relatorio_colegio,
                                                                                'equipe': colegio.equipe,
                                                                                'relatorio_atividades': ativ_realizadas,
                                                                                'professores': professores,
                                                                                'atividades': atividades,
                                                                                'editar': editar,
                                                                                'grupos': grupos})
        else:
            messages.success(request, 'Relatório de atendimento atualizado com sucesso!')
            return redirect('dashboard')

    else:
        messages.warning(request, relatorio_colegio.errors)
        return render(request, 'verDocumento/ver-relatorios-colegio.html', {'formulario': relatorio_colegio,
                                                                            'equipe': colegio.equipe,
                                                                            'relatorio_atividades': ativ_realizadas,
                                                                            'professores': professores,
                                                                            'atividades': atividades,
                                                                            'editar': editar,
                                                                            'grupos': grupos})


@login_required(login_url='login')
def verRelatorioEmpresa(request, id_relatorio):
    empresa = RelatorioDeAtendimentoEmpresaCeu.objects.get(id=int(id_relatorio))
    relatorio_empresa = RelatorioEmpresa(instance=empresa)
    relatorio_empresa.id = int(id_relatorio)
    relatorio_empresa.tipo = empresa.tipo
    professores = Professores.objects.all()
    locaveis = Locaveis.objects.all()
    atividades = Atividades.objects.all()
    grupos = verificar_grupo(request.user.groups.all())
    print(empresa.locacoes)
    relatorio_empresa.relatorio_atividades = pegar_atividades_e_professores(dados_atividades=empresa.atividades,
                                                                            tipo_relatorio='empresa')
    relatorio_empresa.locacoes_realizadas = pegar_atividades_e_professores(dados_atividades=None,
                                                                           tipo_relatorio='empresa',
                                                                           dados_locacoes=empresa.locacoes)

    try:
        professor_logado = Professores.objects.get(usuario=request.user)
    except Professores.DoesNotExists:
        professor_logado = None

    editar = datetime.now().day - empresa.data_hora_salvo.day < 2 and professor_logado.id == empresa.equipe[
        'coordenador']

    if request.method != 'POST':
        return render(request, 'verDocumento/ver-relatorios-empresa.html', {'formulario': relatorio_empresa,
                                                                            'equipe': empresa.equipe,
                                                                            'professores': professores,
                                                                            'locaveis': locaveis,
                                                                            'atividades': atividades,
                                                                            'editar': editar,
                                                                            'grupos': grupos})

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
        except Exception as e:
            email_error(request.user.get_full_name(), e, __name__)
            messages.error(request, 'Houve um erro inesperado, por favor, tente mais tarde')
            relatorio_empresa = RelatorioEmpresa()
            return render(request, 'verDocumento/ver-relatorios-empresa.html', {'formulario': relatorio_empresa,
                                                                                'professores': professores,
                                                                                'grupos': grupos})
        else:
            messages.success(request, 'Relatório de atendimento atualizado com sucesso!')
            return redirect('dashboard')
    else:
        messages.warning(request, relatorio_empresa.errors)
        return render(request, 'verDocumento/ver-relatorios-empresa.html', {'formulario': relatorio_empresa,
                                                                            'professores': professores,
                                                                            'grupos': grupos})


@login_required(login_url='login')
def verFichaDeEvento(request, id_fichaDeEvento):
    ficha = FichaDeEvento.objects.get(id=int(id_fichaDeEvento))
    grupos_atividade = GrupoAtividade.objects.all()
    informacoes = InformacoesAdcionais.objects.get(id=ficha.informacoes_adcionais.id)
    app = CodigosApp.objects.get(id=ficha.codigos_app.id)
    grupos = verificar_grupo(request.user.groups.all())
    ficha_de_evento = CadastroFichaDeEvento(instance=ficha)
    informacoes_adicionais = CadastroInfoAdicionais(instance=informacoes)
    codigos_app = CadastroCodigoApp(instance=app)

    if informacoes.transporte:
        transporte = DadosTransporte.objects.get(id=informacoes.informacoes_transporte.id)
        form_transporte = CadastroDadosTransporte(instance=transporte)
    else:
        transporte = None
        form_transporte = CadastroDadosTransporte()

    ficha_de_evento.id = ficha.id
    informacoes_adicionais.lista_de_segurados = ficha.informacoes_adcionais.lista_segurados
    comercial = User.objects.filter(pk=request.user.id, groups__name='Comercial').exists()
    operacional = User.objects.filter(pk=request.user.id, groups__name='Operacional').exists()

    if request.method != 'POST':
        return render(request, 'verDocumento/ver-ficha-de-evento.html', {'form': ficha_de_evento,
                                                                         'transporte': transporte,
                                                                         'form_transporte': form_transporte,
                                                                         'formAdicionais': informacoes_adicionais,
                                                                         'grupos_atividade': grupos_atividade,
                                                                         'formApp': codigos_app,
                                                                         'comercial': comercial,
                                                                         'operacional': operacional,
                                                                         'grupos': grupos})

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
            email_error(request.user.get_full_name(), e, __name__)
            messages.error(request, f'Ficha de evento não exlcuida: {e}')
            return redirect('verFichaDeEvento', ficha.id)
        else:
            messages.success(request, 'Ficha de evento excluida com sucesso!')
            return redirect('calendario_eventos')

    ficha_de_evento = CadastroFichaDeEvento(request.POST, request.FILES, instance=ficha)

    if ficha_de_evento.is_valid():

        nova_ficha = ficha_de_evento.save(commit=False)
        nova_ficha.refeicoes = cadastro.funcoes.pegar_refeicoes(request.POST)

        try:
            ficha_de_evento.save()
        except Exception as e:
            email_error(request.user.get_full_name(), e, __name__)
            messages.error(request, 'Houve um erro inesperado, por favor tente mais tarde.')
            return redirect('dashboard')
        else:
            messages.success(request, 'Ficha de evento salva com sucesso')
            return redirect('verFichaDeEvento', ficha.id)

    else:
        messages.warning(request, ficha_de_evento.errors)
        return render(request, 'verDocumento/ver-ficha-de-evento.html', {'form': ficha_de_evento,
                                                                         'transporte': transporte,
                                                                         'form_transporte': form_transporte,
                                                                         'formAdicionais': informacoes_adicionais,
                                                                         'grupos_atividade': grupos_atividade,
                                                                         'formApp': codigos_app,
                                                                         'comercial': comercial,
                                                                         'operacional': operacional,
                                                                         'grupos': grupos})
