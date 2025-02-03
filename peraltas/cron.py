from collections import defaultdict
from datetime import datetime, timedelta

from reversion.models import Version
from orcamento.models import Orcamento, StatusOrcamento

from ordemDeServico.models import OrdemDeServico
from peraltas.models import FichaDeEvento, CodigosPadrao, ClienteColegio, RelacaoClienteResponsavel, ProdutosPeraltas, \
    ProdutoCorporativo, Vendedor
import requests

from projetoCEU.envio_de_emails import EmailSender
from projetoCEU.integracao_rd import alterar_campos_personalizados
from projetoCEU.utils import enviar_email_erro


def atualizar_pagantes_ficha():
    url = 'https://dashboard.peraltas.com.br/json/relatorio.json'
    codigos_padrao = [codigo.codigo for codigo in CodigosPadrao.objects.all()]

    response = requests.get(url)

    if response.status_code == 200:
        eventos = response.json()
        eventos_base = {evento['codigoGrupo']: evento for evento in eventos}

        fichas = FichaDeEvento.objects.filter(
            pre_reserva=False,
            check_in__date__gte=datetime.today().date()
        ).exclude(
            codigos_app__eficha__in=codigos_padrao
        )

        for ficha in fichas:
            try:
                alterar = False
                codigos_eficha = [codigo.upper().strip() for codigo in ficha.codigos_app.eficha.split(',')]
                eventos_dict = eventos_base if not verificar_sistema_antigo_cron(
                    codigos_eficha) else verificar_sistema_antigo_cron(codigos_eficha)
                total_pagantes_masculino = 0
                total_pagantes_feminino = 0
                total_professores_masculino = 0
                total_professores_feminino = 0

                for codigo in codigos_eficha:
                    if codigo in eventos_dict:
                        alterar = True
                        totais = eventos_dict[codigo]['totais']
                        total_pagantes_masculino += totais['totalPagantesMasculino']
                        total_pagantes_feminino += totais['totalPagantesFeminino']
                        total_professores_masculino += totais['totalProfessoresMasculino']
                        total_professores_feminino += totais['totalProfessoresFeminino']

                if alterar:
                    if ficha.produto_corporativo:
                        ficha.qtd_homens = total_pagantes_masculino
                        ficha.qtd_mulheres = total_pagantes_feminino
                    else:
                        ficha.qtd_meninos = total_pagantes_masculino
                        ficha.qtd_meninas = total_pagantes_feminino
                        ficha.qtd_profs_homens = total_professores_masculino
                        ficha.qtd_profs_mulheres = total_professores_feminino

                    ficha.qtd_eficha = total_pagantes_masculino + total_pagantes_feminino
                    ficha.qtd_confirmada = ficha.qtd_eficha + (ficha.qtd_offline if ficha.qtd_offline else 0)
                    ficha.adesao = (ficha.qtd_confirmada / ficha.qtd_convidada) * 100
                    ficha.save()

                    try:
                        alterar_campos_personalizados(ficha.id_negocio, ficha)
                    except Exception as e:
                        ...

                    if ficha.os:
                        ordem = OrdemDeServico.objects.get(ficha_de_evento=ficha)
                        ordem.n_participantes = total_pagantes_masculino + total_pagantes_feminino
                        ordem.n_professores = total_professores_masculino + total_professores_feminino
                        ordem.save()
            except Exception as e:
                mensagem_erro = f'Durante a atualização dos pagantes de {ficha.cliente} aconteceu um erro: {e}'
                enviar_email_erro(mensagem_erro, 'ERRO NA ATUALIZAÇÃO DOS PAGANTES')
    else:
        enviar_email_erro(
            f'Erro na conexão com o servidor de pagamentos, código {response.status_code}',
            'ERRO DE CONEXÃO COM SERVIDOR'
        )


def verificar_sistema_antigo_cron(codigos):
    """
    Função necessária para o periodo de transição do sistema de pagamntos
    """

    codigos_padrao = [codigo.codigo for codigo in CodigosPadrao.objects.all()]
    url_gerar_json = 'https://pagamento.peraltas.com.br/a/tools/gera_arquivo_json_turmas.aspx'
    url_json = 'https://pagamento.peraltas.com.br/json/turmas.json'

    response_gerar_json = requests.post(url_gerar_json)
    response_json = requests.get(url_json)

    if response_gerar_json.status_code == 200 and response_json.status_code == 200:
        eventos = response_json.json()
        eventos_dict = {evento['codigoGrupo']: evento for evento in eventos}

        for codigo in codigos:
            if codigo in eventos_dict and codigo != '':
                return eventos_dict


def envio_dados_embarque():
    dia_referencia = datetime.today().date() + timedelta(days=10)
    ordens_aviso = OrdemDeServico.objects.filter(
        check_in__date=dia_referencia
    ).exclude(
        dados_transporte__isnull=True
    )

    for ordem in ordens_aviso:
        for transporte in ordem.dados_transporte.all():
            try:
                EmailSender([transporte.monitor_embarque.usuario.email, 'bruno.furlanetto@hotmail.com']).dados_embarque(
                    ordem, transporte
                )
            except Exception as e:
                mensagem_erro = f'Erro durante a consulta da ordem de servico de {ordem.ficha_de_evento.cliente}: {e}'
                enviar_email_erro(mensagem_erro, 'ERRO NA CONSULTA DA ORDEM')


def verificar_validade_orcamento():
    orcamentos = Orcamento.objects.filter(data_vencimento=datetime.today().date() - timedelta(days=1))

    for orcamento in orcamentos:
        if 'aberto' in orcamento.status_orcamento.status.lower() or 'analise' in orcamento.status_orcamento.status.lower():
            status = StatusOrcamento.objects.get(status__icontains='vencido')
            orcamento.status_orcamento = status
            orcamento.save()


def atualizar_contagem_hotelaria():
    hotcodigo_validos = ['000001', '000004', '000027']
    data_inicio = datetime.today().date()
    data_final = data_inicio + timedelta(days=120)
    url = f'https://servicesapp.brotasecoresort.com.br:8009/testes/get_uhs.php?check_in={data_inicio}&check_out={data_final}'
    response = requests.get(url, verify=False)
    reservas = response.json()['reservas']
    cliente_brotas_eco = ClienteColegio.objects.get(cnpj='03.694.061/0001-90')
    relacao_responsavel = RelacaoClienteResponsavel.objects.filter(cliente=cliente_brotas_eco).first()
    produto = ProdutosPeraltas.objects.get(brotas_eco=True)
    produto_hospedagem = ProdutoCorporativo.objects.filter(brotas_eco=True).first()
    atendente = Vendedor.objects.filter(usuario__groups__name__icontains='diretoria').first()

    dados_por_dia = defaultdict(lambda: {
        'data': None,
        'soma_adultos': 0,
        'soma_criancas': 0,
        'soma_criancas_2': 0,
        'soma_participantes': 0,
        'hotnomes': set()
    })

    for reserva in reservas:
        if reserva['K_HOTCODIGO'] in hotcodigo_validos:
            data_check_in = datetime.strptime(reserva['HORTUDATAENTRADA'], '%Y-%m-%d %H:%M:%S').date()
            data_check_out = datetime.strptime(reserva['HORTUDATASAIDA'], '%Y-%m-%d %H:%M:%S').date()

            if reserva['K_HOTCODIGO'] == '000027' or (data_check_out - data_check_in).days > 0:
                for n in range((data_check_out - data_check_in).days + 1):  # Inclui o dia de check-out
                    dia = data_check_in + timedelta(days=n)
                    dados_por_dia[dia]['data'] = dia.strftime('%Y-%m-%d')
                    dados_por_dia[dia]['soma_adultos'] += int(reserva.get('HORTUQUANTIDADEADULTO', 0))
                    dados_por_dia[dia]['soma_criancas'] += int(reserva.get('HORTUQUANTIDADECRIANCA', 0))
                    dados_por_dia[dia]['soma_criancas_2'] += int(reserva.get('HORTUQUANTIDADECRIANCAFX2', 0))
                    dados_por_dia[dia]['hotnomes'].add(reserva.get('HOTNOME', ''))
                    # Converte os hotnomes para strings concatenadas e soma os participantes
    resultado = []
    for dia, dados in sorted(dados_por_dia.items()):
        dados['hotnomes'] = ', '.join(sorted(dados['hotnomes']))
        dados['soma_participantes'] = (
                dados['soma_adultos'] + dados['soma_criancas'] + dados['soma_criancas_2']
        )
        resultado.append(dados)

    for dia in resultado:
        evento, criado = FichaDeEvento.objects.get_or_create(
            cliente=cliente_brotas_eco,
            check_in=datetime.strptime(f'{dia["data"]} 06:00', '%Y-%m-%d %H:%M'),
            check_out=datetime.strptime(f'{dia["data"]} 22:00', '%Y-%m-%d %H:%M'),
            produto=produto,
            defaults={
                'cliente': cliente_brotas_eco,
                'responsavel_evento': relacao_responsavel.responsavel.all()[0],
                'check_in': datetime.strptime(f'{dia["data"]} 06:00', '%Y-%m-%d %H:%M'),
                'check_out': datetime.strptime(f'{dia["data"]} 22:00', '%Y-%m-%d %H:%M'),
                'produto': produto,
                'produto_corporativo': produto_hospedagem,
                'obs_edicao_horario': 'Preenchido pelo sistema',
                'id_negocio': 'SEMCRDS001',
                'vendedora': atendente,
                'qtd_convidada': dia['soma_participantes'],
                'pre_reserva': True,
                'agendado': True,
                'observacoes': dia['hotnomes'],
            }
        )

        if not criado:
            evento.qtd_convidada = dia['soma_participantes']
            evento.save()
