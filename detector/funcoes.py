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

    if editando == 'false':
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

        dados_eventos = {
            'atividades': atividades,
            'locacoes': locacoes
        }

        return dados_eventos
    else:
        detector = DetectorDeBombas.objects.get(id=int(dados_detector.get('id_detector')))
        professores_atividades = {}

        for grupo_n, id_grupo in enumerate(detector.grupos.all(), start=1):
            try:
                ...
            except:
                ...

        dados_eventos = {
            'atividades': atividades,
            'locacoes': locacoes,
            'professores': professores_atividades
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
    chaves = []
    n_grupos = 1

    for key, value in dados.items():
        chaves.append(key)

        if key == f'grupo_{n_grupos}':
            cliente = ClienteColegio.objects.get(id=int(value))
            dados_atividades[f'grupo_{n_grupos}'] = {'id_grupo': cliente.id}
            grupos.append(cliente.id)
            n_grupos += 1

    for grupo in range(1, n_grupos + 1):
        atividade_i = 1
        locacao_i = 1

        for chave in chaves:
            if re.search(f'^atividade_._grupo_{grupo}$', chave):
                lista_professores = list(map(int, dados.getlist(f'professores_{chave}')))
                atividade = Atividades.objects.get(id=int(dados.get(chave)))
                inicio_atividade = datetime.strptime(dados.get(f'data_e_hora_{chave}'), '%Y-%m-%d %H:%M')
                fim_atividade = (inicio_atividade + atividade.duracao).strftime('%Y-%m-%d %H:%M')

                dados_atividades[f'grupo_{grupo}'][f'atividade_{atividade_i}'] = {
                    'id_atividade': int(dados.get(chave)),
                    'inicio': dados.get(f'data_e_hora_{chave}'),
                    'fim': fim_atividade,
                    'participantes': int(dados.get(f'qtd_{chave}')),
                    'professores': lista_professores[0] if len(lista_professores) == 1 else lista_professores
                }

                atividade_i += 1

            if re.search(f'^locacao_._grupo_{grupo}$', chave):
                lista_professores = list(map(int, dados.getlist(f'professores_{chave}')))

                dados_atividades[f'grupo_{grupo}'][f'locacao_{locacao_i}'] = {
                    'id_espaco': int(dados.get(chave)),
                    'check_in': dados.get(f'check_in_{chave}'),
                    'check_out': dados.get(f'check_out_{chave}'),
                    'professores': lista_professores[0] if len(lista_professores) == 1 else lista_professores
                }

                locacao_i += 1

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
        j = 1

        while True:
            try:
                id_atividade = detector_selecionado.dados_atividades[f'grupo_{i}'][f'atividade_{j}']['id_atividade']
            except KeyError:
                id_atividade = None

            try:
                id_espaco = detector_selecionado.dados_atividades[f'grupo_{i}'][f'locacao_{j}']['id_espaco']
            except KeyError:
                id_espaco = None

            if id_atividade is None and id_espaco is None:
                break

            if id_atividade:
                atividade_bd = Atividades.objects.get(id=id_atividade)
                lista_professores = detector_selecionado.dados_atividades[f'grupo_{i}'][f'atividade_{j}']['professores']
                professores = []

                try:
                    len(lista_professores)
                except TypeError:
                    professor = Professores.objects.get(id=lista_professores)
                    professores = [professor.usuario.get_full_name()]
                else:
                    for id_professor in lista_professores:
                        professor = Professores.objects.get(id=id_professor)
                        professores.append(professor.usuario.get_full_name())

                atividades.append({
                    'title': atividade_bd.atividade,
                    'start': detector_selecionado.dados_atividades[f'grupo_{i}'][f'atividade_{j}']['inicio'],
                    'description': ", ".join(professores),
                    'end': detector_selecionado.dados_atividades[f'grupo_{i}'][f'atividade_{j}']['fim'],
                    'color': cores_legenda[i - 1],
                })

            if id_espaco:
                espaco = Locaveis.objects.get(id=id_espaco)
                lista_professores = detector_selecionado.dados_atividades[f'grupo_{i}'][f'locacao_{j}']['professores']
                professores = []

                try:
                    len(lista_professores)
                except TypeError:
                    professor = Professores.objects.get(id=lista_professores)
                    professores = [professor.usuario.get_full_name()]
                else:
                    for id_professor in lista_professores:
                        professor = Professores.objects.get(id=id_professor)
                        professores.append(professor.usuario.get_full_name())

                atividades.append({
                    'title': espaco.local.estrutura,
                    'start': detector_selecionado.dados_atividades[f'grupo_{i}'][f'locacao_{j}']['check_in'],
                    'description': ", ".join(professores),
                    'end': detector_selecionado.dados_atividades[f'grupo_{i}'][f'locacao_{j}']['check_out'],
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


def salvar_alteracoes_de_atividade_locacao(dados):
    detector_alterado = DetectorDeBombas.objects.get(id=int(dados.get('id_detector')))
    dados_ativ = detector_alterado.dados_atividades

    if dados.get('atividade_excluida') == 'true':
        dados_ativ.pop(dados.get('atividade_locacao_alterada'))
        atividade_excluida(dados_ativ, detector_alterado, dados)
        detector_alterado.observacoes += dados.get("observacoes_da_alteracao")
        # detector_alterado.save()
        return

    if dados.get('locacao_excluida') == 'true':
        dados_ativ.pop(dados.get('atividade_locacao_alterada'))
        locacao_excluida(dados_ativ, detector_alterado, dados)
        detector_alterado.observacoes += dados.get("observacoes_da_alteracao")
        # detector_alterado.save()
        return

    if dados.get('altividade_nova') != '':
        atividade = Atividades.objects.get(id=int(dados.get('altividade_atual')))
        data_hora_atividade = datetime.strptime(dados.get('data_hora_atividade_atual'), '%Y-%m-%dT%H:%M')
        data_e_hora_formatada = data_hora_atividade.strftime('%x %X')
        detector_alterado.observacoes += f'\nAlteração de {atividade.atividade} de {data_e_hora_formatada} : '
        detector_alterado.dados_atividades[dados.get('atividade_locacao_alterada')] = dados.get('altividade_nova')
        detector_alterado.dados_atividades[f'data_e_hora_{dados.get("atividade_locacao_alterada")}'] = dados.get('data_hora_atividade_nova')

    if dados.get('espaco_novo') != '':
        espaco = Locaveis.objects.get(id=int(dados.get('espaco_atual')))
        check_in_locacao = datetime.strptime(dados.get('check_in_atual'), '%Y-%m-%dT%H:%M')
        check_in_formatada = check_in_locacao.strftime('%x %X')
        detector_alterado.observacoes += f'\nLocação do(a) {espaco.local.estrutura} de {check_in_formatada} alterado: '
        dados_ativ[dados.get('atividade_locacao_alterada')] = dados.get('altividade_nova')
        dados_ativ[f'check_in_{dados.get("atividade_locacao_alterada")}'] = dados.get('check_in_novo')
        dados_ativ[f'chekc_out_{dados.get("atividade_locacao_alterada")}'] = dados.get('check_out_novo')

    detector_alterado.observacoes += dados.get("observacoes_da_alteracao")

    if len(list(map(int, dados.get('professores_atividade_nova')))) != 1:
        dados_ativ[f'professores_{dados.get("atividade_locacao_alterada")}'] = list(map(
            int, dados.getlist('professores_atividade_nova')))
    else:
        dados_ativ[f'professores_{dados.get("atividade_locacao_alterada")}'] = dados.get('professores_atividade_nova')

    detector_alterado.save()
    return


def atividade_excluida(dados_ativ, detector_alterado, dados):
    atividade = Atividades.objects.get(id=int(dados.get('altividade_atual')))
    data_hora_atividade = datetime.strptime(dados.get('data_hora_atividade_atual'), '%Y-%m-%dT%H:%M')
    data_e_hora_formatada = data_hora_atividade.strftime('%x %X')
    detector_alterado.observacoes += f'\n{atividade.atividade} de {data_e_hora_formatada} excluída: '

    if dados.get('espaco_novo') != '':
        n_locacao = 0
        lista_teste = dados.get('atividade_locacao_alterada').split('_')
        grupo = f'{lista_teste[2]}_{lista_teste[3]}'

        for key in dados_ativ.keys():
            if re.search(f'^locacao.*{grupo}$', key):
                n_locacao += 1

        if n_locacao == 0:
            dados_ativ[f'locacao_1_{grupo}'] = dados.get('espaco_novo')
            dados_ativ[f'check_in_locacao_1_{grupo}'] = dados.get('check_in_novo')
            dados_ativ[f'check_out_locacao_1_{grupo}'] = dados.get('check_out_novo')
            dados_ativ[f'professores_locacao_1_{grupo}'] = dados.get('professores_atividade_nova')
        else:
            dados_ativ[f'locacao_{n_locacao + 1}_{grupo}'] = dados.get('espaco_novo')
            dados_ativ[f'check_in_locacao_{n_locacao + 1}_{grupo}'] = dados.get('check_in_novo')
            dados_ativ[f'check_out_locacao_{n_locacao + 1}_{grupo}'] = dados.get('check_out_novo')
            dados_ativ[f'professores_locacao_{n_locacao + 1}_{grupo}'] = dados.get('professores_atividade_nova')

        renumerar_atividades(dados_ativ, grupo, 'atividade')

    return


def locacao_excluida(dados_ativ, detector_alterado, dados):
    espaco = Locaveis.objects.get(id=int(dados.get('espaco_atual')))
    check_in_locacao = datetime.strptime(dados.get('check_in_atual'), '%Y-%m-%dT%H:%M')
    check_in_formatada = check_in_locacao.strftime('%x %X')
    detector_alterado.observacoes += f'\nLocação do(a) {espaco.local.estrutura} de {check_in_formatada} excluída: '

    if dados.get('altividade_nova') != '':
        n_atividade = 0
        lista_teste = dados.get('atividade_locacao_alterada').split('_')
        grupo = f'{lista_teste[2]}_{lista_teste[3]}'

        for key in dados_ativ.keys():
            if re.search(f'^atividade.*{grupo}$', key):
                n_atividade += 1

        if n_atividade == 0:
            dados_ativ[f'atividade_1_{grupo}'] = dados.get('altividade_nova')
            dados_ativ[f'data_e_hora_atividade_1_{grupo}'] = dados.get('data_hora_atividade_nova')
            dados_ativ[f'professores_atividade_1_{grupo}'] = dados.get('professores_atividade_nova')
        else:
            dados_ativ[f'atividade_{n_atividade + 1}_{grupo}'] = dados.get('altividade_nova')
            dados_ativ[f'data_e_hora_atividade_{n_atividade + 1}_{grupo}'] = dados.get('data_hora_atividade_nova')
            dados_ativ[f'professores_atividade_{n_atividade + 1}_{grupo}'] = dados.get('professores_atividade_nova')

        renumerar_atividades(dados_ativ, grupo, 'locacao')

    return


def renumerar_atividades(dados_ativ, grupo, atividade_locacao):
    n_atividade = 0

    for key in dados_ativ.keys():
        if re.search(f'^{atividade_locacao}.*{grupo}$', key):
            n_atividade += 1
            dados_ativ[f'{atividade_locacao}_{n_atividade}_{grupo}'] = dados_ativ.pop(key)
            dados_ativ[f'professores_{atividade_locacao}_{n_atividade}_{grupo}'] = dados_ativ.pop(f'profesores_{key}')

            if atividade_locacao == 'atividade':
                dados_ativ[f'data_e_hora_atividade_{n_atividade}_{grupo}'] = dados_ativ.pop(f'data_e_hora_{key}')
            else:
                dados_ativ[f'check_in_locacao_{n_atividade}_{grupo}'] = dados_ativ.pop(f'check_in_{key}')
                dados_ativ[f'check_out_locacao_{n_atividade}_{grupo}'] = dados_ativ.pop(f'check_out_{key}')
