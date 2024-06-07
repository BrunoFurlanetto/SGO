from datetime import timedelta
from django.core.mail import send_mail
from django.urls import reverse

from orcamento.models import Orcamento
from ordemDeServico.models import OrdemDeServico
from projetoCEU.settings import MY_APP_DOMAIN

try:
    from local_settings import *
except ImportError:
    ...


class EmailSender:
    def __init__(self, lista_destinatario):
        self._subject = None
        self.__from_email = EMAIL_HOST_USER
        self.recipient_list = lista_destinatario
        self.__assinatura = '''
            <p>
                Este e-mail é um automático, e não deve ser respondido.                       
                <br>
                Sistema de Gerenciamento Operacional (SGO).
                <br>
                Equipe Grupo Peraltas.
            </p>
        '''

    def __enviar_email(self, mensagem):
        send_mail(
            self._subject,
            '',
            self.__from_email,
            self.recipient_list,
            fail_silently=False,
            html_message=mensagem,
        )

    def mensagem_pre_escala_monitoria(self, ficha_de_evento):
        check_in = ficha_de_evento.check_in
        check_out = ficha_de_evento.check_out
        cliente = ficha_de_evento.cliente
        check_in_monitor = check_in.astimezone() - timedelta(hours=1)
        self._subject = 'Confirmação da pré escala monitoria'

        __mensagem = f'''
            <html>
                <body>
                    <p>
                        <strong>"Este e-mail confirma sua Pré participação no evento acampamento pedagógico {cliente}
                        para prestar serviços de monitoria no Acampamento Peraltas, no período de 
                        {check_in.strftime('%d/%m/%Y')} a {check_out.strftime('%d/%m/%Y')} com o cliente {cliente},
                        devendo estar presente às {check_in_monitor.strftime('%H')} horas do dia {check_in.day} para
                        assumir a função de monitor/recreador."</strong> A inserção do seu nome no cadastro de
                        PRÉ-ESCALA NÃO significa que você está escalado para esse evento.                        
                    </p>
                    <p>
                        Aos monitores que irão fazer o embarque do grupo, um email contendo as informações do embarque
                        será enviado posteriormente, caso já tenha o recebido, ignore esta parte.
                    </p>
                    <p>
                        A confirmação da necessidade do serviço ocorrerá após definição de números de participantes pelo
                        Colégio/Contratante, momento em que o sistema enviará uma confirmação para seu email/whatsApp,
                        informando se você foi escalado para o evento.
                    </p>
                    <p>
                        <strong>Observações importantes:</strong> caso você tenha se inscrito para a data mas não possa
                        comparecer, pedimos a gentileza de avisar com até 10 dias de antecedência, para localizarmos
                        outro profissional habilitado, lembrando que Você pode recusar o trabalho quantas vezes quiser,
                        sem necessidade de qualquer justificativa.
                    </p>
                    <p>
                        A data limite para inscrição e confirmação no interesse de prestação de serviços de um evento,
                        poderá ser feita até 10 dias antes do evento, através do cadastro de PRÉ-ESCALA.
                    </p>      
                    {self.__assinatura}              
                </body>
            </html>
        '''

        self.__enviar_email(__mensagem)

    def mensagem_cadastro_ficha(self, check_in, check_out, cliente, nome_colaboradora):
        self._subject = 'Preenchimento da ficha evento pelo Comercial'

        __mensagem = f'''
            <html>
                <body>
                    <p>
                        {nome_colaboradora}, efetuou o cadastro da ficha de evento referente ao evento de {cliente}, na
                        data {check_in.strftime('%d/%m/%Y')} a {check_out.strftime('%d/%m/%Y')}. Já está liberado o
                        preenchimento da ordem de serviço e pré-escala dos monitores que irão participar desse evento.
                        Favor fazer o mais rápido possível.
                    </p>
                    {self.__assinatura}
                </body>
            </html>
        '''

        self.__enviar_email(__mensagem)

    def mensagem_alteracao_ficha(self, colaborador, cliente, ficha):
        self._subject = 'ALTERAÇÃO NO EVENTO'
        nome_colaboradora = colaborador.usuario.get_full_name()
        check_in = ficha.check_in.strftime('%d/%m/%Y')
        check_out = ficha.check_out.strftime('%d/%m/%Y')
        link_ficha = reverse('ver_ficha_de_evento', kwargs={'id_ficha_de_evento': ficha.id})
        link_completo = f'{MY_APP_DOMAIN}{link_ficha}'

        mensagem = f'''
            <html>
                <body>
                    <p>
                        A ficha de evento do(a) colaborador(a) {nome_colaboradora}, referente ao evento de {cliente}, que irá
                        acontecer de {check_in} a {check_out} foi alterado. Por favor verificar as alterações que foram feitas
                        atravéz do link abaixo.                        
                    </p>
                    
                    <p>
                        <a href="{link_completo}">Ficha de evento de {cliente}</a>
                    </p>
                    {self.__assinatura}
                </body>
            </html>
        '''

        self.__enviar_email(mensagem)

    def mensagem_cadastro_escala(self, ficha_de_evento):
        __ordem_servico = OrdemDeServico.objects.get(ficha_de_evento=ficha_de_evento) if ficha_de_evento.os else None
        __cliente = ficha_de_evento.cliente
        __check_in = ficha_de_evento.check_in if not __ordem_servico else __ordem_servico.check_in
        __check_out = ficha_de_evento.check_out if not __ordem_servico else __ordem_servico.check_out
        __check_in_monitor = ficha_de_evento.check_in.astimezone() - timedelta(hours=1)
        self._subject = f'Confirmação da escala do evento de {__cliente}'

        __mensagem = f'''
            <html>
                <body>
                    <p>
                        Este e-mail confirma sua participação no evento acampamento pedagógico {__cliente} para prestar
                        serviços de monitoria no Acampamento Peraltas, no período de {__check_in.strftime('%d/%m/%Y')}
                        à {__check_out.strftime('%d/%m/%Y')}, devendo estar presente às
                        {__check_in_monitor.strftime('%H')} horas do dia {__check_in.day} para assumir a função de
                        monitor/recreador.
                    </p>
                    <p>
                        Aos monitores que irão fazer o embarque do grupo, um email contendo as informações do embarque
                        será enviado posteriormente, caso já o tenha recebido, ignore esta parte.
                    </p>
                    {self.__assinatura}
                </body>
            </html>
        '''

        self.__enviar_email(__mensagem)

    def mensagem_cadastro_escala_operacional(self, ficha_de_evento, escala):
        __ordem_servico = OrdemDeServico.objects.get(ficha_de_evento=ficha_de_evento) if ficha_de_evento.os else None
        __cliente = ficha_de_evento.cliente
        __check_in = ficha_de_evento.check_in if not __ordem_servico else __ordem_servico.check_in
        __check_out = ficha_de_evento.check_out if not __ordem_servico else __ordem_servico.check_out
        self._subject = f'Confirmação da escala do evento de {__cliente}'

        _acamp = len(escala.monitores_acampamento.all()) > 0
        _embarque = len(escala.monitores_embarque.all()) > 0
        _tec = len(escala.tecnicos.all()) > 0
        _biologo = len(escala.biologos.all()) > 0
        _enfermeiras = len(escala.enfermeiras.all()) > 0

        __mensagem = f'''
            <html>
                <body>
                    <p>
                        A escala do evento de {__cliente}, da data {__check_in.strftime('%d/%m/%Y')} a
                        {__check_out.strftime('%d/%m/%Y')} foi confirmada pela direção. Segue abaixo o nome e função dos
                        monitores escalados:
                    </p>
                    {self.__criar_lista_monitores(escala.monitores_acampamento.all(), 'Acampamento') if _acamp else ''}
                    {self.__criar_lista_monitores(escala.monitores_embarque.all(), 'Embarque') if _embarque else ''}
                    {self.__criar_lista_monitores(escala.tecnicos.all(), 'Tecnicos') if _tec else ''}
                    {self.__criar_lista_monitores(escala.biologos.all(), 'Biologos') if _biologo else ''}
                    {self.__criar_lista_monitores(escala.enfermeiras.all(), 'Enfermeiras') if _enfermeiras else ''}
                    {self.__assinatura}
                </body>
            </html>
        '''

        self.__enviar_email(__mensagem)

    def mensagem_cadastro_ordem(self, check_in, check_out, cliente):
        self._subject = f'Ordem de serviço cadastrada'

        __mensagem = f'''
            <html>
                <body>
                    <p>
                        O operacional efetuou a ordem de serviço do evento de {cliente}, da data
                        {check_in.strftime('%d/%m/%Y')} à {check_out.strftime('%d/%m/%Y')}. Favor entrar na mesma e
                        confirmar as informações.
                    </p>
                    {self.__assinatura}
                </body>
            </html>
        '''

        self.__enviar_email(__mensagem)

    def mensagem_monitor_embarque(self, cliente, check_in, monitor_embarque):
        self._subject = 'Monitor de embarque'

        __mensagem = f'''
            <html>
                <body>
                    <p>
                        {monitor_embarque}, você está escalado para fazer o embarque de
                        {cliente}, dia {check_in.strftime('%d/%m/%Y')}. Informações sobre o local e horário de embarque
                        serão encaminhadas 10 dias antes do evento.
                    </p>
                    {self.__assinatura}
                </body>
            </html>
        '''

        self.__enviar_email(__mensagem)

    def mensagem_confirmacao_evento(self, check_in, check_out, cliente, nome_colaboradora):
        self._subject = f'Confirmação de evento'

        __mensagem = f'''
            <html>
                <body>
                    <p>
                        {nome_colaboradora}, confirmou a pré-reserva referente ao evento de {cliente}, da data
                        {check_in.strftime('%d/%m/%Y')} à {check_out.strftime('%d/%m/%Y')}.
                    </p>
                    {self.__assinatura}
                </body>
            </html>
        '''

        self.__enviar_email(__mensagem)

    def dados_embarque(self, os, dados_emarque):
        self._subject = f'Dados do embarque'

        __mensagem = f'''
            <html>
                <body>
                    <p>
                        {dados_emarque.monitor_embarque.usuario.get_full_name()}, você foi escalado(a) para realizar o
                        embarque de {os.ficha_de_evento.cliente} que acontecerá no dia <strong>
                        {os.check_in.strftime('%d/%m/%Y')}</strong>, dessa forma, segue os dados para o embarque:                    
                    </p>
                    <h3>Dados do embarque</h3>
                    <p>                        
                        <strong>Viação responsável pelo transporte</strong>: {dados_emarque.empresa_onibus.viacao}
                        <br>
                        <strong>Endereço de embarque</strong>: {dados_emarque.endereco_embarque}
                        <br>                 
                        <strong>Horário embarque</strong>: {dados_emarque.horario_embarque.strftime('%H:%M')}
                        <br>
                        <strong>Nome do motorista</strong>: {dados_emarque.nome_motorista}
                        <br>                        
                        <strong>Telefone do motorista</strong>: {dados_emarque.telefone_motorista}                     
                    </p>
                    <p>
                        É importe que esteja no local de embarque pelo menos <strong><u>UMA HORA ANTES DO HORÁRIO
                        DESCRITO ACIMA </u></strong>. Em caso de dúvidas, entrar em contato com o operacional.
                    </p>
                    {self.__assinatura}
                </body>
            </html>
        '''

        self.__enviar_email(__mensagem)

    @staticmethod
    def __criar_lista_monitores(lista_monitores, tipo_escalacao):
        __max_colunas = 4
        __max_linhas = len(lista_monitores) // 4
        __max_linhas += 1 if len(lista_monitores) % 4 != 0 else 0

        __tabela_monitores_html = '''
            <style>
                table {{
                    border-collapse: collapse;
                    width: 100%;
                }}

                th, td {{
                    border: 1px solid black;
                    padding: 8px;
                    text-align: left;
                }}
            </style>
            <h2>{}</h2>
            <table>
        '''.format(tipo_escalacao)

        for i in range(__max_linhas):
            __tabela_monitores_html += '<tr>'

            for j in range(min(__max_colunas, len(lista_monitores))):
                valor = lista_monitores[i*__max_colunas + j] if i*__max_colunas + j < len(lista_monitores) else ''
                __tabela_monitores_html += f'<td>{valor}</td>'

            __tabela_monitores_html += '</tr>'

        __tabela_monitores_html += '</table>'

        return __tabela_monitores_html

    def orcamento_aprovado(self, id_orcamento, aprovado_por):
        self._subject = 'ORÇAMENTO APROVADO PELA DIRETORIA'
        orcamento = Orcamento.objects.get(pk=id_orcamento)

        __mensagem = f'''
            <html>
                <body>
                    <p>
                        Orçamento de {orcamento.cliente} foi aprovado por {aprovado_por}, por favor enviar ao cliente o 
                        quanto antes. Lembrando que a data de vencimento do orçamento em questão é 
                        {orcamento.data_vencimento.strftime('%d/%m/%Y')}.
                    </p>
                    {self.__assinatura}
                </body>
            </html>
        '''
        self.__enviar_email(__mensagem)

    def orcamento_aprovacao(self, id_orcamento):
        orcamento = Orcamento.objects.get(pk=id_orcamento)
        self._subject = 'ORÇAMENTO PARA APROVAÇÃO'

        __mensagem = f'''
            <html>
                <body>
                    <p>
                       O colaborador {orcamento.colaborador.get_full_name()}, adicionou um orçamento 
                       para {orcamento.cliente} que necessita de aprovação da diretoria. Vá até po seu dashboard
                       para que aprove os pedidos.                           
                    </p>
                    <p>
                       Lembrando que o orçamento em questão tem a data de vencimento em {orcamento.data_vencimento.strftime('%d/%m/%Y')} 
                    </p>
                    {self.__assinatura}
                </body>
            </html>
        '''
        self.__enviar_email(__mensagem)

    def evento_cancelado_monitores(self, cliente, check_in):
        self._subject = 'EVENTO CANCELADO'

        __mensagem = f'''
            <html>
                <body>
                    <p>
                       O evento de {cliente} que aconteceria no dia {check_in.strftime('%d/%m/%Y')},
                       no qual montou a escala, foi cancelado.                            
                    </p>
                    {self.__assinatura}
                </body>
            </html>
        '''
        self.__enviar_email(__mensagem)
