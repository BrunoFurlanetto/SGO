from datetime import datetime, timedelta
from random import sample
import re

from ceu.models import Atividades, Locaveis, Professores
from detector.models import DetectorDeBombas
from escala.models import Escala
from ordemDeServico.models import OrdemDeServico
from peraltas.models import ClienteColegio, AtividadesEco

lista_cores = ['#007EC1', '#FCC607', '#FC1416', '#53C20A', '#C24313', '#C2131F', '#E6077A', '#FE4E08', '#20B099']


def pegar_dados_evento(dados_detector, editando, setor):
    lista_id_clientes = list(map(int, dados_detector.getlist('id_grupos[]')))
    cores_escolhidas = sample(lista_cores, k=len(lista_id_clientes))
    data_inicio = datetime.strptime(dados_detector.get('data_inicio'), '%Y-%m-%d')
    data_final = datetime.strptime(dados_detector.get('data_final'), '%Y-%m-%d')
    atividades_ceu = []
    atividades_acampamento = []
    atividades_extra = []
    locacoes = []

    if editando == 'false':
        for i, id_cliente in enumerate(lista_id_clientes):
            if setor == 'CEU':
                ordens = OrdemDeServico.objects.filter(
                    ficha_de_evento__cliente__id=id_cliente,
                    check_in_ceu__date__gte=data_inicio,
                    check_in_ceu__date__lte=data_final
                )
            else:
                ordens = OrdemDeServico.objects.filter(
                    ficha_de_evento__cliente__id=id_cliente,
                    check_in__date__gte=data_inicio.date(),
                    check_in__date__lte=data_final.date()
                )

            for ordem in ordens:
                if ordem.atividades_ceu:
                    for atividade in ordem.atividades_ceu.values():
                        data_atividade = datetime.strptime(atividade['data_e_hora'], '%Y-%m-%d %H:%M')

                        if data_inicio.date() <= data_atividade.date() <= data_final.date():
                            atividade_bd = Atividades.objects.get(id=atividade['atividade'])

                            atividades_ceu.append({
                                'atividade': {
                                    'id': atividade_bd.id,
                                    'nome': atividade_bd.atividade,
                                    'qtd': atividade['participantes']
                                },
                                'inicio_atividade': atividade['data_e_hora'],
                                'fim_atividade': (data_atividade + atividade_bd.duracao).strftime('%Y-%m-%d %H:%M'),
                                'color': cores_escolhidas[i],
                                'grupo': {
                                    'id': ordem.ficha_de_evento.cliente.id,
                                    'nome': ordem.ficha_de_evento.cliente.nome_fantasia
                                }
                            })

                if ordem.locacao_ceu:
                    for espaco in ordem.locacao_ceu.values():
                        local_bd = Locaveis.objects.get(id=espaco['espaco'])
                        locacoes.append({
                            'local': {
                                'id': local_bd.id,
                                'nome': local_bd.local.estrutura,
                                'qtd': espaco['participantes']
                            },
                            'check_in': espaco['check_in'],
                            'check_out': espaco['check_out'],
                            'color': cores_escolhidas[i],
                            'grupo': {
                                'id': ordem.ficha_de_evento.cliente.id,
                                'nome': ordem.ficha_de_evento.cliente.nome_fantasia
                            }
                        })

                if setor == 'Peraltas':
                    if ordem.atividades_eco:
                        for atividade in ordem.atividades_eco.values():
                            data_atividade = datetime.strptime(atividade['data_e_hora'], '%Y-%m-%d %H:%M')

                            if data_inicio.date() <= data_atividade.date() <= data_final.date():
                                atividade_bd = AtividadesEco.objects.get(id=atividade['atividade'])

                                atividades_extra.append({
                                    'atividade': {
                                        'id': atividade_bd.id,
                                        'nome': atividade_bd.nome_atividade_eco,
                                        'qtd': atividade['participantes']
                                    },
                                    'inicio_atividade': atividade['data_e_hora'],
                                    'fim_atividade': (data_atividade + atividade_bd.duracao).strftime('%Y-%m-%d %H:%M'),
                                    'color': cores_escolhidas[i],
                                    'grupo': {
                                        'id': ordem.ficha_de_evento.cliente.id,
                                        'nome': ordem.ficha_de_evento.cliente.nome_fantasia
                                    }
                                })

                        if len(ordem.atividades_peraltas.all()) != 0:
                            for atividade in ordem.atividades_peraltas.all():
                                atividades_acampamento.append({
                                    'id': atividade.id,
                                    'nome': atividade.nome_atividade,
                                    'duracao': atividade.duracao,
                                    'color': cores_escolhidas[i],
                                    'grupo': {
                                        'id': ordem.ficha_de_evento.cliente.id,
                                        'nome': ordem.ficha_de_evento.cliente.nome_fantasia
                                    }
                                })

        dados_eventos = {
            'atividades': atividades_ceu,
            'locacoes': locacoes,
            'atividades_extra': atividades_extra,
            'atividades_acampamento': atividades_acampamento
        }

        return dados_eventos
    else:
        detector = DetectorDeBombas.objects.get(id=int(dados_detector.get('id_detector')))
        dados_atividades = detector.dados_atividades
        professores_atividades = {}

        for grupo_n, grupo in enumerate(detector.grupos.all(), start=1):
            atividade_i = 1
            local_i = 1

            while True:
                try:
                    id_atividade = dados_atividades[f'grupo_{grupo_n}'][f'atividade_{atividade_i}']['id_atividade']
                except KeyError:
                    id_atividade = None

                try:
                    id_local = dados_atividades[f'grupo_{grupo_n}'][f'locacao_{local_i}']['id_espaco']
                except KeyError:
                    id_local = None

                if id_atividade is None and id_local is None:
                    break

                if id_atividade:
                    atividade = Atividades.objects.get(id=id_atividade)
                    cliente = ClienteColegio.objects.get(id=grupo.id)
                    qtd = dados_atividades[f'grupo_{grupo_n}'][f'atividade_{atividade_i}']['participantes']
                    atividades_ceu.append({
                        'atividade': {
                            'id': id_atividade,
                            'nome': atividade.atividade,
                            'qtd': qtd
                        },
                        'inicio_atividade': dados_atividades[f'grupo_{grupo_n}'][f'atividade_{atividade_i}']['inicio'],
                        'fim_atividade': dados_atividades[f'grupo_{grupo_n}'][f'atividade_{atividade_i}']['fim'],
                        'color': cores_escolhidas[grupo_n - 1],
                        'grupo': {
                            'id': grupo.id,
                            'nome': cliente.nome_fantasia
                        }
                    })

                    professores_atividades[
                        f'professores_atividade_{atividade_i}_grupo_{grupo_n}'
                    ] = dados_atividades[f'grupo_{grupo_n}'][f'atividade_{atividade_i}']['professores']

                    atividade_i += 1

                if id_local:
                    espaco = Locaveis.objects.get(id=id_local)
                    cliente = ClienteColegio.objects.get(id=grupo.id)
                    locacoes.append({
                        'local': {
                            'id': id_local,
                            'nome': espaco.local.estrutura,
                            'qtd': dados_atividades[f'grupo_{grupo_n}'][f'locacao_{local_i}']['participantes']
                        },
                        'check_in': dados_atividades[f'grupo_{grupo_n}'][f'locacao_{local_i}']['check_in'],
                        'check_out': dados_atividades[f'grupo_{grupo_n}'][f'locacao_{local_i}']['check_out'],
                        'color': cores_escolhidas[grupo_n - 1],
                        'grupo': {
                            'id': grupo.id,
                            'nome': cliente.nome_fantasia
                        }
                    })

                    professores_atividades[
                        f'professores_locacao_{local_i}_grupo_{grupo_n}'
                    ] = dados_atividades[f'grupo_{grupo_n}'][f'locacao_{local_i}']['professores']

                    local_i += 1

        dados_eventos = {
            'atividades_ceu': atividades_ceu,
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
                    'participantes': dados.get(f'qtd_{chave}'),
                    'professores': lista_professores[0] if len(lista_professores) == 1 else lista_professores
                }

                locacao_i += 1

    return grupos, dados_atividades


def pegar_escalas(dados_eventos):
    escalados = []
    data_inicio = datetime.strptime(dados_eventos.get('data_inicio'), '%Y-%m-%d').date()
    data_final = datetime.strptime(dados_eventos.get('data_final'), '%Y-%m-%d').date()
    data = data_inicio
    datas_sem_professor = []

    while data <= data_final:
        professores_escalados = []
        try:
            escala = Escala.objects.get(data_escala=data)
        except Escala.DoesNotExist:
            datas_sem_professor.append(data.strftime('%Y-%m-%d'))
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
                professores = retornar_nome_de_professores(lista_professores)

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
                professores = retornar_nome_de_professores(lista_professores)

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


def salvar_alteracoes_de_atividade_locacao(dados):
    detector_alterado = DetectorDeBombas.objects.get(id=int(dados.get('id_detector')))
    dados_ativ = detector_alterado.dados_atividades
    atividade_alterada_fatiada = dados.get("atividade_locacao_alterada").split("_")
    grupo_alterado = f'grupo_{atividade_alterada_fatiada[3]}'
    atividade_alterada = f'{atividade_alterada_fatiada[0]}_{atividade_alterada_fatiada[1]}'
    lista_professores = list(map(int, dados.getlist('professores_atividade_nova')))

    if dados.get('atividade_excluida') == 'true':
        dados_ativ[grupo_alterado].pop(atividade_alterada)
        atividade_excluida(dados_ativ, detector_alterado, dados)
        detector_alterado.observacoes += dados.get("observacoes_da_alteracao")
        detector_alterado.save()
        return

    if dados.get('locacao_excluida') == 'true':
        dados_ativ[grupo_alterado].pop(atividade_alterada)
        locacao_excluida(dados_ativ, detector_alterado, dados)
        detector_alterado.observacoes += dados.get("observacoes_da_alteracao")
        detector_alterado.save()
        return

    if dados.get('altividade_nova') != '':
        # Dados da atividade antiga
        atividade_velha = Atividades.objects.get(id=int(dados.get('altividade_atual')))
        inicio_atividade_velha = datetime.strptime(dados.get('data_hora_atividade_atual'), '%Y-%m-%dT%H:%M')
        inicio_velha_formatado = inicio_atividade_velha.strftime('%d/%m/%y às %H:%M')
        detector_alterado.observacoes += f'\n\nAlteração de {atividade_velha.atividade} de {inicio_velha_formatado} para '
        # Dados da atividade nova
        atividade_nova = Atividades.objects.get(id=int(dados.get('altividade_nova')))
        inicio_atividade_nova = datetime.strptime(dados.get('data_hora_atividade_nova'), '%Y-%m-%dT%H:%M')
        inicio_nova_formatado = inicio_atividade_nova.strftime('%d/%m/%y às %H:%M')
        fim_atividade_nova = (inicio_atividade_nova + atividade_nova.duracao).strftime('%Y-%m-%d %H:%M')
        detector_alterado.observacoes += f'{atividade_nova.atividade} com início às {inicio_nova_formatado}: '
        # Salvando as alterações no banco
        atividade_banco = dados_ativ[grupo_alterado][atividade_alterada]
        atividade_banco['id_atividade'] = int(dados.get('altividade_nova'))
        atividade_banco['inicio'] = inicio_atividade_nova.strftime('%Y-%m-%d %H:%M')
        atividade_banco['fim'] = fim_atividade_nova
        atividade_banco['professores'] = lista_professores[0] if len(lista_professores) == 1 else lista_professores

    if dados.get('espaco_novo') != '':
        # Dados da locação antiga
        espaco_antigo = Locaveis.objects.get(id=int(dados.get('espaco_atual')))
        check_in_locacao_antiga = datetime.strptime(dados.get('check_in_atual'), '%Y-%m-%dT%H:%M')
        check_out_locacao_antiga = datetime.strptime(dados.get('check_out_atual'), '%Y-%m-%dT%H:%M')
        check_in_formatada_antiga = check_in_locacao_antiga.strftime('%d/%m/%y às %H:%M')
        check_out_formatada_antiga = check_out_locacao_antiga.strftime('%d/%m/%y às %H:%M')
        detector_alterado.observacoes += f'\n\nLocação do(a) {espaco_antigo.local.estrutura} com check in às '
        detector_alterado.observacoes += f'{check_in_formatada_antiga} e check out às {check_out_formatada_antiga} '
        # Dados da nova locação
        espaco_novo = Locaveis.objects.get(id=int(dados.get('espaco_novo')))
        check_in_locacao_novo = datetime.strptime(dados.get('check_in_novo'), '%Y-%m-%dT%H:%M')
        check_out_locacao_novo = datetime.strptime(dados.get('check_out_novo'), '%Y-%m-%dT%H:%M')
        check_in_formatada_novo = check_in_locacao_novo.strftime('%d/%m/%y às %H:%M')
        check_out_formatada_novo = check_out_locacao_novo.strftime('%d/%m/%y às %H:%M')
        detector_alterado.observacoes += f'alterado para {espaco_novo.local.estrutura} com check in às '
        detector_alterado.observacoes += f'{check_in_formatada_novo} e check out às {check_out_formatada_novo}: '
        # Salvando as alterações no banco
        locacao_banco = dados_ativ[grupo_alterado][atividade_alterada]
        locacao_banco['id_espaco'] = int(dados.get('espaco_novo'))
        locacao_banco['check_in'] = check_in_locacao_novo.strftime('%Y-%m-%d %H:%M')
        locacao_banco['check_out'] = check_out_locacao_novo.strftime('%Y-%m-%d %H:%M')
        locacao_banco['professores'] = lista_professores[0] if len(lista_professores) == 1 else lista_professores

    detector_alterado.observacoes += dados.get("observacoes_da_alteracao")
    detector_alterado.save()


def atividade_excluida(dados_ativ, detector_alterado, dados):
    atividade = Atividades.objects.get(id=int(dados.get('altividade_atual')))
    data_hora_atividade = datetime.strptime(dados.get('data_hora_atividade_atual'), '%Y-%m-%dT%H:%M')
    data_e_hora_formatada = data_hora_atividade.strftime('%d/%m/%y às %H:%M')
    detector_alterado.observacoes += f'\n\n{atividade.atividade} de {data_e_hora_formatada} excluída: '
    lista_teste = dados.get('atividade_locacao_alterada').split('_')[3]
    grupo = f'grupo_{lista_teste}'

    if dados.get('espaco_novo') != '':
        n_locacao = 0

        for key in dados_ativ[grupo].keys():
            if 'locacao_' in key:
                n_locacao += 1

        if n_locacao == 0:
            dados_ativ[grupo][f'locacao_1'] = {
                'id_espaco': int(dados.get('espaco_novo')),
                'check_in': dados.get('check_in_novo').replace('T', ' '),
                'check_out': dados.get('check_out_novo').replace('T', ' '),
                'professores': dados.get('professores_atividade_nova')
            }
        else:
            dados_ativ[grupo][f'locacao_{n_locacao + 1}'] = {
                'id_espaco': int(dados.get('espaco_novo')),
                'check_in': dados.get('check_in_novo').replace('T', ' '),
                'check_out': dados.get('check_out_novo').replace('T', ' '),
                'professores': dados.get('professores_atividade_nova')
            }

    renumerar_atividades(dados_ativ, grupo, 'atividade')

    return


def locacao_excluida(dados_ativ, detector_alterado, dados):
    espaco = Locaveis.objects.get(id=int(dados.get('espaco_atual')))
    check_in_locacao = datetime.strptime(dados.get('check_in_atual'), '%Y-%m-%dT%H:%M')
    check_in_formatada = check_in_locacao.strftime('%d/%m/%y às %H:%M')
    detector_alterado.observacoes += f'\n\nLocação do(a) {espaco.local.estrutura} de {check_in_formatada} excluída: '

    atividade = Atividades.objects.get(id=int(dados.get('altividade_nova')))
    inicio = datetime.strptime(dados.get('data_hora_atividade_nova'), '%Y-%m-%dT%H:%M')

    if dados.get('altividade_nova') != '':
        n_atividade = 0
        lista_teste = dados.get('atividade_locacao_alterada').split('_')
        grupo = f'{lista_teste[2]}_{lista_teste[3]}'

        for key in dados_ativ[grupo].keys():
            if 'atividade' in key:
                n_atividade += 1

        if n_atividade == 0:
            dados_ativ[grupo]['atividade_1'] = {
                'id_atividade': int(dados.get('altividade_nova')),
                'inicio': inicio.strftime('%Y-%m-%d %H:%M'),
                'fim': (inicio + atividade.duracao).strftime('%Y-%m-%d %H:%M'),
                'qtd': dados.get('qtd_atividade')
            }
        else:
            dados_ativ[grupo][f'atividade_{n_atividade + 1}'] = {
                'id_atividade': int(dados.get('altividade_nova')),
                'inicio': inicio.strftime('%Y-%m-%d %H:%M'),
                'fim': (inicio + atividade.duracao).strftime('%Y-%m-%d %H:%M'),
                'qtd': dados.get('qtd_atividade')
            }

        renumerar_atividades(dados_ativ, grupo, 'locacao')

    return


def renumerar_atividades(dados_ativ, grupo, atividade_locacao):
    atividades = []

    for chave in dados_ativ[grupo].keys():
        if f'{atividade_locacao}_' in chave:
            atividades.append(chave)

    for atividade_n, atividade in enumerate(atividades, start=1):
        dados_ativ[grupo][f'{atividade_locacao}_{atividade_n}'] = dados_ativ[grupo].pop(atividade)


def retornar_nome_de_professores(lista_de_professores):
    professores = []

    try:
        len(lista_de_professores)
    except TypeError:
        professor = Professores.objects.get(id=lista_de_professores)
        professores = [professor.usuario.get_full_name()]
    else:
        for id_professor in lista_de_professores:
            professor = Professores.objects.get(id=id_professor)
            professores.append(professor.usuario.get_full_name())
    finally:
        return professores
