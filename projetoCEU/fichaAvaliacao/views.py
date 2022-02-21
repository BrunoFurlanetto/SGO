from datetime import datetime
from time import sleep
from unicodedata import normalize
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from cadastro.models import RelatorioDeAtendimentoCeu, Tipo, Atividades, Professores
from django.contrib.auth.models import Group
from dashboard.views import is_ajax
from fichaAvaliacao.models import FichaDeAvaliacaoForm


def fichaAvaliacao(request):
    if not request.user.is_authenticated:
        return redirect('login')
    elif not User.objects.filter(pk=request.user.id, groups__name='Colégio'):
        return redirect('dashboard')

    ver_icons = User.objects.filter(pk=request.user.id, groups__name='Colégio').exists()
    ordens = RelatorioDeAtendimentoCeu.objects.order_by('data_atendimento').filter(instituicao__icontains=request.user.last_name)
    avaliacoes = ['Excelente', 'Ótimo', 'Bom', 'Regular', 'Ruim']
    professores = []
    atividades = []
    formulario = FichaDeAvaliacaoForm()

    # -------------- Testes para separar as atividades sem repetição na mesma data ----------------------------
    for ordem in ordens:
        if {'atividade': ordem.atividade_1, 'data': ordem.data_atendimento} not in atividades:
            atividade = {'atividade': ordem.atividade_1, 'data': ordem.data_atendimento}
            atividades.append(atividade)

        if ordem.atividade_2 is not None and {'atividade': ordem.atividade_2, 'data': ordem.data_atendimento} \
                not in atividades:
            atividade = {'atividade': ordem.atividade_2, 'data': ordem.data_atendimento}
            atividades.append(atividade)

        if ordem.atividade_3 is not None and {'atividade': ordem.atividade_3, 'data': ordem.data_atendimento} \
                not in atividades:
            atividade = {'atividade': ordem.atividade_3, 'data': ordem.data_atendimento}
            atividades.append(atividade)

        if ordem.atividade_4 is not None and {'atividade': ordem.atividade_4, 'data': ordem.data_atendimento} \
                not in atividades:
            atividade = {'atividade': ordem.atividade_4, 'data': ordem.data_atendimento}
            atividades.append(atividade)

    # -------------- Testes para popular a lista dos professores que atenderam sem repetição --------------------------
    for ordem in ordens:
        if ordem.coordenador not in professores and not None:
            professores.append(ordem.coordenador)

        if ordem.professor_2 is not None and ordem.professor_2 not in professores:
            professores.append(ordem.professor_2)

        if ordem.professor_3 is not None and ordem.professor_3 not in professores:
            professores.append(ordem.professor_3)

        if ordem.professor_4 is not None and ordem.professor_4 not in professores:
            professores.append(ordem.professor_4)

    if request.method != 'POST':
        return render(request, 'fichaAvaliacao/fichaAvaliacao.html', {'ver': ver_icons, 'avaliacoes': avaliacoes,
                                                                      'atividades': atividades,
                                                                      'professores': professores,
                                                                      'form': formulario})

    formulario = FichaDeAvaliacaoForm(request.POST)

    # -- Campos que devem ser preenchidos, mas não pelo usuário, mas necessário para validação --
    avaliacao = formulario.save(commit=False)
    avaliacao.instituicao = request.user.last_name

    # --------- Adcionando todas as atividades feitas no banco de dados --------------
    avaliacao.data_atividade_1 = atividades[0]['data']
    avaliacao.atividade_1 = Atividades.objects.get(atividade=atividades[0]['atividade'])

    for i in range(len(atividades)):
        if i == 1:
            avaliacao.data_atividade_2 = atividades[1]['data']
            avaliacao.atividade_2 = Atividades.objects.get(atividade=atividades[1]['atividade'])

        if i == 2:
            avaliacao.data_atividade_3 = atividades[2]['data']
            avaliacao.atividade_3 = Atividades.objects.get(atividade=atividades[2]['atividade'])

        if i == 3:
            avaliacao.data_atividade_4 = atividades[3]['data']
            avaliacao.atividade_4 = Atividades.objects.get(atividade=atividades[3]['atividade'])

        if i == 4:
            avaliacao.data_atividade_5 = atividades[4]['data']
            avaliacao.atividade_5 = Atividades.objects.get(atividade=atividades[4]['atividade'])

        if i == 5:
            avaliacao.data_atividade_6 = atividades[5]['data']
            avaliacao.atividade_6 = Atividades.objects.get(atividade=atividades[5]['atividade'])

        if i == 6:
            avaliacao.data_atividade_7 = atividades[6]['data']
            avaliacao.atividade_7 = Atividades.objects.get(atividade=atividades[6]['atividade'])

        if i == 7:
            avaliacao.data_atividade_8 = atividades[7]['data']
            avaliacao.atividade_8 = Atividades.objects.get(atividade=atividades[7]['atividade'])

    # ------------ Teste para existência de professores para ser adcinoado -------------------
    avaliacao.professor_1 = Professores.objects.get(nome=professores[0])

    for i in range(len(professores)):
        if i == 1:
            avaliacao.professor_2 = Professores.objects.get(nome=professores[1])

        if i == 2:
            avaliacao.professor_3 = Professores.objects.get(nome=professores[2])

        if i == 3:
            avaliacao.professor_4 = Professores.objects.get(nome=professores[3])

        if i == 4:
            avaliacao.professor_5 = Professores.objects.get(nome=professores[4])

        if i == 5:
            avaliacao.professor_6 = Professores.objects.get(nome=professores[5])

    if formulario.is_valid():
        avaliacao.save()
        colegio = RelatorioDeAtendimentoCeu.objects.filter(instituicao__iexact=request.user.last_name)
        colegio.update(entregue=True)
        return redirect('agradecimentos')
    else:
        formulario = FichaDeAvaliacaoForm(request.POST)
        return render(request, 'fichaAvaliacao/fichaAvaliacao.html', {'ver': ver_icons, 'avaliacoes': avaliacoes,
                                                                      'atividades': atividades,
                                                                      'professores': professores,
                                                                      'form': formulario})


@csrf_exempt
def solicitarFichaAvaliacao(request):
    if not request.user.is_authenticated:
        return redirect('login')

    colegio = Tipo.objects.get(tipo='Colégio')
    colegios = RelatorioDeAtendimentoCeu.objects.filter(tipo=colegio)
    selecao = RelatorioDeAtendimentoCeu.objects.filter(instituicao__iexact=request.POST.get('instituicao'))
    instituicoes = []

    if selecao is None:
        messages.error(request, 'Não houve nenhuma seleção!')
        return render(request, 'fichaAvaliacao/solicitacaoAvaliacao.html', {'instituicoes': instituicoes})

    for escolas in colegios:
        if escolas.instituicao.capitalize() not in instituicoes and not escolas.solicitado:
            instituicoes.append(escolas.instituicao.capitalize())

    if selecao is not None:
        equipe = []
        atividades = []
        dados = [equipe, atividades]

        for campo in selecao:
            equipe.append(campo.coordenador)
            equipe.append(campo.professor_2)
            equipe.append(campo.professor_3)
            equipe.append(campo.professor_4)
            atividades.append(campo.atividade_1)
            atividades.append(campo.atividade_2)
            atividades.append(campo.atividade_3)
            atividades.append(campo.atividade_4)
            atividades.append(campo.atividade_5)

    if is_ajax(request) and request.method == 'POST':
        return HttpResponse(dados)

    if request.method != 'POST':
        return render(request, 'fichaAvaliacao/solicitacaoAvaliacao.html', {'instituicoes': instituicoes})
    else:
        i = 0
        for letra in request.POST.get('instituicao'):

            if letra == ' ':
                break

            i += 1

        instituicao = normalize('NFKD', request.POST.get("instituicao")).encode('ASCII', 'ignore').decode('ASCII')

        login = f'Colegio{instituicao[0:i].capitalize()}'
        senha = f'{instituicao[0:i].capitalize()}{datetime.now().year}@'
        email = f'avaliacao_{instituicao[0:i].lower()}@fundacaoceu.com'

        try:
            if instituicao == '':
                messages.error(request, 'Instituição não selecionada!')
                return render(request, 'fichaAvaliacao/solicitacaoAvaliacao.html', {'instituicoes': instituicoes})
            else:
                user = User.objects.create_user(username=login, email=email,
                                                password=senha, first_name='Colégio',
                                                last_name=request.POST.get("instituicao"))
                grupo = Group.objects.get(name='Colégio')
                grupo.user_set.add(user)
                user.save()
                selecao.update(solicitado=True)

                novo_user = {'instituicao': request.POST.get('instituicao'), 'login': login, 'senha': senha,
                             'email': email}
                chamar = True

                return render(request, 'fichaAvaliacao/solicitacaoAvaliacao.html', {'instituicoes': instituicoes,
                                                                                    'chamar': chamar,
                                                                                    "novo_user": novo_user})
        except:
            messages.error(request, 'Houve um erro inesperado e não foi possível terminar a solicitação!')
            return render(request, 'fichaAvaliacao/solicitacaoAvaliacao.html', {'instituicoes': instituicoes})


def agradecimentos(request):
    if not request.user.is_authenticated:
        return redirect('login')
    elif not User.objects.filter(pk=request.user.id, groups__name='Colégio'):
        return redirect('dashboard')

    if request.method != 'POST':
        ver_icons = User.objects.filter(pk=request.user.id, groups__name='Colégio').exists()
        user = User.objects.get(pk=request.user.id)
        user.delete()
        return render(request, 'fichaAvaliacao/agradecimento.html', {'ver': ver_icons})
