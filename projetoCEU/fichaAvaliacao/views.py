from datetime import datetime
from unicodedata import normalize
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from cadastro.models import OrdemDeServico, Tipo


def fichaAvaliacao(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method != 'POST':
        return render(request, 'fichaAvaliacao/fichaAvaliacao.html')


@csrf_exempt
def solicitarFichaAvaliacao(request):
    if not request.user.is_authenticated:
        return redirect('login')

    colegio = Tipo.objects.get(tipo='Colégio')
    colegios = OrdemDeServico.objects.filter(tipo=colegio)
    selecao = OrdemDeServico.objects.filter(instituicao__iexact=request.POST.get('instituicao'))

    instituicoes = []
    for escolas in colegios:
        if escolas.instituicao.capitalize() not in instituicoes and not escolas.solicitado:
            instituicoes.append(escolas.instituicao.capitalize())

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

        user = User.objects.create_user(username=login, email=email,
                                        password=senha, first_name='Colégio',
                                        last_name=instituicao[0:i],)
        user.save()
        selecao.update(solicitado=True)
        return redirect('dashboard')
