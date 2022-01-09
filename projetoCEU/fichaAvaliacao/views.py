from datetime import datetime
from time import sleep
from unicodedata import normalize

from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from cadastro.models import OrdemDeServico, Tipo
from django.contrib.auth.models import Group


def fichaAvaliacao(request):
    if not request.user.is_authenticated:
        return redirect('login')
    elif not User.objects.filter(pk=request.user.id, groups__name='Colégio'):
        return redirect('dashboard')

    ordem = OrdemDeServico.objects.filter(instituicao__icontains=request.user.last_name)
    avaliacoes = ['Excelente', 'Ótimo', 'Bom', 'Regular', 'Ruim']
    professores = []

    for item in ordem:
        if item.coordenador not in professores and not None:
            professores.append(item.coordenador)

        if item.professor_2 not in professores and not None:
            professores.append(item.professor_2)

        if item.professor_3 not in professores and not None:
            professores.append(item.professor_3)

        if item.professor_4 not in professores and not None:
            professores.append(item.professor_4)

        professores.remove(None)

    ver_icons = User.objects.filter(pk=request.user.id, groups__name='Colégio').exists()

    if request.method != 'POST':
        return render(request, 'fichaAvaliacao/fichaAvaliacao.html', {'ver': ver_icons, 'avaliacoes': avaliacoes,
                                                                      'ordem': ordem, 'professores': professores})
    else:
        # user = User.objects.get(pk=request.user.id)
        # user.delete()
        # sleep(2)
        # return redirect('logout')
        ...


@csrf_exempt
def solicitarFichaAvaliacao(request):
    if not request.user.is_authenticated:
        return redirect('login')

    colegio = Tipo.objects.get(tipo='Colégio')
    colegios = OrdemDeServico.objects.filter(tipo=colegio)
    selecao = OrdemDeServico.objects.filter(instituicao__iexact=request.POST.get('instituicao'))
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

    if request.is_ajax() and request.method == 'POST':
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
            if instituicao is None:
                raise 'Houve um erro inesperado e não foi possível terminar a solicitação!'
            user = User.objects.create_user(username=login, email=email,
                                            password=senha, first_name='Colégio',
                                            last_name=request.POST.get("instituicao"))
            grupo = Group.objects.get(name='Colégio')
            grupo.user_set.add(user)
            user.save()
            selecao.update(solicitado=True)

            novo_user = {'instituicao': request.POST.get('instituicao'), 'login': login, 'senha': senha, 'email': email}
            chamar = True

            return render(request, 'fichaAvaliacao/solicitacaoAvaliacao.html', {'instituicoes': instituicoes,
                                                                                'chamar': chamar,
                                                                                "novo_user": novo_user})
        except:
            messages.error(request, 'Houve um erro inesperado e não foi possível terminar a solicitação!')
            return render(request, 'fichaAvaliacao/solicitacaoAvaliacao.html', {'instituicoes': instituicoes})
