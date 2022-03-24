from cadastro.funcoesColegio import pegar_informacoes_cliente
from ceu.models import Atividades, Professores, Locaveis
from peraltas.models import ClienteColegio, Responsavel, CadastroInfoAdicionais, CadastroResumoFinanceiro, \
    CadastroCodigoApp, InformacoesAdcionais, ResumoFinanceiro, CodigosApp


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

    if requisicao.get('cnpj'):
        cliente_bd = ClienteColegio.objects.get(cnpj=int(requisicao.get('cnpj')))

        cliente = {
            'id': cliente_bd.id,
            'razao_social': cliente_bd.razao_social,
            'cnpj': cliente_bd.cnpj,
            'nome_fantasia': cliente_bd.nome_fantasia,
            'endereco': cliente_bd.endereco,
            'bairro': cliente_bd.bairro,
            'cidade': cliente_bd.bairro,
            'estado': cliente_bd.estado,
            'cep': cliente_bd.cep
        }

        return cliente

    if requisicao.get('id'):
        print(requisicao.get('id'))
        responsaveis_bd = Responsavel.objects.filter(responsavel_por=int(requisicao.get('id')))
        responsaveis = {}

        for responsavel in responsaveis_bd:
            responsaveis[responsavel.id] = {'nome': responsavel.nome,
                                            'cargo': responsavel.cargo,
                                            'fone': responsavel.fone,
                                            'email': responsavel.email_responsavel_evento,
                                            'responsavel_por': responsavel.responsavel_por.nome_fantasia
                                            }

        return responsaveis

    if requisicao.get('id_selecao'):
        responsavel_bd = Responsavel.objects.get(id=int(requisicao.get('id_selecao')))

        responsavel = {
            'id': responsavel_bd.id,
            'nome': responsavel_bd.nome,
            'cargo': responsavel_bd.cargo,
            'fone': responsavel_bd.fone,
            'email_responsavel_evento': responsavel_bd.email_responsavel_evento,
            'responsavel_por': responsavel_bd.responsavel_por.id
        }

        return responsavel

    if requisicao.get('infos') == 'adicionais':

        if requisicao.get('id_infos_adicionais'):
            info = InformacoesAdcionais.objects.get(id=int(requisicao.get('id_infos_adicionais')))
            form = CadastroInfoAdicionais(requisicao, instance=info)
        else:
            form = CadastroInfoAdicionais(requisicao)

        if form.is_valid():
            novas_infos = form.save()
            return {'id': novas_infos.id}
        else:
            print('Não foi')
            print(form.errors)

    if requisicao.get('infos') == 'financeiro':

        if requisicao.get('id_resumo_financeiro'):
            resumo = ResumoFinanceiro.objects.get(id=int(requisicao.get('id_resumo_financeiro')))
            form = CadastroResumoFinanceiro(requisicao, instance=resumo)
        else:
            form = CadastroResumoFinanceiro(requisicao)

        resumo = form.save(commit=False)
        vencimentos = []

        for i in range(1, int(requisicao.get('parcelas')) + 1):
            vencimentos.append(requisicao.get(f'vencimento_{i}'))

        resumo.vencimentos = ', '.join(vencimentos)
        resumo.forma_pagamento = f'{requisicao.get("parcelas")}vezes no(a) {requisicao.get("forma_pagamento")}'

        if form.is_valid():
            novo_resumo = form.save()
            return {'id': novo_resumo.id}
        else:
            print(form.errors)

    if requisicao.get('infos') == 'app':

        if requisicao.get('id_codigo_app'):
            codigo = CodigosApp.objects.get(id=int(requisicao.get('id_codigo_app')))
            form = CadastroCodigoApp(requisicao, instance=codigo)
        else:
            form = CadastroCodigoApp(requisicao)

        if form.is_valid():
            novo_codigo = form.save()
            return {'id': novo_codigo.id}


def pegar_refeicoes(dados):
    refeicoes = {}
    refeicao_data = []
    i = 0

    for campo in dados:
        if 'data_refeicao' in campo:
            i += 1

    for j in range(1, i+1):

        if dados.get(f'cafe{j}'):
            refeicao_data.append('Café')

        if dados.get(f'coffee_m_{j}'):
            refeicao_data.append('Coffee manhã')

        if dados.get(f'almoco_{j}'):
            refeicao_data.append('Almoço')

        if dados.get(f'lanche_t_{j}'):
            refeicao_data.append('Lanche tarde')

        if dados.get(f'coffee_t_{j}'):
            refeicao_data.append('Coffee tarde')

        if dados.get(f'jantar{j}'):
            refeicao_data.append('Jantar')

        if dados.get(f'coffee_n_{j}'):
            refeicao_data.append('Coffee noite')

        refeicoes[dados.get(f'data_refeicao_{j}')] = refeicao_data

    return refeicoes
