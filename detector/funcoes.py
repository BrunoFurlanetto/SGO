from datetime import datetime, timedelta
from random import sample
import re

from ceu.models import Atividades, Locaveis, Professores
from detector.models import DetectorDeBombas
from escala.models import Escala
from ordemDeServico.models import OrdemDeServico
from peraltas.models import ClienteColegio


lista_cores = ['#007EC1', '#FCC607', '#FC1416', '#53C20A', '#C24313', '#C2131F', '#E6077A', '#FE4E08', '#20B099']


def pegar_dados_evento(dados_detector, editando):
    lista_id_clientes = list(map(int, dados_detector.getlist('id_grupos[]')))
    cores_escolhidas = sample(lista_cores, k=len(lista_id_clientes))
    data_inicio = datetime.strptime(dados_detector.get('data_inicio'), '%Y-%m-%d')
    data_final = datetime.strptime(dados_detector.get('data_final'), '%Y-%m-%d')
    atividades = []
    locacoes = []

    for i, id_cliente in enumerate(lista_id_clientes):
        ordens = (OrdemDeServico.objects.filter(escala_ceu=True)
                  .filter(ficha_de_evento__cliente__id=id_cliente)
                  .filter(check_in_ceu__date__gte=dados_detector.get('data_inicio'),
                          check_in_ceu__date__lte=dados_detector.get('data_final'))
                  )

        for ordem in ordens:
            if ordem.atividades_ceu:
                for atividade in ordem.atividades_ceu.values():
                    data_atividade = datetime.strptime(atividade['data_e_hora'], '%Y-%m-%d %H:%M')

                    if data_inicio.date() <= data_atividade.date() <= data_final.date():
                        atividade_bd = Atividades.objects.get(atividade=atividade['atividade'])

                        atividades.append({
                            'atividade': {'id': atividade_bd.id,
                                          'nome': atividade['atividade'],
                                          'qtd': atividade['participantes']},
                            'inicio_atividade': atividade['data_e_hora'],
                            'fim_atividade': (data_atividade + atividade_bd.duracao).strftime('%Y-%m-%d %H:%M'),
                            'color': cores_escolhidas[i],
                            'grupo': {'id': ordem.ficha_de_evento.cliente.id,
                                      'nome': ordem.ficha_de_evento.cliente.nome_fantasia}
                        })

            if ordem.locacao_ceu:
                for espaco in ordem.locacao_ceu.values():
                    local_bd = Locaveis.objects.get(local__estrutura=espaco['espaco'])

                    locacoes.append({
                        'local': {'id': local_bd.id, 'nome': espaco['espaco']},
                        'check_in': espaco['check_in'],
                        'check_out': espaco['check_out'],
                        'color': cores_escolhidas[i],
                        'grupo': {'id': ordem.ficha_de_evento.cliente.id,
                                  'nome': ordem.ficha_de_evento.cliente.nome_fantasia}
                    })

    if editando == 'true':
        detector = DetectorDeBombas.objects.get(id=int(dados_detector.get('id_detector')))
        professores_atividades = {}

        for key, value in detector.dados_atividades.items():
            if 'professor' in key:
                professores_atividades[key] = value

        dados_eventos = {
            'atividades': atividades,
            'locacoes': locacoes,
            'professores': professores_atividades
        }

        return dados_eventos

    dados_eventos = {
        'atividades': atividades,
        'locacoes': locacoes
    }

    return dados_eventos


def veririficar_escalas(data_inicio, data_final):
    datas_sem = []
    dias_evento = data_final.day - data_inicio.day

    for dia in range(0, dias_evento + 1):
        data_teste = data_inicio + timedelta(days=dia)
        escala = Escala.objects.filter(data_escala=data_teste)

        if len(escala) == 0:
            datas_sem.append(data_teste.strftime('%Y-%m-%d'))

    return datas_sem


def juntar_dados_detector(dados):
    grupos = []
    dados_atividades = {}
    i = 1

    for key, value in dados.items():
        if key == f'grupo_{i}':
            cliente = ClienteColegio.objects.get(id=int(value))
            dados_atividades[f'grupo_{i}'] = cliente.nome_fantasia
            grupos.append(cliente.id)
            i += 1
        else:
            if key != 'csrfmiddlewaretoken' and key != 'inicio' and key != 'final':
                try:
                    list(map(int, dados.getlist(key)))
                except ValueError:
                    dados_atividades[key] = value
                else:
                    if len(list(map(int, dados.getlist(key)))) != 1:
                        dados_atividades[key] = list(map(int, dados.getlist(key)))
                    else:
                        dados_atividades[key] = int(value)

    return grupos, dados_atividades


def pegar_escalas(dados_eventos):
    escalados = []
    data_inicio = datetime.strptime(dados_eventos.get('data_inicio'), '%Y-%m-%d').date()
    data_final = datetime.strptime(dados_eventos.get('data_final'), '%Y-%m-%d').date()
    datas_sem_professor = veririficar_escalas(
        datetime.strptime(dados_eventos.get('data_inicio'), '%Y-%m-%d'),
        datetime.strptime(dados_eventos.get('data_final'), '%Y-%m-%d')
    )
    data = data_inicio

    while data <= data_final:
        professores_escalados = []
        try:
            escala = Escala.objects.get(data_escala=data)
        except Escala.DoesNotExist:
            ...
        else:
            for id_professor in escala.equipe.values():
                professor = Professores.objects.get(id=id_professor)
                professores_escalados.append({'id': professor.id, 'nome': professor.usuario.get_full_name()})

        escalados.append({'data': data, 'escalados': professores_escalados})

        data += timedelta(days=1)

    escalados.append({'datas_sem': datas_sem_professor})

    return escalados


def tratar_dados_detector_selecionado(detector_selecionado):
    n_grupos = len(detector_selecionado.grupos.all())
    cores_legenda = sample(lista_cores, k=n_grupos)
    data_1 = detector_selecionado.data_inicio
    data_2 = detector_selecionado.data_final
    intervalo = (data_2.day - data_1.day) + 1
    grupos = {}
    atividades = []

    for i, grupo in enumerate(detector_selecionado.grupos.all(), start=1):
        grupos[grupo.nome_fantasia] = cores_legenda[i - 1]
        ordem_de_servico = OrdemDeServico.objects.get(ficha_de_evento__cliente__id=grupo.id,
                                                      check_in_ceu__date__gte=detector_selecionado.data_inicio)
        j = 1

        while True:
            id_atividade = detector_selecionado.dados_atividades.get(f'atividade_{j}_grupo_{i}')
            id_espaco = detector_selecionado.dados_atividades.get(f'locacao_{j}_grupo_{i}')

            if id_atividade is None and id_espaco is None:
                break

            if id_atividade:
                atividade_bd = Atividades.objects.get(id=id_atividade)
                termino_atividade = datetime.strptime(
                    detector_selecionado.dados_atividades.get(f'data_e_hora_atividade_{j}_grupo_{i}'),
                    '%Y-%m-%d %H:%M'
                ) + atividade_bd.duracao
                professores = professores_atividade(
                    detector_selecionado.dados_atividades.get(f'professores_atividade_{j}_grupo_{i}')
                )

                atividades.append({
                    'title': atividade_bd.atividade,
                    'start': detector_selecionado.dados_atividades.get(f'data_e_hora_atividade_{j}_grupo_{i}'),
                    'description': ", ".join(professores),
                    'end': termino_atividade.strftime('%Y-%m-%d %H:%M'),
                    'color': cores_legenda[i - 1],
                })

            if id_espaco:
                espaco = Locaveis.objects.get(id=id_espaco)
                professores = professores_atividade(
                    detector_selecionado.dados_atividades.get(f'professores_locacao_{j}_grupo_{i}')
                )

                atividades.append({
                    'title': espaco.local.estrutura,
                    'start': detector_selecionado.dados_atividades.get(f'check_in_locacao_{j}_grupo_{i}'),
                    'description': ", ".join(professores),
                    'end': detector_selecionado.dados_atividades.get(f'check_out_locacao_{j}_grupo_{i}'),
                    'color': cores_legenda[i - 1]
                })

            j += 1

    dados_detector = {'grupos': grupos, 'events': atividades, 'datas': [data_1, intervalo]}
    return dados_detector


def professores_atividade(id_professores):
    professores = []

    if isinstance(id_professores, list):
        for id_professor in id_professores:
            professor = Professores.objects.get(id=id_professor)
            professores.append(professor.usuario.get_full_name())
    else:
        professor = Professores.objects.get(id=id_professores)
        professores.append(professor.usuario.get_full_name())

    return professores
