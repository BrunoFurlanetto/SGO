import datetime
import json
from itertools import chain
from tkinter import *

from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Table, TableStyle
import io
import os

from random import randint

from cadastro.models import RelatorioDeAtendimentoPublicoCeu, RelatorioDeAtendimentoColegioCeu, \
    RelatorioDeAtendimentoEmpresaCeu
from ceu.models import Professores, Valores


def pt(mm):
    return mm / 0.3527777777782


def px(mm):
    return mm / 0.264583


def criar_pdf_relatorio():
    pasta = os.path.dirname(__file__)
    pdf = canvas.Canvas(pasta + '\\resumo.pdf', pagesize=A4, bottomup=0)
    pdf.setTitle('Resumo financeiro')

    pdf.drawImage(
        r'C:\Users\bruno\OneDrive\Área de Trabalho\Projetos\SGO\projetoCEU\templates\static\img\logoPeraltasResumo.jpg',
        x=pt(20), y=pt(20), width=200, height=42.83, preserveAspectRatio=True)
    pdf.drawImage(
        r'C:\Users\bruno\OneDrive\Área de Trabalho\Projetos\SGO\projetoCEU\templates\static\img\logoResumo.jpg',
        x=pt(140), y=pt(20), width=150, height=57.78, preserveAspectRatio=True)

    pdf.setFont('Times-Bold', 18)
    pdf.drawCentredString(x=pt(105), y=pt(55), text='RESUMO FINANCEIRO')

    pdf.setFont('Times-Roman', 16)
    pdf.drawCentredString(x=pt(105), y=pt(62), text='FUNDAÇÃO CEU')

    pdf.setFont('Times-Bold', 14)
    cabecalho = ['Professor', 'Atividades', 'Diárias', 'Valor atividades', 'Valor diárias', 'Reembolso', 'Total']
    data = []

    pdf.setFont('Times-Roman', 12)
    professores = Professores.objects.all()

    for professor in professores:
        data.append(pegar_dados_relatorios(professor))

    data.append(cabecalho)

    table_resumo = Table(data, rowHeights=15, repeatRows=1)

    estilo_tabela = TableStyle([
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#fcc607')),
        ('LINEABOVE', (0, -1), (-1, -1), 0.80, colors.black),
        ('LINEABOVE', (0, 1), (-1, -2), 1, colors.white),
        ('LINEBEFORE', (1, 0), (-1, -1), 0.5, colors.black, 0, None, None, 2, 1),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('LEADING', (0, 0), (-1, -1), 26),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 0), (0, -2), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])

    for linha in range(len(data) - 1):
        if linha % 2 == 0:
            cor_linha = colors.lightblue
        else:
            cor_linha = colors.aliceblue

        estilo_tabela.add('BACKGROUND', (0, linha), (-1, linha), cor_linha)

    table_resumo.setStyle(estilo_tabela)

    table_resumo.wrapOn(pdf, 150, 150)
    table_resumo.drawOn(pdf, pt(20), pt(70))

    pdf.save()


def pegar_dados_relatorios(professor):
    valor_atividade = Valores.objects.get(tipo='Atividade')
    valor_diaria = Valores.objects.get(tipo='Diária')

    n_atividades = 0
    diarias = 0
    datas = []

    relatorios_publico = RelatorioDeAtendimentoPublicoCeu.objects.filter(
        data_atendimento__month=datetime.datetime.now().month).filter(
        equipe__icontains=json.dumps(professor.usuario.first_name))

    relatorios_colegio = RelatorioDeAtendimentoColegioCeu.objects.filter(
        check_in__month__lte=datetime.datetime.now().month,
        check_out__month__gte=datetime.datetime.now().month).filter(
        equipe__icontains=json.dumps(professor.usuario.first_name))

    relatorios_empresa = RelatorioDeAtendimentoEmpresaCeu.objects.filter(
        check_in__month__lte=datetime.datetime.now().month,
        check_out__month__gte=datetime.datetime.now().month).filter(
        equipe__icontains=json.dumps(professor.usuario.first_name))

    relatorios = list(chain(relatorios_publico, relatorios_colegio, relatorios_empresa))

    for relatorio in relatorios:
        if relatorio.atividades:
            for atividade in relatorio.atividades:

                if professor.usuario.first_name in relatorio.atividades[atividade]['professores']:
                    n_atividades += 1

                    if relatorio.atividades[atividade]['data_e_hora'] not in datas:
                        datas.append(relatorio.atividades[atividade]['data_e_hora'])

    if professor.diarista:
        diarias = len(datas)

    dados = [
        professor.usuario.get_full_name(),
        n_atividades,
        diarias,
        converter_dinheiro(n_atividades * valor_atividade.valor_pago),
        converter_dinheiro(diarias * valor_diaria.valor_pago),
        converter_dinheiro(0),
        converter_dinheiro(n_atividades * valor_atividade.valor_pago + diarias * valor_diaria.valor_pago)
    ]

    return dados


def converter_dinheiro(valor):
    dinheiro = f'R$ {valor}'

    return dinheiro.replace('.', ',')
