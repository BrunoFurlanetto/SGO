from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.colors import white, darkblue, black
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

from reportlab.platypus import Paragraph

from orcamento.models import Orcamento


def marca_dagua(c):
    largura, altura = A4
    c.setFont("Helvetica", 35)
    c.setFillColorRGB(0.7, 0.7, 0.7, alpha=0.7)
    c.saveState()
    c.rotate(45)
    x = (largura + c.stringWidth('Pré orçamento - sem valor de negociação', "Helvetica", 35)) / 7
    y = altura / 13
    c.drawString(x, y, 'Pré orçamento - sem valor de negociação')
    c.restoreState()


def iniciar_nova_pagina(c, pre_orcamento=False):
    largura, altura = A4
    draw_vertical_gradient(c, steps=300)
    desenhar_elementos_fixos(c)
    c.setFont("RedHatDisplay-Bold", 32.5)
    c.setFillColor('#003271')
    c.drawString(2 * cm, altura - 3 * cm, "PROPOSTA COMERCIAL")
    c.setFont("Montserrat-Bold", 12)
    c.setFillColor(black)

    if pre_orcamento:
        marca_dagua(c)


def cm_to_pt(value_cm):
    return value_cm * cm


def carregar_fontes_personalizadas():
    """
    Carrega Red Hat Display e Montserrat (Regular, Bold, Italic) a partir da pasta_fontes.
    """
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    pasta_fontes = os.path.join(diretorio_atual, 'modelos', 'fonts')
    fontes = {
        "RedHatDisplay": {
            "regular": "RedHatDisplay-Regular.ttf",
            "bold": "RedHatDisplay-Bold.ttf",
            "italic": "RedHatDisplay-Italic.ttf",
        },
        "Montserrat": {
            "regular": "Montserrat-Regular.ttf",
            "bold": "Montserrat-Bold.ttf",
            "italic": "Montserrat-Italic.ttf",
        }
    }

    for nome_base, variacoes in fontes.items():
        for estilo, arquivo in variacoes.items():
            caminho_completo = os.path.join(pasta_fontes, arquivo)
            nome_registro = nome_base

            if not os.path.exists(caminho_completo):
                raise FileNotFoundError(f"Fonte {arquivo} não encontrada em {pasta_fontes}")

            if estilo == "bold":
                nome_registro += "-Bold"
            elif estilo == "italic":
                nome_registro += "-Italic"

            pdfmetrics.registerFont(TTFont(nome_registro, caminho_completo))

    pdfmetrics.registerFontFamily(
        'Montserrat',
        normal='Montserrat',
        bold='Montserrat-Bold',
        italic='Montserrat-Italic'
    )

    pdfmetrics.registerFontFamily(
        'RedHatDisplay',
        normal='RedHatDisplay',
        bold='RedHatDisplay-Bold',
        italic='RedHatDisplay-Italic'
    )


def desenhar_bloco_texto(
        c,
        x_inicial_cm,
        y_inicial_cm,
        textos,
        largura_maxima_cm=13.0,
        tamanho_fonte=12.0,
        linha_offset_cm=0.3,
        fontName='Montserrat',
        line_spacing_cm=1.0,
):
    largura, altura = A4
    x = x_inicial_cm * cm
    y = altura - (y_inicial_cm * cm)
    largura_maxima = largura_maxima_cm * cm

    # ⚡ Criar um estilo novo, não usar getSampleStyleSheet()
    style = ParagraphStyle(
        name="EstiloPersonalizado",
        fontName=fontName,  # Fonte base (normal)
        fontSize=tamanho_fonte,
        leading=tamanho_fonte * line_spacing_cm,  # Espaçamento interno entre linhas (1.5x)
        textColor='black',
        alignment=TA_JUSTIFY
    )

    for texto in textos:
        p = Paragraph(texto, style)
        width, height = p.wrap(largura_maxima, 9999)  # define largura máxima; altura é dinâmica
        p.drawOn(c, x, y - height)
        y -= (height + linha_offset_cm * cm)

    return y


def draw_vertical_gradient(c, steps=100):
    x = 0
    y = 0.4 * cm
    width = 1.31 * cm
    height = 29.52 * cm
    start_color = darkblue
    end_color = white

    for i in range(steps):
        ratio = i / steps
        r = start_color.red + (end_color.red - start_color.red) * ratio
        g = start_color.green + (end_color.green - start_color.green) * ratio
        b = start_color.blue + (end_color.blue - start_color.blue) * ratio
        c.setFillColorRGB(r, g, b)

        # Desenha de cima para baixo
        y_step = y + height * (1 - (i + 1) / steps)
        c.rect(x, y_step, width, height / steps, stroke=0, fill=1)


def desenhar_elementos_fixos(c):
    c.drawImage(
        'orcamento/modelos/logo_peraltas.png',
        cm_to_pt(15.60),
        cm_to_pt(29.7 - 3.2 - 3.40),
        width=cm_to_pt(3.8),
        height=cm_to_pt(3.4),
        mask='auto'
    )

    c.drawImage(
        'orcamento/modelos/insta.png',
        cm_to_pt(9.2),
        cm_to_pt(29.7 - 25.5 - 3.40),
        width=cm_to_pt(0.7),
        height=cm_to_pt(0.7),
        mask='auto'
    )

    c.drawImage(
        'orcamento/modelos/fone.png',
        cm_to_pt(15.8),
        cm_to_pt(29.7 - 25.5 - 3.40),
        width=cm_to_pt(0.7),
        height=cm_to_pt(0.7),
        mask='auto'
    )

    # Retângulo 1 (marrom escuro)
    c.setFillColor("#30231B")
    c.rect(
        cm_to_pt(-0.03),
        cm_to_pt(0),  # conversão topo para base do canvas
        cm_to_pt(1.89),
        cm_to_pt(0.60),
        stroke=0,
        fill=1
    )

    # Retângulo 2 (azul escuro)
    c.setFillColor("#003271")
    c.rect(
        cm_to_pt(2.04),
        cm_to_pt(0),
        cm_to_pt(18.97),
        cm_to_pt(0.60),
        stroke=0,
        fill=1
    )

    # --------------------------------------- Informações de rodapé ----------------------------------------------------
    c.setFont("Montserrat", 12)
    c.setFillColor(black)
    c.drawString(10 * cm, cm_to_pt(29.7 - 25.3 - 3.40), "@peraltasacampamento")
    c.drawString(16.6 * cm, cm_to_pt(29.7 - 25.3 - 3.40), "(11) 9 4384 - 3828")


def desenhar_icones_segunda_pagina(c, x_inicial_cm=2.0, x_final_cm=15.0, altura_img_cm=1.4):
    largura_total_cm = x_final_cm - x_inicial_cm
    caminhos_imagens = [
        "orcamento/modelos/icone_pedagogica.png",
        "orcamento/modelos/icone_eco.png",
        "orcamento/modelos/icone_ceu.png",
        "orcamento/modelos/icone_lazer.png"
    ]
    num_imagens = len(caminhos_imagens)
    largura_img_cm = 2.0  # Definindo uma largura fixa por imagem (exemplo)

    # Espaço entre as imagens
    if num_imagens > 1:
        espaco_entre_cm = (largura_total_cm - (num_imagens * largura_img_cm)) / (num_imagens - 1)
    else:
        espaco_entre_cm = 0

    x_atual_cm = x_inicial_cm
    altura, largura = A4
    y_pt = altura + (3.6 * cm)  # converter a posição y

    for caminho_imagem in caminhos_imagens:
        x_pt = x_atual_cm * cm
        c.drawImage(
            caminho_imagem,
            x_pt,
            y_pt,
            width=largura_img_cm * cm,
            height=altura_img_cm * cm,
            preserveAspectRatio=True,
            mask='auto'
        )
        x_atual_cm += largura_img_cm + espaco_entre_cm


def primeira_pagina(c, orcamento, pre_orcamento=False):
    largura, altura = A4
    iniciar_nova_pagina(c, pre_orcamento)

    # Dados do colégio, responsável e consultor
    dados_cliente_responsavel = [
        f'NOME DO COLÉGIO: {orcamento.cliente.nome_fantasia}',
        f'RESPONSÁVEL: {orcamento.responsavel.nome}',
        f'TELEFONE: {orcamento.responsavel.fone}',
        f'E-MAIL: {orcamento.responsavel.email_responsavel_evento}',
    ]
    dados_consultor = [
        f'CONSULTOR RESPONSÁVEL: {orcamento.colaborador.get_full_name()}',
        f'TELEFONE: {orcamento.colaborador.vendedor.telefone_formatado}',
        f'E-MAIL: {orcamento.colaborador.email}',
    ]
    y_atual = desenhar_bloco_texto(c, 2.25, 3.8, dados_cliente_responsavel)
    y_atual = desenhar_bloco_texto(c, 2.25, (altura - y_atual + (0.4 * cm)) / cm, dados_consultor)
    c.setStrokeColor(colors.HexColor('#6F6A7B'))
    c.setLineWidth(0.1)
    c.setStrokeAlpha(0.4)
    c.line(2.1 * cm, y_atual, (2.1 * cm + 17 * cm), y_atual)

    # -------------------------------------------- Dados do pacote -----------------------------------------------------
    # -------------------------------------------- Dados do produto ----------------------------------------------------
    c.setFont("Montserrat-Bold", 12)
    c.setFillColor(black)
    c.drawString(2.17 * cm, y_atual - 0.7 * cm, "INFORMAÇÕES DO PACOTE CONTRATADO")
    y_atual = y_atual - 0.7 * cm
    dados_produto_e_check_in = [
        f'<b>PACOTE CONTRATADO</b>: {orcamento.produto.produto}',
        f'<b>CHECK-IN & CHECK-OUT</b>: {orcamento.check_in.astimezone().strftime("%d/%m/%Y %H:%M")} - {orcamento.check_out.astimezone().strftime("%d/%m/%Y %H:%M")}',
    ]
    y_atual = desenhar_bloco_texto(c, 4, (altura - y_atual + (0.5 * cm)) / cm, dados_produto_e_check_in,
                                   largura_maxima_cm=15, linha_offset_cm=0.4)
    c.drawImage(
        'orcamento/modelos/icone_produto.png',
        cm_to_pt(2.23),
        cm_to_pt((y_atual / cm) + 0.1),
        width=cm_to_pt(1.73),
        height=cm_to_pt(1.73),
        mask='auto'
    )

    # ----------------------------------------- Dados da alimentação ---------------------------------------------------
    c.setFont("Montserrat-Bold", 12)
    c.setFillColor(black)
    c.drawString(8 * cm, y_atual - 0.8 * cm, "ALIMENTAÇÕES INCLUSAS")
    y_atual = y_atual - 0.8 * cm

    if orcamento.dias_evento == 1:
        dados_alimentacao = [orcamento.alimentacao_saida]
    elif orcamento.dias_evento == 2:
        dados_alimentacao = [
            f'Primeiro dia: {orcamento.alimentacao_entrada}',
            f'Segundo dia: {orcamento.alimentacao_saida}',
        ]
    else:
        dados_alimentacao = [
            f'<b>Primeiro dia</b>: {orcamento.alimentacao_entrada}',
            f'<b>Último dia</b>: {orcamento.alimentacao_saida}',
            f'<b>Demais dia</b>: Café da manhã, Almoço, Jantar e Chá da noite',
        ]

    y_atual = desenhar_bloco_texto(c, 4, (altura - y_atual + (0.2 * cm)) / cm, dados_alimentacao, largura_maxima_cm=15)
    c.drawImage(
        'orcamento/modelos/icone_alimentos.png',
        cm_to_pt(2.17),
        cm_to_pt((y_atual / cm) + (0.1 * orcamento.dias_evento)),
        width=cm_to_pt(1.82),
        height=cm_to_pt(1.82),
        mask='auto'
    )

    # ------------------------------------------- Dados monitoria ------------------------------------------------------
    c.setFont("Montserrat-Bold", 12)
    c.setFillColor(black)
    c.drawString(8 * cm, y_atual - 0.8 * cm, "MONITORIA CONTRATADA")
    y_atual = y_atual - 0.8 * cm
    y_atual = desenhar_bloco_texto(c, 4, (altura - y_atual + (0.2 * cm)) / cm,
                                   [orcamento.tipo_monitoria.descricao_monitoria], largura_maxima_cm=15,
                                   line_spacing_cm=1.5)
    c.drawImage(
        'orcamento/modelos/icone_monitoria.png',
        cm_to_pt(2.34),
        cm_to_pt((y_atual / cm) + (0.9 * int(not orcamento.tipo_monitoria.sem_monitoria))),
        width=cm_to_pt(1.49),
        height=cm_to_pt(1.49),
        mask='auto'
    )

    # ---------------------------------------- Dados Transporte --------------------------------------------------------
    c.setFont("Montserrat-Bold", 12)
    c.setFillColor(black)
    c.drawString(7 * cm, y_atual - 0.8 * cm, "INFORMAÇÕES DO TRANSPORTE")
    y_atual = y_atual - 0.8 * cm

    if orcamento.transporte == 'sim':
        y_atual = desenhar_bloco_texto(
            c,
            4,
            (altura - y_atual + (0.2 * cm)) / cm,
            [orcamento.infos_transporte], largura_maxima_cm=15,
            line_spacing_cm=1.5
        )

        c.drawImage(
            'orcamento/modelos/icone_transporte.png',
            cm_to_pt(2.38),
            cm_to_pt((y_atual / cm) + 0.6),
            width=cm_to_pt(1.49),
            height=cm_to_pt(1.49),
            mask='auto'
        )
    else:
        y_atual = desenhar_bloco_texto(
            c,
            4,
            (altura - y_atual + (0.2 * cm)) / cm,
            ["Transporte de ida e volta não contemplado no pacote."], largura_maxima_cm=15,
            line_spacing_cm=1.5
        )

        c.drawImage(
            'orcamento/modelos/icone_transporte.png',
            cm_to_pt(2.38),
            cm_to_pt(y_atual / cm),
            width=cm_to_pt(1.49),
            height=cm_to_pt(1.49),
            mask='auto'
        )

    # ----------------------------------------- Observações importantes ------------------------------------------------
    c.setFont("Montserrat-Bold", 12)
    c.setFillColor(black)
    c.drawString(7 * cm, y_atual - 0.8 * cm, "OBSERVAÇÕES IMORTANTES")
    y_atual = y_atual - 0.8 * cm
    obs = [
        'Não oferecemos acomodações para motoristas quando o transporte não for operado por nós.',
        'O pacote inclui roupa de cama. Trazer toalha de banho e de piscina.',
        'É fundamental que cada aluno traga suas próprias toalhas para a piscina e para banho.',
    ]

    y_atual = desenhar_bloco_texto(
        c,
        2.25,
        (altura - y_atual + (0.2 * cm)) / cm,
        obs, largura_maxima_cm=16.55,
        line_spacing_cm=1.5
    )

    c.showPage()


def segunda_pagina(c, orcamento, pre_orcamento=False):
    largura, altura = A4
    iniciar_nova_pagina(c, pre_orcamento)
    desenhar_icones_segunda_pagina(c)
    c.setFont("Montserrat-Bold", 12)
    c.setFillColor(black)
    c.drawString(2.25 * cm, altura - 6 * cm, "ATIVIDADES CONTRATADAS")
    y_atual = altura - 6 * cm

    # ---------------------------------------- Informações dos opcionais -----------------------------------------------
    for opcional in orcamento.opcionais.all():
        if y_atual <= 80:
            c.showPage()
            iniciar_nova_pagina(c, pre_orcamento)
            desenhar_icones_segunda_pagina(c)
            c.setFont("Montserrat-Bold", 12)
            c.setFillColor(black)
            c.drawString(2.25 * cm, altura - 6 * cm, "ATIVIDADES CONTRATADAS")
            y_atual = altura - 6 * cm

        c.setFont("Montserrat-Bold", 12)
        c.setFillColor(black)
        c.drawString(2.85 * cm, y_atual - 0.8 * cm, opcional.nome)
        y_atual = y_atual - 0.8 * cm
        y_atual = desenhar_bloco_texto(
            c,
            3.7,
            (altura - y_atual + (0.2 * cm)) / cm,
            [opcional.descricao], largura_maxima_cm=15.10,
            line_spacing_cm=1.5
        )

    # ------------------------------------------------- Condições finais -----------------------------------------------
    if y_atual <= 300:
        c.showPage()
        iniciar_nova_pagina(c, pre_orcamento)
        c.drawString(7 * cm, altura - 6 * cm, "CONDIÇÕES FINAIS")
        y_atual = altura - 6 * cm
    else:
        c.drawString(2.25 * cm, y_atual - 0.8 * cm, "CONDIÇÕES FINAIS")
        y_atual = y_atual - 0.8 * cm

    condicoes_finais = [
        'Serão disponibilizadas 05 cortesias para professors e coordenadores acompanharem o grupo.',
        'Para cada cortesia adicional, será cobrado 50% do valor do pacote.',
        'Esse pacote inclui transporte de ida e volta, estadia de 3 dias com pensão completa (2 cafés, 2 almoços, 2 jantares e 4 lanches), com entrada as 10hs para almoço,  Monitoria na proporção media de 1/12 alunos, Seguro saúde, 3 atividades no Centro de Estudos, entrevista com Astornomos conforme a programação de estudos e atividades.',
    ]
    y_atual = desenhar_bloco_texto(
        c,
        2.85,
        (altura - y_atual + (0.2 * cm)) / cm,
        condicoes_finais, largura_maxima_cm=15.95,
        line_spacing_cm=1.5
    )

    # --------------------------------------------- Informações de pagamento -------------------------------------------
    c.setFont("Montserrat-Bold", 12)
    c.setFillColor(black)
    c.drawString(2.25 * cm, y_atual - 0.8 * cm, "INVESTIMENTO POR ALUNO")
    y_atual = y_atual - 0.8 * cm

    dados_pagamento = [
        'Um total de ' + f'<b>R$ {orcamento.valor}</b>'.replace('.', ',') + ' por aluno. Em até 6x',
    ]
    y_atual = desenhar_bloco_texto(
        c,
        4,
        (altura - y_atual + (0.2 * cm)) / cm,
        dados_pagamento, largura_maxima_cm=16.55,
        line_spacing_cm=1.5
    )

    c.setFont("Montserrat-Bold", 12)
    c.setFillColor(black)
    c.drawString(4 * cm, y_atual - 0.8 * cm, "FORMA DE PAGAMENTO")
    y_atual = y_atual - 0.8 * cm
    dados_forma_pagamento = [
        'Os pagamento podem ser realizados de duas maneiras',
        '1. <b>Via Sistema Peraltas</b>: Até 6 parcelas mensais consecutivas.',
        '2. <b>Via Escola</b>: Em até 5 parcelas.',
    ]
    y_atual = desenhar_bloco_texto(
        c,
        4,
        (altura - y_atual + (0.2 * cm)) / cm,
        dados_forma_pagamento, largura_maxima_cm=16.55,
        line_spacing_cm=1.5
    )
    c.drawImage(
        'orcamento/modelos/icone_pagamentos.png',
        cm_to_pt(2.25),
        cm_to_pt((y_atual / cm) + 2),
        width=cm_to_pt(1.49),
        height=cm_to_pt(1.43),
        mask='auto'
    )


def gerar_pdf_orcamento(orcamento, pre_orcamento=False):
    buffer = BytesIO()
    c = Canvas(buffer, pagesize=A4)
    carregar_fontes_personalizadas()
    largura, altura = A4

    # Desenhar elementos fixos no template
    primeira_pagina(c, orcamento, pre_orcamento=pre_orcamento)
    segunda_pagina(c, orcamento, pre_orcamento=pre_orcamento)

    c.save()
    buffer.seek(0)

    return buffer
