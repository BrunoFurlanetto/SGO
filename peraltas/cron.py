from datetime import datetime

from django.utils import timezone

from peraltas.models import FichaDeEvento, CodigosPadrao
import requests

from projetoCEU.utils import enviar_email_erro


def atualizar_pagantes_ficha():
    url = 'https://pagamento.peraltas.com.br/json/turmas.json'
    codigos_padrao = [codigo.codigo for codigo in CodigosPadrao.objects.all()]

    response = requests.get(url)

    if response.status_code == 200:
        eventos = response.json()

        eventos_dict = {evento['codigoGrupo']: evento for evento in eventos}

        fichas = FichaDeEvento.objects.filter(
            pre_reserva=False,
            check_in__date__gte=timezone.make_aware(datetime(2023, 3, 1))
        ).exclude(
            codigos_app__evento__in=codigos_padrao
        )

        try:
            for ficha in fichas:
                codigos_eficha = [codigo.upper().strip() for codigo in ficha.codigos_app.evento.split(',')]

                total_pagantes_masculino = 0
                total_pagantes_feminino = 0
                total_professores_masculino = 0
                total_professores_feminino = 0

                for codigo in codigos_eficha:
                    if codigo in eventos_dict:
                        totais = eventos_dict[codigo]['totais']
                        total_pagantes_masculino += totais['totalPagantesMasculino']
                        total_pagantes_feminino += totais['totalPagantesFeminino']
                        total_professores_masculino += totais['totalProfessoresMasculino']
                        total_professores_feminino += totais['totalProfessoresFeminino']

                if ficha.produto_corporativo:
                    ficha.qtd_homens = total_pagantes_masculino
                    ficha.qtd_mulheres = total_pagantes_feminino
                else:
                    ficha.qtd_meninos = total_pagantes_masculino
                    ficha.qtd_meninas = total_pagantes_feminino
                    ficha.qtd_profs_homens = total_professores_masculino
                    ficha.qtd_profs_mulheres = total_professores_feminino

                ficha.qtd_confirmada = total_pagantes_masculino + total_pagantes_feminino
                ficha.save()
        except Exception as e:
            mensagem_erro = f'Durante a atualização dos pagantes aconteceu um erro: {e}'
            enviar_email_erro(mensagem_erro, 'ERRO NA ATUALIZAÇÃO DOS PAGANTES')
        else:
            enviar_email_erro(
                f'Atualização realizada com sucesso as {datetime.now().strftime("%d/%m/%Y %H:%M")}',
                'ATUALIZAÇÃO REALIZADA COM SUCESSO'
            )
    else:
        enviar_email_erro(
            f'Erro na conexão com o servidor de pagamentos, código {response.status_code}',
            'ERRO DE CONEXÃO COM SERVIDOR'
        )
