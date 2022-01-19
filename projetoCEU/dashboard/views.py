from datetime import datetime
from django.db.models import Q
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from cadastro.models import OrdemDeServico, Professores, Tipo
from django.views.decorators.csrf import csrf_exempt
from dashboard.funcoes import contar_atividades, contar_horas, is_ajax
from escala.models import Escala


@csrf_exempt
def dashboard(request):

    # --------------------------- Parte para verificação de autenticação ---------------------------------
    if not request.user.is_authenticated:
        return redirect('login')

    ver_icons = User.objects.filter(pk=request.user.id, groups__name='Colégio').exists()

    if ver_icons:
        return redirect('fichaAvaliacao')
    # ----------------------------------------------------------------------------------------------------

    dados_iniciais = OrdemDeServico.objects.order_by('hora_atividade_1').filter(data_atendimento=datetime.now())
    ordem_de_servico = OrdemDeServico.objects.order_by('hora_atividade_1').filter(
        data_atendimento=request.POST.get('data_selecionada'))
    professor_logado = Professores.objects.get(nome=request.user.first_name)
    # ------------------ Ordens para conta de atividades e horas do mês --------------------
    ordens_usuario = OrdemDeServico.objects.filter(
        Q(coordenador=professor_logado) | Q(professor_2=professor_logado) |
        Q(professor_3=professor_logado) | Q(professor_4=professor_logado)).filter(
        Q(tipo=Tipo.objects.get(tipo='Público')) | Q(tipo=Tipo.objects.get(tipo='Colégio'))).filter(
        data_atendimento__month=datetime.now().month).values()
    ordens_usuario_empresa = OrdemDeServico.objects.filter(
        Q(coordenador=professor_logado) | Q(professor_2=professor_logado)).filter(
        Q(tipo=Tipo.objects.get(tipo='Empresa'))).filter(data_atendimento__month=datetime.now().month).values()
    # --------------------------------------------------------------------------------------
    escalas = Escala.objects.filter(data=datetime.now())

    # ----- Parte para seleção da escala do dia -------
    for escala in escalas:
        equipe_escalada = escala.equipe.split(', ')

    # ------ Parte dos dados mandados para o ajax, para serem exibidos na tabela -------
    data = datetime.now()
    ids = []
    tipos = []
    coordenadores = []
    equipe = []
    instituicoes = []
    dados = [ids, tipos, instituicoes, coordenadores, equipe]

    for campo in ordem_de_servico:
        ids.append(campo.id)
        tipos.append(campo.tipo)
        instituicoes.append(campo.instituicao)
        coordenadores.append(campo.coordenador)
        equipe.append(campo.professor_2)
        equipe.append(campo.professor_3)
        equipe.append(campo.professor_4)

    # ------------------ Parte para chegar no resumo do mês -------------------
    n_atividade = contar_atividades(professor_logado, ordens_usuario.values())
    n_horas = contar_horas(professor_logado, ordens_usuario_empresa.values())
    # -------------------------------------------------------------------------

    if is_ajax(request) and request.method == 'POST':
        return HttpResponse(dados)

    return render(request, 'dashboard/dashboard.html', {'ordemDeServico': dados_iniciais, 'data': data,
                                                        'equipe_escalada': equipe_escalada, 'n_atividades': n_atividade,
                                                        'n_horas': n_horas})
