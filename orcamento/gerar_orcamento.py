import re
from io import BytesIO

from PyPDF2 import PdfWriter, PdfReader
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

from orcamento.models import Orcamento, TemplateOrcamento


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
    bulletText="•",
    recuo_bullet_cm=0.5,
):
    largura, altura = A4
    x_base = x_inicial_cm * cm
    y = altura - (y_inicial_cm * cm)
    largura_maxima = largura_maxima_cm * cm

    style = ParagraphStyle(
        name="EstiloPersonalizado",
        fontName=fontName,
        fontSize=tamanho_fonte,
        leading=tamanho_fonte * line_spacing_cm,
        textColor='black',
        alignment=TA_JUSTIFY
    )

    for texto in textos:
        # 1) Se vier blocos de <p>...</p>, extrai cada parágrafo
        if '<p>' in texto and '</p>' in texto:
            paragrafos = re.findall(r'<p>(.*?)</p>', texto, flags=re.DOTALL)
            for par in paragrafos:
                p = Paragraph(par, style)
                w, h = p.wrap(largura_maxima, 9999)
                p.drawOn(c, x_base, y - h)
                y -= (h + linha_offset_cm*cm)
            continue

        # 2) Lista ordenada
        if '<ol>' in texto and '</ol>' in texto:
            itens = re.findall(r'<li>(.*?)</li>', texto, flags=re.DOTALL)
            for idx, item in enumerate(itens, start=1):
                p = Paragraph(item, style, bulletText=f"{idx}.")
                x = x_base + recuo_bullet_cm * cm
                w, h = p.wrap(largura_maxima - recuo_bullet_cm*cm, 9999)
                p.drawOn(c, x, y - h)
                y -= (h + linha_offset_cm*cm)
            continue

        # 3) Lista não ordenada
        if '<ul>' in texto and '</ul>' in texto:
            itens = re.findall(r'<li>(.*?)</li>', texto, flags=re.DOTALL)
            for item in itens:
                p = Paragraph(item, style, bulletText=bulletText)
                x = x_base + recuo_bullet_cm * cm
                w, h = p.wrap(largura_maxima - recuo_bullet_cm*cm, 9999)
                p.drawOn(c, x, y - h)
                y -= (h + linha_offset_cm*cm)
            continue

        # 4) Texto simples (inline <b>,<i> etc. já são entendidos)
        p = Paragraph(texto, style)
        w, h = p.wrap(largura_maxima, 9999)
        p.drawOn(c, x_base, y - h)
        y -= (h + linha_offset_cm*cm)

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
    c.drawString(6 * cm, y_atual - 0.7 * cm, "INFORMAÇÕES DO PACOTE CONTRATADO")
    y_atual = y_atual - 0.7 * cm
    dados_produto_e_check_in = [
        f'<b>PACOTE CONTRATADO</b>: {orcamento.produto.produto}',
        f'<b>CHECK-IN</b>: {orcamento.check_in.astimezone().strftime("%d/%m/%Y às %H:%M")}',
        f'<b>CHECK-OUT</b>: {orcamento.check_out.astimezone().strftime("%d/%m/%Y às %H:%M")}',
    ]
    y_atual = desenhar_bloco_texto(c, 4, (altura - y_atual + (0.5 * cm)) / cm, dados_produto_e_check_in,
                                   largura_maxima_cm=15, linha_offset_cm=0.4)
    c.drawImage(
        'orcamento/modelos/icone_produto.png',
        cm_to_pt(2.23),
        cm_to_pt((y_atual / cm) + 0.5),
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
            f'<b>Primeiro dia</b>: {orcamento.alimentacao_entrada}',
            f'<b>Segundo dia</b>: {orcamento.alimentacao_saida}',
        ]
    else:
        dados_alimentacao = [
            f'<b>Primeiro dia</b>: {orcamento.alimentacao_entrada}',
            f'<b>Demais dia</b>: Café da manhã, Almoço, Jantar e Chá da noite',
            f'<b>Último dia</b>: {orcamento.alimentacao_saida}',
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

    c.showPage()


def segunda_pagina(c, orcamento, pre_orcamento=False):
    largura, altura = A4
    iniciar_nova_pagina(c, pre_orcamento)
    desenhar_icones_segunda_pagina(c)
    c.setFont("Montserrat-Bold", 12)
    c.setFillColor(black)
    c.drawString(6.5 * cm, altura - 6 * cm, "ATIVIDADES CONTRATADAS")
    y_atual = altura - 6 * cm

    # ---------------------------------------- Informações dos opcionais -----------------------------------------------
    for opcional in orcamento.opcionais.all():
        if not opcional.categoria.staff:
            if y_atual <= 200:
                c.showPage()
                iniciar_nova_pagina(c, pre_orcamento)
                desenhar_icones_segunda_pagina(c)
                c.setFont("Montserrat-Bold", 12)
                c.setFillColor(black)
                c.drawString(6 * cm, altura - 6 * cm, "ATIVIDADES CONTRATADAS")
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

    # ------------------------------------------------- Outros itens ---------------------------------------------------
    if orcamento.opcionais_extra:
        if y_atual <= 200:
            c.showPage()
            iniciar_nova_pagina(c, pre_orcamento)
            desenhar_icones_segunda_pagina(c)
            c.setFont("Montserrat-Bold", 12)
            c.setFillColor(black)
            c.drawString(8.5 * cm, altura - 6 * cm, "OUTROS ITENS")
            y_atual = altura - 6 * cm
        else:
            c.setFont("Montserrat-Bold", 12)
            c.setFillColor(black)
            c.drawString(8.5 * cm, y_atual - 0.8 * cm, "OUTROS ITENS")
            y_atual = y_atual - 0.8 * cm

        for outro in orcamento.opcionais_extra:
            if y_atual <= 200:
                c.showPage()
                iniciar_nova_pagina(c, pre_orcamento)
                desenhar_icones_segunda_pagina(c)
                c.setFont("Montserrat-Bold", 12)
                c.setFillColor(black)
                c.drawString(8.5 * cm, altura - 6 * cm, "OUTROS ITENS")
                y_atual = altura - 6 * cm

            c.setFont("Montserrat-Bold", 12)
            c.setFillColor(black)
            c.drawString(2.85 * cm, y_atual - 0.8 * cm, outro['nome'])
            y_atual = y_atual - 0.8 * cm
            y_atual = desenhar_bloco_texto(
                c,
                3.7,
                (altura - y_atual + (0.2 * cm)) / cm,
                [outro['descricao']], largura_maxima_cm=15.10,
                line_spacing_cm=1.5
            )

    # ----------------------------------------------- Observações ------------------------------------------------------
    if orcamento.observacoes:
        if y_atual <= 200:
            c.showPage()
            iniciar_nova_pagina(c, pre_orcamento)
            desenhar_icones_segunda_pagina(c)
            c.setFont("Montserrat-Bold", 12)
            c.setFillColor(black)
            c.drawString(8.5 * cm, altura - 6 * cm, "OBSERVAÇÕES")
            y_atual = altura - 6 * cm
        else:
            c.setFont("Montserrat-Bold", 12)
            c.setFillColor(black)
            c.drawString(8.5 * cm, y_atual - 0.8 * cm, "OBSERVAÇÕES")
            y_atual = y_atual - 0.8 * cm

        y_atual = desenhar_bloco_texto(
            c,
            2.85,
            (altura - y_atual + (0.2 * cm)) / cm,
            [orcamento.observacoes], largura_maxima_cm=15.95,
            line_spacing_cm=1.5
        )
    print(y_atual)
    # ----------------------------------------- Observações importantes ------------------------------------------------
    if y_atual <= 158:
        c.showPage()
        iniciar_nova_pagina(c, pre_orcamento)
        desenhar_icones_segunda_pagina(c)
        c.setFont("Montserrat-Bold", 12)
        c.setFillColor(black)
        c.drawString(7 * cm, y_atual - 6 * cm, "OBSERVAÇÕES IMORTANTES")
        y_atual = altura - 6 * cm
    else:
        c.setFont("Montserrat-Bold", 12)
        c.setFillColor(black)
        c.drawString(7 * cm, y_atual - 0.8 * cm, "OBSERVAÇÕES IMORTANTES")
        y_atual = y_atual - 0.8 * cm

    obs = [
        '<ul><li>Não oferecemos acomodações para motoristas quando o transporte não for operado por nós.</li></ul>',
        '<ul><li>É fundamental que cada aluno traga suas próprias toalhas para a piscina e para banho, com nome do aluno</li></ul>',
    ]

    y_atual = desenhar_bloco_texto(
        c,
        2.25,
        (altura - y_atual + (0.2 * cm)) / cm,
        obs, largura_maxima_cm=16.55,
        line_spacing_cm=1.5,
    )

    # ------------------------------------------------- Condições finais -----------------------------------------------
    c.setFont("Montserrat-Bold", 12)
    c.setFillColor(black)

    if y_atual <= 300:
        c.showPage()
        iniciar_nova_pagina(c, pre_orcamento)
        c.setFont("Montserrat-Bold", 12)
        c.setFillColor(black)
        c.drawString(8 * cm, altura - 6.5 * cm, "CONDIÇÕES FINAIS")
        y_atual = altura - 6.5 * cm
    else:
        c.setFont("Montserrat-Bold", 12)
        c.setFillColor(black)
        c.drawString(8 * cm, y_atual - 0.8 * cm, "CONDIÇÕES FINAIS")
        y_atual = y_atual - 0.8 * cm

    condicoes_finais = [orcamento.condicoes_finais]
    y_atual = desenhar_bloco_texto(
        c,
        2.85,
        (altura - y_atual + (0.2 * cm)) / cm,
        condicoes_finais, largura_maxima_cm=15.95,
        line_spacing_cm=1.5
    )

    # --------------------------------------------- Informações de pagamento -------------------------------------------

    if y_atual <= 230:
        c.showPage()
        iniciar_nova_pagina(c, pre_orcamento)
        c.setFont("Montserrat-Bold", 12)
        c.setFillColor(black)
        c.drawString(7.5 * cm, altura - 6.5 * cm, "INVESTIMENTO POR ALUNO")
        y_atual = altura - 6.5 * cm
    else:
        c.setFont("Montserrat-Bold", 12)
        c.setFillColor(black)
        c.drawString(7.5 * cm, y_atual - 0.8 * cm, "INVESTIMENTO POR ALUNO")
        y_atual = y_atual - 0.8 * cm

    if pre_orcamento:
        dados_pagamento = [
            'Um total de ' + f'<b>R$ {orcamento.valor}</b>'.replace('.', ',') + ' por aluno.',
        ]
    else:
        dados_pagamento = [
            f'Para o fechamento até <b>{orcamento.data_vencimento.strftime("%d/%m/%Y")}</b>, um total de ' + f'<b>R$ {orcamento.valor}</b>'.replace(
                '.', ',') + ' por aluno. Em até 6x.',
        ]

    y_atual = desenhar_bloco_texto(
        c,
        2.85,
        (altura - y_atual + (0.2 * cm)) / cm,
        dados_pagamento, largura_maxima_cm=15.95,
        line_spacing_cm=1.5
    )

    c.setFont("Montserrat-Bold", 12)
    c.setFillColor(black)
    c.drawString(4 * cm, y_atual - 0.8 * cm, "FORMAS DE PAGAMENTO")
    y_atual = y_atual - 0.8 * cm

    y_atual = desenhar_bloco_texto(
        c,
        4,
        (altura - y_atual + (0.2 * cm)) / cm,
        [orcamento.regras_de_pagamento], largura_maxima_cm=16.55,
        line_spacing_cm=1.5
    )
    c.drawImage(
        'orcamento/modelos/icone_pagamentos.png',
        cm_to_pt(2.25),
        cm_to_pt((y_atual / cm) + 1),
        width=cm_to_pt(1.49),
        height=cm_to_pt(1.43),
        mask='auto'
    )


def mesclar_pdf_dinamico_com_modelo(pdf_dinamico_buffer, caminho_pdf_modelo):
    """
    Mescla o PDF gerado dinamicamente com o modelo fixo, inserindo as páginas dinâmicas
    antes da última página do modelo.

    Args:
        pdf_dinamico_buffer (BytesIO): O buffer contendo o PDF gerado dinamicamente.
        caminho_pdf_modelo (str): Caminho para o arquivo de modelo fixo (.pdf).

    Returns:
        BytesIO: Buffer com o PDF final mesclado.
    """
    # Criar writer para o PDF de saída
    output = PdfWriter()

    # Carregar o modelo fixo
    modelo_reader = PdfReader(caminho_pdf_modelo)

    # Adicionar todas as páginas do modelo, menos a última
    for i in range(len(modelo_reader.pages) - 1):
        output.add_page(modelo_reader.pages[i])

    # Carregar o PDF dinâmico
    dinamico_reader = PdfReader(pdf_dinamico_buffer)

    # Adicionar todas as páginas geradas dinamicamente
    for page in dinamico_reader.pages:
        output.add_page(page)

    # Adicionar a última página do modelo
    output.add_page(modelo_reader.pages[-1])

    # Escrever o PDF final em memória
    resultado_buffer = BytesIO()
    output.write(resultado_buffer)
    resultado_buffer.seek(0)

    return resultado_buffer


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

    try:
        template_orcamento = TemplateOrcamento.objects.get(ano_vigencia=orcamento.check_in.year)
    except TemplateOrcamento.DoesNotExist:
        raise FileNotFoundError(
            f"Não foi encontrado um template para o ano {orcamento.check_in.year}."
        )

    buffer = mesclar_pdf_dinamico_com_modelo(buffer, template_orcamento.arquivo)

    return buffer
