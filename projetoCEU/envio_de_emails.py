from datetime import timedelta
from django.core.mail import send_mail

try:
    from local_settings import *
except ImportError:
    ...


class EmailSender:
    def __init__(self, lista_destinatario):
        self.subject = None
        self.from_email = EMAIL_HOST_USER
        self.recipient_list = lista_destinatario

    def enviar_email(self, mensagem):
        send_mail(
            self.subject,
            '',
            self.from_email,
            self.recipient_list,
            fail_silently=False,
            html_message=mensagem,
        )

    def mensagem_pre_escala_monitoria(self, check_in, check_out, cliente):
        check_in_monitor = check_in - timedelta(hours=3)
        self.subject = 'Confirmação da pré escala monitoria'

        mensagem = f'''
            <html>
                <body>
                    <p>
                        <strong>"Este e-mail confirma sua Pré participação no evento acampamento pedagógico XXXX para
                        prestar serviços de monitoria no Acampamento Peraltas, no período de 
                        {check_in.strftime('%d/%m/%Y')} a {check_out.strftime('%d/%m/%Y')} com o cliente {cliente},
                        devendo estar presente às {check_in_monitor.strftime('%H')} horas do dia {check_in.day} para
                        assumir a função de monitor/recreador."</strong> A inserção do seu nome no cadastro de
                        PRÉ-ESCALA NÃO significa que você está escalado para esse evento.                        
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
                    <p>
                        Este e-mail é um automático, e não deve ser respondido.                       
                        <br>
                        Sistema de Gerenciamento Operacional (SGO).
                        <br>
                        Equipe Grupo Peraltas.
                    </p>
                </body>
            </html>
        '''

        self.enviar_email(mensagem)

    def mensagem_cadastro_ficha_monitoria(self, check_in, check_out, cliente, nome_colaboradora):
        self.subject = 'Confirmação do preenchimento da ficha evento pelo Comercial'

        mensagem = f'''
            <html>
                <body>
                    <p>
                        {nome_colaboradora}, efetuou o cadastro da ficha de evento referente ao evento de {cliente}, na
                        data {check_in.strftime('%d/%m/%Y')} a {check_out.strftime('%d/%m/%Y')}. Já está liberado o
                        preenchimento da pré-escala dos monitores que irão participar desse evento. Favor fazer o mais
                        rápido possível. 
                    </p>
                    <p>
                        Este e-mail é um automático, e não deve ser respondido.                       
                        <br>
                        Sistema de Gerenciamento Operacional (SGO).
                        <br>
                        Equipe Grupo Peraltas.
                    </p>
                </body>
            </html>
        '''

        self.enviar_email(mensagem)

    def mensagem_cadastro_ficha_operacional(self, check_in, check_out, cliente, nome_colaboradora):
        self.subject = 'Confirmação do preenchimento da ficha evento pelo Comercial'

        mensagem = f'''
            <html>
                <body>
                    <p>
                        {nome_colaboradora}, efetuou o cadastro da ficha de evento referente ao evento de {cliente}, na
                        data {check_in.strftime('%d/%m/%Y')} a {check_out.strftime('%d/%m/%Y')}. Já está liberado o
                        preenchimento da ordem de serviço e pré-escala dos monitores que irão participar desse evento.
                        Favor fazer o mais rápido possível.
                    </p>
                    <p>
                        Este e-mail é um automático, e não deve ser respondido.                       
                        <br>
                        Sistema de Gerenciamento Operacional (SGO).
                        <br>
                        Equipe Grupo Peraltas.
                    </p>
                </body>
            </html>
        '''

        self.enviar_email(mensagem)

    def mensagem_cadastro_escala(self, check_in, check_out, cliente):
        self.subject = f'Confirmação da escala do evento de {cliente}'
        check_in_monitor = check_in - timedelta(hours=3)

        mensagem = f'''
            <html>
                <body>
                    <p>
                        Este e-mail confirma sua participação no evento acampamento pedagógico XXXX para prestar
                        serviços de monitoria no Acampamento Peraltas, no período de {check_in.strftime('%d/%m/%Y')}
                        à {check_out.strftime('%d/%m/%Y')} de {cliente}, devendo estar presente às
                        {check_in_monitor.strftime('%H')} horas do dia {check_in.day} para assumir a função de
                        monitor/recreador.
                    </p>
                    <p>
                        Este e-mail é um automático, e não deve ser respondido.                       
                        <br>
                        Sistema de Gerenciamento Operacional (SGO).
                        <br>
                        Equipe Grupo Peraltas.
                    </p>
                </body>
            </html>
        '''

        self.enviar_email(mensagem)

    def mensagem_cadastro_escala_operacional(self, check_in, check_out, cliente):
        self.subject = f'Confirmação da escala do evento de {cliente}'
        check_in_monitor = check_in - timedelta(hours=3)

        mensagem = f'''
            <html>
                <body>
                    <p>
                        A escala do evento de {cliente}, da data {check_in.strftime('%d/%m/%Y')} a
                        {check_out.strftime('%d/%m/%Y')} foi confirmada pela direção. Segue abaixo o nome e função dos
                        monitores escalados. 
                        Nome 1 / Função
                        Nome 2/ função
                    </p>
                    <p>
                        Este e-mail é um automático, e não deve ser respondido.                       
                        <br>
                        Sistema de Gerenciamento Operacional (SGO).
                        <br>
                        Equipe Grupo Peraltas.
                    </p>
                </body>
            </html>
        '''

        self.enviar_email(mensagem)

    def mensagem_cadastro_ordem(self, check_in, check_out, cliente):
        self.subject = f'Ordem de serviço cadastrada'

        mensagem = f'''
            <html>
                <body>
                    <p>
                        O operacional efetuou a ordem de serviço do evento de {cliente}, da data
                        {check_in.strftime('%d/%m/%Y')} à {check_out.strftime('%d/%m/%Y')}. Favor entrar na mesma e
                        confirmar as informações.
                    </p>
                    <p>
                        Este e-mail é um automático, e não deve ser respondido.                       
                        <br>
                        Sistema de Gerenciamento Operacional (SGO).
                        <br>
                        Equipe Grupo Peraltas.
                    </p>
                </body>
            </html>
        '''

        self.enviar_email(mensagem)

    def mensagem_confirmacao_evento(self, check_in, check_out, cliente, nome_colaboradora):
        self.subject = f'Confirmação de evento'

        mensagem = f'''
            <html>
                <body>
                    <p>
                        {nome_colaboradora}, confirmou a pré-reserva referente ao evento de {cliente}, da data
                        {check_in.strftime('%d/%m/%Y')} à {check_out.strftime('%d/%m/%Y')}.
                    </p>
                    <p>
                        Este e-mail é um automático, e não deve ser respondido.                       
                        <br>
                        Sistema de Gerenciamento Operacional (SGO).
                        <br>
                        Equipe Grupo Peraltas.
                    </p>
                </body>
            </html>
        '''

        self.enviar_email(mensagem)
