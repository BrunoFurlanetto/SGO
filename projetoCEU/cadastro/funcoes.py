from cadastro.funcoesColegio import pegar_informacoes_cliente
from ceu.models import Atividades, Professores, Locaveis
from peraltas.models import ClienteColegio, Responsavel, CadastroInfoAdicionais, \
    CadastroCodigoApp, InformacoesAdcionais, CodigosApp, FichaDeEvento, ProdutosPeraltas


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def requests_ajax(requisicao):
    if requisicao.get('id_ficha'):
        ficha_de_evento = FichaDeEvento.objects.get(id=int(requisicao.get('id_ficha')))
        serie = []
        atividades_ceu = {}
        locacoes_ceu = {}
        atividades_eco = {}
        atividades_peraltas = {}
        corporativo = False
        produto_corporativo = ProdutosPeraltas.objects.get(produto='Corporativo (Empresa)')

        for perfil in ficha_de_evento.perfil_participantes.all():
            if perfil.ano != '':
                serie.append(perfil.ano)
            elif perfil.fase == 'Ensino superior':
                serie.append(perfil.fase)

        for atividade in ficha_de_evento.informacoes_adcionais.atividades_ceu.all():
            atividades_ceu[atividade.id] = atividade.atividade

        for local in ficha_de_evento.informacoes_adcionais.locacoes_ceu.all():
            locacoes_ceu[local.id] = local.local.estrutura

        for atividade in ficha_de_evento.informacoes_adcionais.atividades_eco.all():
            atividades_eco[atividade.id] = atividade.atividade

        for produto in ficha_de_evento.produto.all():

            if produto == produto_corporativo:
                corporativo = True

        dados_ficha = {
            'id_instituicao': ficha_de_evento.cliente.nome_fantasia,
            'id_cidade': ficha_de_evento.cliente.cidade,
            'id_responsavel_grupo': ficha_de_evento.responsavel_evento.nome,
            'id_n_participantes': ficha_de_evento.qtd_confirmada,
            'id_serie': ', '.join(serie),
            'id_n_professores': ficha_de_evento.qtd_professores,
            'id_check_in': ficha_de_evento.check_in,
            'id_check_out': ficha_de_evento.check_out,
            'id_vendedor': ficha_de_evento.vendedora.id,
            'id_empresa': ficha_de_evento.empresa,
            'atividades_ceu': atividades_ceu,
            'locacoes_ceu': locacoes_ceu,
            'atividades_eco': atividades_eco,
            'id_observacoes': ficha_de_evento.observacoes,
            'corporativo': corporativo
        }

        return dados_ficha

    if requisicao.get('tipo') == 'Colégio':
        atividades_bd = Atividades.objects.all()
        atividades = {}

        for atividade in atividades_bd:
            atividades[atividade.id] = atividade.atividade

        return {'dados': atividades}

    if requisicao.get('tipo') == 'Empresa':
        locaveis_bd = Locaveis.objects.all()
        locaveis = {}

        for estrutura in locaveis_bd:
            print(estrutura.local)
            locaveis[estrutura.local.id] = estrutura.local.estrutura

        return locaveis

    if requisicao.get('atividade'):
        atividade_selecionada = Atividades.objects.get(id=requisicao.get('atividade'))
        limtacoes = []

        for limite in atividade_selecionada.limitacao.all():
            limtacoes.append(limite.limitacao)

        return {'limitacoes': limtacoes,
                'participantes_minimo': atividade_selecionada.numero_de_participantes_minimo,
                'participantes_maximo': atividade_selecionada.numero_de_participantes_maximo}

    if requisicao.get('local'):
        local_selecionado = Locaveis.objects.get(id=requisicao.POST.get('local'))

        return {'lotacao': local_selecionado.lotacao}

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
        locais_bd = Locaveis.objects.all()
        locais = {}

        for local in locais_bd:
            locais[local.id] = local.local.estrutura

        return locais

    if requisicao.get('cnpj'):
        print(requisicao.get('cnpj'))
        cliente_bd = ClienteColegio.objects.get(cnpj=requisicao.get('cnpj'))

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

    if requisicao.get('id_cliente'):
        responsavel = Responsavel.objects.get(id=int(requisicao.get('id_responsavel')))
        print(requisicao.get('id_responsavel'))
        if responsavel.responsavel_por.id == int(requisicao.get('id_cliente')):

            resposta = True
        else:
            resposta = False

        return {'resposta': resposta}

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

    if requisicao.get('infos') == 'app':

        if requisicao.get('id_codigo_app'):
            codigo = CodigosApp.objects.get(id=int(requisicao.get('id_codigo_app')))
            form = CadastroCodigoApp(requisicao, instance=codigo)
        else:
            form = CadastroCodigoApp(requisicao)

        if form.is_valid():
            novo_codigo = form.save()
            return {'id': novo_codigo.id}

    if requisicao.get('id_produto'):
        produto = ProdutosPeraltas.objects.get(id=int(requisicao.get('id_produto')))

        return {
            'colegio': produto.colegio,
            'pernoite': produto.pernoite,
            'vt': produto.produto == 'Visita Técnica',
            'outro': produto.produto == 'Outro'
        }


def pegar_refeicoes(dados):
    refeicoes = {}
    i = 0
    print(dados)

    for campo in dados:
        if 'data_refeicao' in campo:
            i += 1

    for j in range(1, i + 1):
        refeicao_data = []

        if dados.get(f'cafe_{j}'):
            refeicao_data.append('Café')

        if dados.get(f'coffee_m_{j}'):
            refeicao_data.append('Coffee manhã')

        if dados.get(f'almoco_{j}'):
            refeicao_data.append('Almoço')

        if dados.get(f'lanche_t_{j}'):
            refeicao_data.append('Lanche tarde')

        if dados.get(f'coffee_t_{j}'):
            refeicao_data.append('Coffee tarde')

        if dados.get(f'jantar_{j}'):
            refeicao_data.append('Jantar')

        if dados.get(f'coffee_n_{j}'):
            refeicao_data.append('Coffee noite')

        if dados.get(f'lanche_n_{j}'):
            refeicao_data.append('Lanche noite')

        refeicoes[dados.get(f'data_refeicao_{j}')] = refeicao_data
        print(refeicoes)

    return refeicoes
