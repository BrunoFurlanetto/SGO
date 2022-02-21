from datetime import timedelta, datetime
import operator
from django.db.models import Q

from cadastro.models import RelatorioDeAtendimentoCeu
from ceu.models import Tipo, Professores


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def verificar_anos(os):
    anos = []

    for ordem in os:
        if not ordem.data_atendimento.year in anos:
            anos.append(ordem.data_atendimento.year)

    return anos


# ------------- O meses aqui precisam ser nomeados porque os dados são enviados via ajax pra ser impresso na tela ------
def pegar_mes(ordens):
    temp = []
    meses = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho',
             8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}

    for ordem in ordens:
        if not meses[ordem.data_atendimento.month] in temp:
            temp.append(meses[ordem.data_atendimento.month])

    return ', '.join(temp)


def contar_atividades(professor):
    n_atividades = 0
    ordens = RelatorioDeAtendimentoCeu.objects.filter(Q(coordenador=professor) | Q(professor_2=professor) |
                                                      Q(professor_3=professor) | Q(professor_4=professor)).filter(
        data_atendimento__month=datetime.now().month).values()

    for ordem in ordens:
        for nome in ordem:
            if 'professores' in nome and 'locacao' not in nome and ordem[nome] is not None:

                if professor.nome in ordem[nome]:
                    n_atividades += 1

    return n_atividades


def contar_horas(professor):
    n_horas = timedelta()
    ordens = RelatorioDeAtendimentoCeu.objects.filter(
        Q(coordenador__nome=professor) |
        Q(professor_2__nome=professor) |
        Q(professor_3__nome=professor) |
        Q(professor_4__nome=professor)).filter(data_atendimento__month=datetime.now().month).values()

    for ordem in ordens:

        for nome in ordem:
            if 'professores_locacao_1' in nome and ordem[nome] is not None:

                if professor.nome in ordem[nome]:
                    n_horas += ordem['soma_horas_1']

            if 'professores_locacao_2' in nome and ordem[nome] is not None:

                if professor.nome in ordem[nome]:
                    # if ordem['soma_horas_2'] is not None:
                    n_horas += ordem['soma_horas_2']

            if 'professores_locacao_3' in nome and ordem[nome] is not None:

                if professor.nome in ordem[nome]:
                    # if Professores.objects.get(pk=ordem[nome]) == professor:
                    n_horas += ordem['soma_horas_3']

    return formatar_horas(n_horas)


def contar_diaria(professor):
    ordens = RelatorioDeAtendimentoCeu.objects.filter(Q(coordenador=professor) | Q(professor_2=professor) |
                                                      Q(professor_3=professor) | Q(professor_4=professor)).filter(
        Q(tipo=Tipo.objects.get(tipo='Público')) |
        Q(tipo=Tipo.objects.get(tipo='Colégio'))).filter(data_atendimento__month=datetime.now().month).values()

    if professor.diarista:
        return len(ordens)
    else:
        return 0


def formatar_horas(horas):
    if horas != timedelta(days=0):
        h = horas.days * 24 + horas.seconds // 3600
        m = (horas.seconds % 3600) / 3600
        total = h + m
        return str(round(total, 2))
    else:
        h = horas.seconds // 3600
        m = (horas.seconds % 3600) / 3600
        total = h + m
        return str(round(total, 2))


def pegar_atividades(ordens):
    atividades_realizadas = []
    atividades = {}

    for ordem in ordens:

        if ordem.atividade_1 is not None:
            atividades_realizadas.append(ordem.atividade_1.atividade)

        if ordem.atividade_2 is not None:
            atividades_realizadas.append(ordem.atividade_2.atividade)

        if ordem.atividade_3 is not None:
            atividades_realizadas.append(ordem.atividade_3.atividade)

        if ordem.atividade_4 is not None:
            atividades_realizadas.append(ordem.atividade_4.atividade)

        if ordem.atividade_5 is not None:
            atividades_realizadas.append(ordem.atividade_5.atividade)

    for atividade in atividades_realizadas:
        atividades[atividade] = atividades_realizadas.count(atividade)

    return ordenar_dicionario(atividades)


def contar_atividades_professor(professor, ordens):
    atividades_realizadas = {}

    for ordem in ordens:
        if professor.nome in ordem.professores_atividade_1:
            if atividades_realizadas.get(ordem.atividade_1.atividade):
                atividades_realizadas[ordem.atividade_1.atividade] += 1
            else:
                atividades_realizadas[ordem.atividade_1.atividade] = 1

        if professor.nome in ordem.professores_atividade_2:
            if atividades_realizadas.get(ordem.atividade_2.atividade):
                atividades_realizadas[ordem.atividade_2.atividade] += 1
            else:
                atividades_realizadas[ordem.atividade_2.atividade] = 1

        if professor.nome in ordem.professores_atividade_3:
            if atividades_realizadas.get(ordem.atividade_3.atividade):
                atividades_realizadas[ordem.atividade_3.atividade] += 1
            else:
                atividades_realizadas[ordem.atividade_3.atividade] = 1

        if professor.nome in ordem.professores_atividade_4:
            if atividades_realizadas.get(ordem.atividade_4.atividade):
                atividades_realizadas[ordem.atividade_4.atividade] += 1
            else:
                atividades_realizadas[ordem.atividade_4.atividade] = 1

        if professor.nome in ordem.professores_atividade_5:
            if atividades_realizadas.get(ordem.atividade_5.atividade):
                atividades_realizadas[ordem.atividade_5.atividade] += 1
            else:
                atividades_realizadas[ordem.atividade_5.atividade] = 1

    return ordenar_dicionario(atividades_realizadas)


def ordenar_dicionario(dicionario):
    tuplas_ordenada = sorted(dicionario.items(), key=operator.itemgetter(1), reverse=True)
    tuplas_finais = []

    # ------ Limita o número de atividades em 10, o restante vai para a key 'Outras' --------
    if len(tuplas_ordenada) > 3:
        posicao = 1
        contagem_outros = 0

        for chave, valor in tuplas_ordenada:
            if posicao < 10:
                tuplas_finais.append((chave, valor))
                posicao += 1
                continue
            else:
                contagem_outros += 1

        tuplas_finais.append(('Outras', contagem_outros))
        return dict((x, y) for x, y in tuplas_finais)
    # ----------------------------------------------------------------------------------------

    return dict((x, y) for x, y in tuplas_ordenada)
