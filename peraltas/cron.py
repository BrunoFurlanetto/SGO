from datetime import datetime, timedelta

from reversion.models import Version
from orcamento.models import Orcamento, StatusOrcamento

from ordemDeServico.models import OrdemDeServico
from peraltas.models import FichaDeEvento, CodigosPadrao
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

        try:
            for ficha in fichas:
                alterar = False
                codigos_eficha = [codigo.upper().strip() for codigo in ficha.codigos_app.eficha.split(',')]
                eventos_dict = eventos_base if not verificar_sistema_antigo_cron(codigos_eficha) else verificar_sistema_antigo_cron(codigos_eficha)
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
            mensagem_erro = f'Durante a atualização dos pagantes aconteceu um erro: {e}'
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


def deletar_versoes_antigas():
    data_de_corte = datetime.now() - timedelta(days=15)
    versoes_antigas = Version.objects.get_for_model(FichaDeEvento).filter(revision__date_created__lt=data_de_corte)
    versoes_antigas.delete()
