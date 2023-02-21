from datetime import datetime

from fpdf import FPDF

from ceu.models import Atividades, Locaveis
from peraltas.models import AtividadesEco


class PDF(FPDF):
    def __init__(self):
        super().__init__('P', 'mm', 'Letter')
        self.set_font('Times', '', 12)
        self.add_page()

    def my_header(self, titulo):
        self.image('templates/static/img/logoPeraltasResumo.jpg', 15, 10, 65)
        self.ln(10)
        self.set_font('helvetica', 'B', 20)
        w_titulo = self.get_string_width(titulo) + 6
        w_pdf = self.w
        self.set_x((w_pdf - w_titulo) / 2)
        self.cell(w_titulo, 20, titulo, ln=1, align='C')

    def titulo_secao(self, titulo_secao, height, width):
        self.set_font('Times', 'B', 14)
        self.set_fill_color(255, 137, 32)
        self.cell(width, height, titulo_secao, ln=2, fill=True, align='c')
        self.set_font('Times', '', 12)

    def texto_negrito(self, w, h, texto):
        self.set_font('Times', 'B', 12)
        self.cell(w, h, texto)
        self.set_font('Times', '', 12)

    def tables(self, headings, rows, alings=None, col_widths=(75, 35, 56, 15, 15)):
        self.set_fill_color(23, 129, 180)
        self.set_text_color(255)
        self.set_draw_color(174, 167, 53)
        self.set_line_width(0.3)
        self.set_font(style="B")

        for col_width, heading in zip(col_widths, headings):
            self.cell(col_width, 7, heading, border=1, align="C", fill=True)

        self.ln()
        self.set_text_color(0)
        self.set_font()

        for n, row in enumerate(rows):
            if n % 2 == 0:
                self.set_fill_color(255, 198, 148)
            else:
                self.set_fill_color(224, 235, 255)

            for col in range(0, len(col_widths)):
                self.cell(
                    col_widths[col],
                    6,
                    row[col],
                    border="LR",
                    align="L" if not alings else alings[col],
                    fill=True
                )

            self.ln()

        self.cell(sum(col_widths), 0, "", "T")


def ordem_de_servico(ordem_de_servico):
    ficha_de_evento = ordem_de_servico.ficha_de_evento

    pdf_ordem = PDF()
    pdf_ordem.my_header('Ordem de serviço')
    # --------------------------------------------- Dados do cliente ---------------------------------------------------
    pdf_ordem.titulo_secao('Dados do cliente', 5, 0)
    pdf_ordem.ln(1)

    pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Cliente: ') + 1, 8, 'Cliente:')
    pdf_ordem.cell(120, 8, ficha_de_evento.cliente.__str__())

    pdf_ordem.texto_negrito(pdf_ordem.get_string_width('CNPJ: ') + 1, 8, 'CNPJ:')
    pdf_ordem.cell(0, 8, ficha_de_evento.cliente.cnpj, ln=1)

    pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Endereço: ') + 1, 8, 'Endereço:')
    pdf_ordem.cell(110, 8, ficha_de_evento.cliente.endereco)

    pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Bairro: ') + 1, 8, 'Bairro:')
    pdf_ordem.cell(40, 8, ficha_de_evento.cliente.bairro, ln=1)

    pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Cidade: ') + 1, 8, 'Cidade:')
    pdf_ordem.cell(90, 8, ficha_de_evento.cliente.cidade)

    pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Estado: ') + 1, 8, 'Estado:')
    pdf_ordem.cell(20, 8, ficha_de_evento.cliente.estado)

    pdf_ordem.texto_negrito(pdf_ordem.get_string_width('CEP: ') + 1, 8, 'CEP:')
    pdf_ordem.cell(30, 8, ficha_de_evento.cliente.cep, ln=1)

    pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Código APP PJ: ') + 2, 8, 'Código APP PJ:')
    pdf_ordem.cell(30, 8, str(ficha_de_evento.codigos_app.cliente_pj))

    pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Código APP PF: ') + 2, 8, 'Código APP PF:')
    pdf_ordem.cell(30, 8, str(ficha_de_evento.codigos_app.cliente_pf), ln=1)

    pdf_ordem.ln(4)
    # ------------------------------------------ Dados do evento -------------------------------------------------------
    pdf_ordem.titulo_secao('Dados do evento', 5, 0)
    pdf_ordem.ln(2)

    pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Check in: ') + 1, 8, 'Check in:')
    check_in = ordem_de_servico.check_in.astimezone().strftime('%d/%m/%Y %H:%M')
    pdf_ordem.cell(pdf_ordem.get_string_width(check_in) + 10, 8, check_in)

    pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Check out: ') + 1, 8, 'Check out:')
    check_out = ordem_de_servico.check_out.astimezone().strftime('%d/%m/%Y %H:%M')
    pdf_ordem.cell(pdf_ordem.get_string_width(check_out) + 10, 8, check_out)

    if pdf_ordem.get_string_width(ficha_de_evento.responsavel_evento.nome) > 50:
        pdf_ordem.ln()

    pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Responsável: ') + 1, 8, 'Responsável:')
    nome_responsavel = ficha_de_evento.responsavel_evento.nome
    pdf_ordem.cell(pdf_ordem.get_string_width(nome_responsavel), 8, nome_responsavel, ln=1)

    pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Produto contratado: ') + 3, 8, 'Produto contratado:')
    pdf_ordem.multi_cell(100, 8, ficha_de_evento.produto.produto, ln=1)

    if ficha_de_evento.produto_corporativo:
        pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Produto corporativo: ') + 3, 8, 'Produto corporativo:')
        pdf_ordem.multi_cell(100, 8, ficha_de_evento.produto_corporativo.produto, ln=1)
    else:
        pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Perfíl do grupo: ') + 2, 8, 'Perfil do grupo:')
        pdf_ordem.cell(pdf_ordem.get_string_width(ordem_de_servico.serie) + 10, 8, ordem_de_servico.serie)

        if pdf_ordem.get_string_width(ordem_de_servico.serie) + 10 > 96:
            pdf_ordem.ln(8)

        pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Professores: ') + 2, 8, 'Professores:')
        pdf_ordem.cell(10, 8, str(ordem_de_servico.n_professores))

    pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Participantes: ') + 2, 8, 'Participantes:')
    pdf_ordem.cell(10, 8, str(ordem_de_servico.n_participantes), ln=1)

    pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Código eficha: ') + 1, 8, 'Código eficha:')
    pdf_ordem.multi_cell(100, 8, ficha_de_evento.codigos_app.evento, ln=1)

    pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Código APP reserva: ') + 2, 8, 'Código APP reserva:')
    pdf_ordem.cell(100, 8, ficha_de_evento.codigos_app.reserva, ln=1)

    pdf_ordem.ln(4)

    # ----------------------------------------- Dados interno ----------------------------------------------------------
    pdf_ordem.titulo_secao('Dados interno', 5, 0)
    pdf_ordem.ln(2)

    pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Atendente: ') + 2, 8, 'Atendente:')
    atendente = ordem_de_servico.vendedor.usuario.get_full_name()
    pdf_ordem.cell(pdf_ordem.get_string_width(atendente) + 10, 8, atendente)

    pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Coordenador do grupo: ') + 3, 8, 'Coordenador do grupo:')
    monitor_responsavel = ordem_de_servico.monitor_responsavel.usuario.get_full_name()
    pdf_ordem.cell(pdf_ordem.get_string_width(monitor_responsavel), 8, monitor_responsavel, ln=1)

    pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Seguro: ') + 1, 8, 'Seguro:')

    if ficha_de_evento.informacoes_adcionais.seguro:
        pdf_ordem.cell(20, 8, 'Sim')
    else:
        pdf_ordem.cell(20, 8, 'Não')

    pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Monitoria: ') + 3, 8, 'Monitoria:')

    if ficha_de_evento.informacoes_adcionais.monitoria == 1:
        w_text = pdf_ordem.get_string_width('Meia monitoria fora de quarto (1/20)') + 8
        pdf_ordem.cell(w_text, 8, 'Meia monitoria fora de quarto (1/20)')
    elif ficha_de_evento.informacoes_adcionais.monitoria == 2:
        w_text = pdf_ordem.get_string_width('Meia monitoria dentro de quarto (1/20)') + 8
        pdf_ordem.cell(w_text, 8, 'Meia monitoria dentro de quarto (1/20)')
    else:
        w_text = pdf_ordem.get_string_width('Monitoria completa (1/20)') + 5
        pdf_ordem.cell(w_text, 8, 'Monitoria completa (1/20)')

    pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Enfermagem: ') + 2, 8, 'Enfermagem:')

    if ficha_de_evento.informacoes_adcionais.enfermaria == 1:
        pdf_ordem.cell(0, 8, 'Sem enfermeira', ln=1)
    elif ficha_de_evento.informacoes_adcionais.enfermaria == 1:
        pdf_ordem.cell(0, 8, 'Das 08h às 22h', ln=1)
    else:
        pdf_ordem.cell(0, 8, 'Das 08h às 08h (24h)', ln=1)

    pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Cantina: ') + 2, 8, 'Cantina:')

    if ficha_de_evento.informacoes_adcionais.cantina == 1:
        pdf_ordem.cell(20, 8, 'Não')
    else:
        pdf_ordem.cell(20, 8, 'Sim')

    pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Roupa de cama: ') + 2, 8, 'Roupa de cama:')

    if ficha_de_evento.informacoes_adcionais.roupa_de_cama == 1:
        pdf_ordem.cell(20, 8, 'Não', ln=1)
    else:
        pdf_ordem.cell(20, 8, 'Sim', ln=1)

    if len(ficha_de_evento.informacoes_adcionais.opcionais_geral.all()) > 0:
        opcionais = []
        pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Opcionais gerais: ') + 3, 8, 'Opcionais gerais:')

        for opcional in ficha_de_evento.informacoes_adcionais.opcionais_geral.all():
            opcionais.append(opcional.opcional_geral)

        pdf_ordem.multi_cell(100, 8, ', '.join(opcionais), ln=1)

    if len(ficha_de_evento.informacoes_adcionais.opcionais_formatura.all()) > 0:
        opcionais_formatura = []
        pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Opcioanais formatura: ') + 3, 8, 'Opcionais formatura:')

        for opcional in ficha_de_evento.informacoes_adcionais.opcionais_formatura.all():
            opcionais_formatura.append(opcional)

        pdf_ordem.multi_cell(100, 8, ', '.join(opcionais_formatura), ln=1)

    pdf_ordem.ln(4)
    # ------------------------------------------- Dados de transporte --------------------------------------------------
    if ficha_de_evento.informacoes_adcionais.transporte and ficha_de_evento.informacoes_adcionais.transporte_fechado_internamente == 1:
        pdf_ordem.titulo_secao('Dados do transporte', 5, 0)
        pdf_ordem.ln(2)

        pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Viação: ') + 1, 8, 'Viação:')
        pdf_ordem.cell(100, 8, ordem_de_servico.dados_transporte.empresa_onibus.viacao)

        pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Motorista: ') + 2, 8, 'Motorista:')
        pdf_ordem.cell(0, 8, ordem_de_servico.dados_transporte.nome_motorista, ln=1)

        pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Endereço embarque: ') + 3, 8, 'Endereço embarque:')
        w_text = pdf_ordem.get_string_width(ordem_de_servico.dados_transporte.endereco_embarque) + 10
        pdf_ordem.cell(w_text, 8, ordem_de_servico.dados_transporte.endereco_embarque)

        pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Hora: ') + 1, 8, 'Hora:')
        pdf_ordem.cell(0, 8, ordem_de_servico.dados_transporte.horario_embarque.strftime('%H:%M'), ln=1)

        pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Telefone motorista: ') + 2, 8, 'Telefone motorista:')
        pdf_ordem.cell(40, 8, ordem_de_servico.dados_transporte.telefone_motorista)

        pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Monitor embarque: ') + 3, 8, 'Monitor embarque:')
        pdf_ordem.cell(0, 8, ordem_de_servico.monitor_embarque.usuario.get_full_name(), ln=1)

        pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Micro ônibus: ') + 2, 8, 'Micro ônibus:')
        pdf_ordem.cell(20, 8, str(ordem_de_servico.dados_transporte.dados_veiculos['micro_onibus']))

        pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Ônibus 46 lugares: ') + 2, 8, 'Ônibus 46 lugares:')
        pdf_ordem.cell(20, 8, str(ordem_de_servico.dados_transporte.dados_veiculos['onibus_46']))

        pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Ônibus 50 lugares: ') + 2, 8, 'Ônibus 50 lugares:')
        pdf_ordem.cell(20, 8, str(ordem_de_servico.dados_transporte.dados_veiculos['onibus_50']), ln=1)

        pdf_ordem.ln(4)
    # ----------------------------------------------- Quantidades ------------------------------------------------------
    pdf_ordem.titulo_secao('Quantidades', 5, 0)
    pdf_ordem.ln(2)

    if not ficha_de_evento.produto_corporativo:
        pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Número de alunos: ') + 3, 8, 'Número de alunos:')
        pdf_ordem.cell(15, 8, str(ordem_de_servico.n_participantes))

        pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Número de meninos: ') + 3, 8, 'Número de meninos:')
        pdf_ordem.cell(15, 8, str(ficha_de_evento.qtd_meninos))

        pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Número de meninas: ') + 3, 8, 'Número de meninas:')
        pdf_ordem.cell(15, 8, str(ficha_de_evento.qtd_meninas), ln=1)

        pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Número de professores: ') + 3, 8, 'Número de professores:')
        pdf_ordem.cell(15, 8, str(ordem_de_servico.n_professores))

        pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Número de homens: ') + 2, 8, 'Número de homens:')
        pdf_ordem.cell(15, 8, str(ficha_de_evento.qtd_profs_homens))

        pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Número de mulheres: ') + 2, 8, 'Número de mulheres:')
        pdf_ordem.cell(15, 8, str(ficha_de_evento.qtd_profs_mulheres), ln=1)
    else:
        pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Número de participantes: ') + 3, 8, 'Número de participantes:')
        pdf_ordem.cell(15, 8, str(ordem_de_servico.n_participantes))

        pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Número de homens: ') + 2, 8, 'Número de homens:')
        pdf_ordem.cell(15, 8, str(ficha_de_evento.qtd_homens))

        pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Número de mulheres: ') + 2, 8, 'Número de mulheres:')
        pdf_ordem.cell(15, 8, str(ficha_de_evento.qtd_mulheres), ln=1)

    pdf_ordem.ln(4)
    # --------------------------------------------- Refeições ----------------------------------------------------------
    pdf_ordem.titulo_secao('Refeições', 5, 0)
    pdf_ordem.ln(2)
    pdf_ordem.cell(0, 8, 'As refeições conratados pelo grupo foram as seguintes:', ln=1)
    pdf_ordem.ln(2)

    for refeicao in ficha_de_evento.juntar_refeicoes():
        data = datetime.strptime(refeicao['dia'], '%Y-%m-%d').strftime('%d/%m/%Y')
        pdf_ordem.cell(5, 8, '')
        pdf_ordem.texto_negrito(pdf_ordem.get_string_width(f'{data}: ') + 1, 8, f'{data}:')
        pdf_ordem.cell(0, 8, refeicao['refeicoes'], ln=1)

    if ficha_de_evento.observacoes_refeicoes:
        pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Observações: ') + 1, 8, 'Observações:')
        w = 195 - pdf_ordem.get_string_width('Observações: ') + 1
        pdf_ordem.multi_cell(w, 8, ficha_de_evento.observacoes_refeicoes, ln=1)

    pdf_ordem.ln(4)
    # ---------------------------------------- Atividades acampamento --------------------------------------------------
    if len(ordem_de_servico.atividades_peraltas.all()) > 0:
        pdf_ordem.titulo_secao('Atividades acampamento', 5, 0)
        pdf_ordem.ln(2)

        pdf_ordem.texto_negrito(pdf_ordem.get_string_width('Atividades Peraltas: ') + 3, 8, 'Atividades Peraltas:')
        w = pdf_ordem.get_string_width('Atividades Peraltas: ') + 3
        lista_de_atividades = [atividade.nome_atividade for atividade in ordem_de_servico.atividades_peraltas.all()]
        pdf_ordem.multi_cell(195 - w, 8, ', '.join(lista_de_atividades))

        pdf_ordem.ln(4)
    # ---------------------------------------------- Atividades extra --------------------------------------------------
    if ordem_de_servico.atividades_eco:
        pdf_ordem.titulo_secao('Atividades extra', 5, 0)
        pdf_ordem.ln(2)
        dados = []

        for atividade in ordem_de_servico.atividades_eco.values():
            nome_atividade = AtividadesEco.objects.get(pk=atividade['atividade'])
            data = datetime.strptime(atividade['data_e_hora'], '%Y-%m-%d %H:%M').strftime('%d/%m/%Y %H:%M')

            dado = [
                nome_atividade.nome_atividade_eco,
                data,
                atividade['serie'],
                atividade['biologo'].capitalize(),
                str(atividade['participantes'])
            ]

            dados.append(dado)

        pdf_ordem.tables(
            ['Atividade', 'Data e hora', 'Serie', 'Biologo', 'QTD'],
            dados,
            ['L', 'C', 'L', 'C', 'C'],
            col_widths=(75, 35, 56, 15, 15)
        )
        pdf_ordem.ln(4)
    # --------------------------------------------- Atividades CEU -----------------------------------------------------
    if ordem_de_servico.atividades_ceu:
        pdf_ordem.titulo_secao('Atividades CEU', 5, 0)
        pdf_ordem.ln(2)
        dados = []

        for atividade in ordem_de_servico.atividades_ceu.values():
            nome_atividade = Atividades.objects.get(pk=atividade['atividade'])
            data = datetime.strptime(atividade['data_e_hora'], '%Y-%m-%d %H:%M').strftime('%d/%m/%Y %H:%M')

            dado = [
                nome_atividade.atividade,
                data,
                atividade['serie'],
                str(atividade['participantes'])
            ]

            dados.append(dado)

        pdf_ordem.tables(
            ['Atividade', 'Data e hora', 'Serie', 'QTD'],
            dados,
            ['L', 'C', 'L', 'C'],
            col_widths=(80, 35, 66, 15)
        )
        pdf_ordem.ln(4)
    # ------------------------------------------------- Locacoes CEU ---------------------------------------------------
    if ordem_de_servico.locacao_ceu:
        pdf_ordem.titulo_secao('Locacoes CEU', 5, 0)
        pdf_ordem.ln(2)
        dados = []
        print(ordem_de_servico.locacao_ceu.values())
        for espaco in ordem_de_servico.locacao_ceu.values():
            nome_espaco = Locaveis.objects.get(pk=espaco['espaco'])
            check_in = datetime.strptime(espaco['check_in'], '%Y-%m-%d %H:%M').strftime('%d/%m/%Y %H:%M')
            check_out = datetime.strptime(espaco['check_out'], '%Y-%m-%d %H:%M').strftime('%d/%m/%Y %H:%M')

            dado = [
                nome_espaco.local.__str__(),
                check_in,
                check_out,
                espaco['local_coffee'],
                espaco['hora_coffee'],
                str(espaco['participantes'])
            ]

            dados.append(dado)

        pdf_ordem.tables(
            ['Espaco', 'Check in', 'Check out', 'Local coffee', 'Hora', 'QTD'],
            dados,
            ['L', 'C', 'C', 'L', 'C', 'C'],
            col_widths=(25, 35, 35, 70, 16, 15)
        )
        pdf_ordem.ln(4)

    if ordem_de_servico.observacoes != '':
        pdf_ordem.titulo_secao('Observações', 5, 0)
        pdf_ordem.ln(2)
        pdf_ordem.multi_cell(195, 8, ordem_de_servico.observacoes)

    pdf_ordem.output('temp/ordem_de_servico.pdf')
