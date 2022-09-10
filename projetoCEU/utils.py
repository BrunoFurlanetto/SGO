import datetime
import email.message
import smtplib
from email.message import EmailMessage
from datetime import datetime


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def verificar_grupo(grupos_usuario):
    grupos = []

    for grupo in grupos_usuario:
        grupos.append(grupo.name)

    return grupos


def email_error(usuario, erro, view):
    corpo_email = f'O usuário {usuario}, acabou por estourar a exceção "{erro}", na página {view} as {datetime.now()}'

    msg = EmailMessage()
    msg['Subject'] = f"EXCEPTION ({erro})"
    msg['From'] = 'error.alpha.teste@gmail.com'
    msg['To'] = 'bruno.furlanetto@hotmail.com'
    password = 'ofdsqhqzyfctqkem'
    msg.set_content(corpo_email)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(msg['From'], password)
        smtp.send_message(msg)


