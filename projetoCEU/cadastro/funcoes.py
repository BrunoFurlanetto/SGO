from cadastro.models import Atividades, Professores


def indice_formulario(formulario, campo, n=5):
    """
    :param formulario: Form de model a ser percorrido
    :param campo: String a ser procurado nos campos do formulário
    :param n_atividades: número de retornos necessários, para locacao, mandar 3
    :return: Irá retornar apenas os campos do fomulário que apresentam a palavra
             enviada no parametro campo.
    """

    indice = 1
    campos = []

    for i in formulario.fields:
        if indice <= n:
            if campo in i:
                if 'professores' not in i:
                    if campo == 'hora':
                        if 'entrada' not in i:
                            campos.append(formulario[i])
                    else:
                        if 'hora' not in i:
                            campos.append(formulario[i])

    return campos


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def verificar_tabela(dados):
    if dados.get('ativ1') == '':
        return True, 'Atividade 1 não preenchida'
    else:
        if dados.get('horaAtividade_1') == '':
            return True, 'Início da atividade 1 não preenchida'

        if dados.get('prf1atv1') == '':
            return True, 'É preciso cadastrar ao menos um professor na atividade 1'

    if dados.get('ativ2') != '':
        if dados.get('horaAtividade_2') == '':
            return True, 'Início da atividade 2 não preenchida'

        if dados.get('prf1atv2') == '':
            return True, 'É preciso cadastrar ao menos um professor na atividade 2'

    if dados.get('ativ3') != '':
        if dados.get('horaAtividade_3') == '':
            return True, 'Início da atividade 3 não preenchida'

        if dados.get('prf1atv3') == '':
            return True, 'É preciso cadastrar ao menos um professor na atividade 3'

    if dados.get('ativ4') != '':
        if dados.get('horaAtividade_4') == '':
            return True, 'Início da atividade 4 não preenchida'

        if dados.get('prf1atv4') == '':
            return True, 'É preciso cadastrar ao menos um professor na atividade 4'

    if dados.get('ativ5') != '':
        if dados.get('horaAtividade_5') == '':
            return True, 'Início da atividade 5 não preenchida'

        if dados.get('prf1atv5') == '':
            return True, 'É preciso cadastrar ao menos um professor na atividade 5'

    equipe = [dados.get('coordenador'), dados.get('professor_2'), dados.get('professor_3'), dados.get('professor_4')]
    print(equipe)
    for d in dados:
        if 'prf' in d and dados.get(d) != '':
            if dados.get(d) not in equipe:
                return True, f'Professor {dados.get(d)} cadastrado em atividade, mas não escalado!!'

    return False, 'Ok'


def analisar_tabela_atividade(os, dados):
    os.atividade_1 = Atividades.objects.get(atividade=dados.get('ativ1'))
    os.hora_atividade_1 = dados.get('horaAtividade_1')
    os.professores_atividade_1 = juntar_professores(dados)

    if dados.get('ativ2') != '':
        os.atividade_2 = Atividades.objects.get(atividade=dados.get('ativ2'))
        os.hora_atividade_2 = dados.get('horaAtividade_2')
        os.professores_atividade_2 = juntar_professores(dados, atividade=2)

    if dados.get('ativ3') != '':
        os.atividade_3 = Atividades.objects.get(atividade=dados.get('ativ3'))
        os.hora_atividade_3 = dados.get('horaAtividade_3')
        os.professores_atividade_3 = juntar_professores(dados, atividade=3)

    if dados.get('ativ4') != '':
        os.atividade_4 = Atividades.objects.get(atividade=dados.get('ativ4'))
        os.hora_atividade_4 = dados.get('horaAtividade_4')
        os.professores_atividade_4 = juntar_professores(dados, atividade=4)

    if dados.get('ativ5') != '':
        os.atividade_5 = Atividades.objects.get(atividade=dados.get('ativ5'))
        os.hora_atividade_5 = dados.get('horaAtividade_5')
        os.professores_atividade_5 = juntar_professores(dados, atividade=5)


def juntar_professores(dados, atividade=1):
    if atividade == 1:
        professores = str(Professores.objects.get(id=dados.get('prf1atv1')))
        for d in dados:
            if 'atv1' in d and dados.get(d) != '' and 'prf1' not in d:
                professores += ', ' + str(Professores.objects.get(id=dados.get(d)))

        return professores

    if atividade == 2:
        professores = str(Professores.objects.get(id=dados.get('prf1atv2')))
        for d in dados:
            if 'atv2' in d and dados.get(d) != '' and 'prf1' not in d:
                professores += ', ' + str(Professores.objects.get(id=dados.get(d)))

        return professores

    if atividade == 3:
        professores = str(Professores.objects.get(id=dados.get('prf1atv3')))
        for d in dados:
            if 'atv3' in d and dados.get(d) != '' and 'prf1' not in d:
                professores += ', ' + str(Professores.objects.get(id=dados.get(d)))

        return professores

    if atividade == 4:
        professores = str(Professores.objects.get(id=dados.get('prf1atv4')))
        for d in dados:
            if 'atv4' in d and dados.get(d) != '' and 'prf1' not in d:
                professores += ', ' + str(Professores.objects.get(id=dados.get(d)))

        return professores

    if atividade == 5:
        professores = str(Professores.objects.get(id=dados.get('prf1atv5')))
        for d in dados:
            if 'atv5' in d and dados.get(d) != '' and 'prf1' not in d:
                professores += ', ' + str(Professores.objects.get(id=dados.get(d)))

        return professores
