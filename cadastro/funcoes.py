import requests

from cadastro.funcoesColegio import pegar_informacoes_cliente
from ceu.models import Atividades, Professores, Locaveis
from ordemDeServico.models import OrdemDeServico, CadastroDadosTransporte, DadosTransporte
from peraltas.models import ClienteColegio, Responsavel, CadastroInfoAdicionais, \
    CadastroCodigoApp, InformacoesAdcionais, CodigosApp, FichaDeEvento, ProdutosPeraltas, CadastroResponsavel, \
    CadastroCliente, RelacaoClienteResponsavel, OpcionaisGerais, OpcionaisFormatura, \
    AtividadesEco, EscalaAcampamento, ProdutoCorporativo, Monitor, CodigosPadrao
from projetoCEU.utils import enviar_email_erro


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def requests_ajax(requisicao, files=None, usuario=None):
    if requisicao.get('id_ficha'):
        ficha_de_evento = FichaDeEvento.objects.get(pk=requisicao.get('id_ficha'))
        id_monitor_embarque = ''
        serie = []
        atividades_ceu = {}
        locacoes_ceu = {}
        atividades_eco = {}
        atividades_peraltas = []

        for perfil in ficha_de_evento.perfil_participantes.all():
            if perfil.ano != '':
                serie.append(perfil.ano)
            elif perfil.fase == 'Ensino superior':
                serie.append(perfil.fase)

        for atividade in ficha_de_evento.atividades_ceu.all():
            atividades_ceu[atividade.id] = atividade.atividade

        for local in ficha_de_evento.locacoes_ceu.all():
            locacoes_ceu[local.id] = local.local.estrutura

        for atividade in ficha_de_evento.atividades_eco.all():
            atividades_eco[atividade.id] = atividade.nome_atividade_eco

        for grupo in ficha_de_evento.atividades_peraltas.all():
            atividades_peraltas.append(grupo.grupo)

        dados_ficha = {
            'id_instituicao': ficha_de_evento.cliente.nome_fantasia,
            'id_cidade': ficha_de_evento.cliente.cidade,
            'id_endereco': ficha_de_evento.cliente.endereco,
            'id_cnpj': ficha_de_evento.cliente.cnpj,
            'id_responsavel_grupo': ficha_de_evento.responsavel_evento.nome,
            'transporte': ficha_de_evento.informacoes_adcionais.transporte_fechado_internamente == 1,
            'seguro': ficha_de_evento.informacoes_adcionais.seguro,
            'id_n_participantes': ficha_de_evento.qtd_confirmada,
            'id_serie': ', '.join(serie),
            'id_n_professores': ficha_de_evento.qtd_professores,
            'id_check_in': ficha_de_evento.check_in,
            'id_check_out': ficha_de_evento.check_out,
            'id_vendedor': ficha_de_evento.vendedora.id,
            'id_empresa': ficha_de_evento.empresa,
            'atividades_ceu': atividades_ceu,
            'atividades_ceu_a_definir': ficha_de_evento.atividades_ceu_a_definir,
            'locacoes_ceu': locacoes_ceu,
            'atividades_eco': atividades_eco,
            'atividades_peraltas': atividades_peraltas,
            'id_observacoes': ficha_de_evento.observacoes,
            'corporativo': not ficha_de_evento.produto.colegio
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
            locaveis[estrutura.id] = estrutura.local.estrutura

        return locaveis

    if requisicao.get('tipo') == 'ecoturismo':
        atividades_eco_bd = AtividadesEco.objects.all()
        monitores_biologos_bd = Monitor.objects.filter(biologo=True)
        atividades = {}
        biologos = {}

        for monitor in monitores_biologos_bd:
            biologos[monitor.id] = monitor.usuario.get_full_name()

        for atividade in atividades_eco_bd:
            atividades[atividade.id] = atividade.nome_atividade_eco

        return {'atividades': atividades, 'biologos': biologos}

    if requisicao.get('atividade'):
        atividade_selecionada = Atividades.objects.get(id=int(requisicao.get('atividade')))
        limtacoes = []

        for limite in atividade_selecionada.limitacao.all():
            limtacoes.append(limite.limitacao)

        return {'limitacoes': limtacoes,
                'participantes_minimo': atividade_selecionada.numero_de_participantes_minimo,
                'participantes_maximo': atividade_selecionada.numero_de_participantes_maximo}

    if requisicao.get('local'):
        local_selecionado = Locaveis.objects.get(id=int(requisicao.get('local')))

        return {'lotacao': local_selecionado.local.lotacao}

    if requisicao.get('atividade_ecoturismo'):
        atividade = AtividadesEco.objects.get(id=int(requisicao.get('atividade_ecoturismo')))

        return {'participantes_minimo': atividade.participantes_min,
                'participantes_maximo': atividade.participantes_max}

    if requisicao.get('cliente'):
        info_cliente = pegar_informacoes_cliente(requisicao.get('cliente'))

        return info_cliente

    if requisicao.get('campo') == 'professor':
        professores_db = Professores.objects.all()
        professores = {}

        for professor in professores_db:
            professores[professor.id] = professor.usuario.get_full_name()

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

    if requisicao.get('campo') == 'professor':
        professores_db = Professores.objects.all()
        professores = {}

        for professor in professores_db:
            professores[professor.id] = professor.usuario.get_full_name()

        return professores

    if requisicao.get('cnpj') and not requisicao.get('novo'):
        cliente_bd = ClienteColegio.objects.get(cnpj=requisicao.get('cnpj'))

        try:
            relacao = RelacaoClienteResponsavel.objects.get(cliente=cliente_bd)
        except RelacaoClienteResponsavel.DoesNotExist:
            cliente = {
                'id': cliente_bd.id,
                'codigo_app_pj': cliente_bd.codigo_app_pj,
                'razao_social': cliente_bd.razao_social,
                'cnpj': cliente_bd.cnpj,
                'nome_fantasia': cliente_bd.nome_fantasia,
                'nickname': cliente_bd.nickname,
                'endereco': cliente_bd.endereco,
                'bairro': cliente_bd.bairro,
                'cidade': cliente_bd.bairro,
                'estado': cliente_bd.estado,
                'cep': cliente_bd.cep,
            }
        else:
            responsaveis = {}
            for responsavel in relacao.responsavel.all():
                responsaveis[responsavel.id] = responsavel.nome

            cliente = {
                'id': cliente_bd.id,
                'codigo_app_pj': cliente_bd.codigo_app_pj,
                'razao_social': cliente_bd.razao_social,
                'cnpj': cliente_bd.cnpj,
                'nome_fantasia': cliente_bd.nome_fantasia,
                'nickname': cliente_bd.nickname,
                'endereco': cliente_bd.endereco,
                'bairro': cliente_bd.bairro,
                'cidade': cliente_bd.bairro,
                'estado': cliente_bd.estado,
                'cep': cliente_bd.cep,
                'responsaveis': responsaveis
            }

        return cliente

    if requisicao.get('id_cliente_app'):
        cliente = ClienteColegio.objects.get(id=int(requisicao.get('id_cliente_app')))

        return {'id_cliente_pj': cliente.codigo_app_pj}

    if requisicao.get('id'):
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
        cargos = []

        for cargo in responsavel_bd.cargo.all():
            cargos.append(cargo.id)

        try:
            relacao = RelacaoClienteResponsavel.objects.get(responsavel=responsavel_bd)
        except RelacaoClienteResponsavel.DoesNotExist:
            clientes = ClienteColegio.objects.all()
            responsavel = {
                'id': responsavel_bd.id,
                'nome': responsavel_bd.nome,
                'cargo': cargos,
                'fone': responsavel_bd.fone,
                'email_responsavel_evento': responsavel_bd.email_responsavel_evento,
                'responsavel_por': [{'nome': cliente.nome_fantasia, 'id': cliente.id} for cliente in clientes]
            }
        else:
            responsavel = {
                'id': responsavel_bd.id,
                'nome': responsavel_bd.nome,
                'cargo': cargos,
                'fone': responsavel_bd.fone,
                'email_responsavel_evento': responsavel_bd.email_responsavel_evento,
                'responsavel_por': {'nome': relacao.cliente.nome_fantasia, 'id': relacao.cliente.id}
            }

        return responsavel

    if requisicao.get('id_cliente'):
        relacao = RelacaoClienteResponsavel.objects.get(cliente=int(requisicao.get('id_cliente')))
        responsavel = Responsavel.objects.get(id=int(requisicao.get('id_responsavel')))

        if responsavel in relacao.responsavel.all():
            resposta = True
        else:
            resposta = False

        return {'resposta': resposta}

    if requisicao.get('novo') == 'responsavel':
        form = CadastroResponsavel(requisicao)

        if form.is_valid():
            try:
                novo_responsavel = form.save(commit=False)
                novo_responsavel.responsavel_cadastro = usuario
                novo_responsavel = form.save()
            except Exception as e:
                return {'mensagem': f'Houve um erro inesperado ({e}), responsável não foi salvo. Por favor tente mais tarde!'}
            else:
                return {'mensagem': 'Responsável salvo com sucesso!',
                        'nome_responsavel': novo_responsavel.nome,
                        'id_responsavel': novo_responsavel.id}

        else:
            return {'mensagem': form.errors}

    if requisicao.get('novo') == 'cliente':
        form = CadastroCliente(requisicao)

        if form.is_valid():
            try:
                novo_cliente = form.save(commit=False)
                novo_cliente.responsavel_cadastro = usuario
                novo_cliente = form.save()
            except Exception as e:
                return {'mensagem': f'Houve um erro inesperado ({e}), por favor tentar mais tarde!'}
            else:
                if requisicao.get('id_responsavel'):
                    cliente = ClienteColegio.objects.get(id=int(novo_cliente.id))
                    responsavel = Responsavel.objects.get(id=int(requisicao.get('id_responsavel')))
                    relacao = RelacaoClienteResponsavel(cliente=cliente)
                    relacao.save()
                    relacao = RelacaoClienteResponsavel.objects.get(cliente=int(novo_cliente.id))
                    relacao.responsavel.add(responsavel.id)

                return {'mensagem': 'Cliente salvo com sucesso',
                        'id_cliente': novo_cliente.id,
                        'nome_fantasia': novo_cliente.nome_fantasia}
        else:
            return {'mensagem': form.errors}

    if requisicao.get('infos') == 'adicionais':

        if requisicao.get('infos_adicionais'):
            info = InformacoesAdcionais.objects.get(id=int(requisicao.get('infos_adicionais')))

            if files:
                form = CadastroInfoAdicionais(requisicao, files=files, instance=info)
            else:
                form = CadastroInfoAdicionais(requisicao, instance=info)
        else:
            if files:
                form = CadastroInfoAdicionais(requisicao, files=requisicao.get('id_lista_segurados'))
            else:
                form = CadastroInfoAdicionais(requisicao)

        if form.is_valid():
            novas_infos = form.save()
            return {'id': novas_infos.id}
        else:
            return {'mensagem': form.errors}

    if requisicao.get('novo_op'):
        if requisicao.get('novo_op') == 'geral':
            try:
                novo_op_geral = OpcionaisGerais.objects.create(opcional_geral=requisicao.get('nome_op'))
                novo_op_geral.save()
            except:
                return {'salvo': False}
            else:
                return {'salvo': True, 'id': novo_op_geral.id}

        if requisicao.get('novo_op') == 'formatura':
            try:
                novo_op_formatura = OpcionaisFormatura.objects.create(opcional_formatura=requisicao.get('nome_op'))
                novo_op_formatura.save()
            except:
                return {'salvo': False}
            else:
                return {'salvo': True, 'id': novo_op_formatura.id}

    if requisicao.get('infos') == 'app':
        if requisicao.get('id_codigo_app'):
            codigo = CodigosApp.objects.get(id=int(requisicao.get('id_codigo_app')))
            form = CadastroCodigoApp(requisicao, instance=codigo)
        else:
            form = CadastroCodigoApp(requisicao)

        if form.is_valid():
            try:
                novo_codigo = form.save()
            except Exception as e:
                enviar_email_erro(f'{e}', 'ERRO')
            else:
                enviar_email_erro(f'{novo_codigo, novo_codigo.id}', 'Erro')
                return {'id': novo_codigo.id}

    if requisicao.get('id_produto'):
        produto = ProdutosPeraltas.objects.get(id=int(requisicao.get('id_produto')))
        dados_produtos_corporativo = {}

        if not produto.colegio:
            produtos_corporativos = ProdutoCorporativo.objects.all()

            for produto_corporativo in produtos_corporativos:
                dados_produtos_corporativo[produto_corporativo.id] = {
                    'check_in_padrao': produto_corporativo.hora_padrao_check_in,
                    'check_out_padrao': produto_corporativo.hora_padrao_check_out
                }

        return {
            'colegio': produto.colegio,
            'pernoite': produto.pernoite,
            'vt': produto.produto == 'Visita Técnica',
            'outro': produto.produto == 'Outro',
            'so_ceu': produto.produto == 'Só CEU',
            'n_dias': produto.n_dias,
            'hora_check_in_padrao': produto.hora_padrao_check_in,
            'hora_check_out_padrao': produto.hora_padrao_check_out,
            'dados_produtos_corporativo': dados_produtos_corporativo
        }


def pegar_refeicoes(dados):
    refeicoes = {}
    i = 0

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

    return refeicoes


def ver_empresa_atividades(dados):
    atividades_ceu = [dados.get('atividades_ceu'), dados.get('atividades_ceu_a_definir')]
    locacoes_ceu = dados.get('locacoes_ceu')
    atividades_exta = dados.get('atividades_eco')
    atividades_peraltas = dados.get('atividades_peraltas')

    if (atividades_ceu or locacoes_ceu) and (atividades_exta or atividades_peraltas):
        return 'Peraltas CEU'
    elif not (atividades_ceu or locacoes_ceu):
        return 'Peraltas'
    else:
        return 'CEU'


def numero_coordenadores(ficha_de_evento):
    ordem_de_servico = None

    if ficha_de_evento.os:
        ordem_de_servico = OrdemDeServico.objects.get(ficha_de_evento=ficha_de_evento)
        participantes = ordem_de_servico.n_participantes
    else:
        participantes = ficha_de_evento.qtd_convidada

    if not ordem_de_servico:
        if participantes < 120:
            return 1
        else:
            return 2
    else:
        if participantes < ordem_de_servico.racional_coordenadores:
            return 1
        elif ordem_de_servico.racional_coordenadores < participantes < 160:
            return 2
        else:
            if ordem_de_servico.permicao_coordenadores:
                return 3
            else:
                return 2


def separar_dados_transporte(dados_transporte, transporte_n):
    campos = list(CadastroDadosTransporte().fields.keys())
    n_carros = ['n_micro', 'n_46', 'n_50']
    campos.extend(n_carros)
    numero_carros = {}
    dados = {}

    for campo in campos:
        if len(dados_transporte.getlist(campo)) > 0:
            dados[campo] = dados_transporte.getlist(campo)[transporte_n]

            if campo in n_carros:
                numero_carros[campo] = dados_transporte.getlist(campo)[transporte_n]

    return dados, numero_carros


def salvar_dados_transporte(form_transporte, numero_carros):
    dados_transporte = form_transporte.save(commit=False)
    dados_transporte.dados_veiculos = DadosTransporte.reunir_veiculos(numero_carros)
    form_salvo = form_transporte.save()

    return form_salvo.id


def verificar_codigos(codigos):
    codigos_padrao = [codigo.codigo for codigo in CodigosPadrao.objects.all()]
    url_gerar_json = 'https://pagamento.peraltas.com.br/a/tools/gera_arquivo_json_turmas.aspx'
    url_json = 'https://pagamento.peraltas.com.br/json/turmas.json'

    for codigo in codigos:
        if codigo in codigos_padrao:
            return {
                'salvar': True
            }

    response_gerar_json = requests.get(url_gerar_json)
    response_json = requests.get(url_json)

    if response_gerar_json.status_code == 200 and response_json.status_code == 200:
        total_pagantes_masculino = 0
        total_pagantes_feminino = 0
        total_professores_masculino = 0
        total_professores_feminino = 0

        eventos = response_json.json()
        eventos_dict = {evento['codigoGrupo']: evento for evento in eventos}

        for codigo in codigos:
            if codigo not in eventos_dict and codigo != '':
                return {
                    'salvar': False,
                    'mensagem': f'O código {codigo} não está cadastrado no sistema de pagamentos. Verifique e tente novamente.'
                }
            elif codigo in eventos_dict and codigo != '':
                totais = eventos_dict[codigo]['totais']
                total_pagantes_masculino += totais['totalPagantesMasculino']
                total_pagantes_feminino += totais['totalPagantesFeminino']
                total_professores_masculino += totais['totalProfessoresMasculino']
                total_professores_feminino += totais['totalProfessoresFeminino']
    else:
        return {
            'salvar': False,
            'mensagem': 'O servidor de pagamentos não respondeu, cadastre um dos códgigos de exceção e tente novamente mais tarde.'
        }

    return {
        'salvar': True,
        'totais': {
            'total_pagantes_masculino': total_pagantes_masculino,
            'total_pagantes_feminino': total_pagantes_feminino,
            'total_professores_masculino': total_professores_masculino,
            'total_professores_feminino': total_professores_feminino,
            'total_confirmado': total_pagantes_masculino + total_pagantes_feminino,
            'total_eficha': total_pagantes_masculino + total_pagantes_feminino,
        }
    }
