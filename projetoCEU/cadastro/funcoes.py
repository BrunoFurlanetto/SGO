import datetime
from time import strptime

from django.http import JsonResponse

from cadastro.funcoesColegio import pegar_informacoes_cliente
from ceu.models import Atividades, Professores, Locaveis


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def requests_ajax(requisicao):

    if requisicao.get('cliente'):
        info_cliente = pegar_informacoes_cliente(requisicao.get('cliente'))

        return info_cliente

    if requisicao.get('campo') == 'professor':
        professores_db = Professores.objects.all()
        professores = {}

        for professor in professores_db:
            professores[professor.id] = professor.usuario.first_name

        return professores

    if requisicao.get('campo') == 'atividade':
        atividades_db = Atividades.objects.all()
        atividades = {}

        for atividade in atividades_db:
            atividades[atividade.id] = atividade.atividade

        return atividades

    if requisicao.get('campo') == 'locacao':
        locais_bd = Locaveis.objects.filter(locavel=True)
        locais = {}

        for local in locais_bd:
            locais[local.id] = local.estrutura

        return locais
