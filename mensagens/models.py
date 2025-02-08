from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.timezone import now

from orcamento.models import Orcamento


class Mensagem(models.Model):
    remetente = models.ForeignKey(User, models.SET_NULL, blank=True, null=True, related_name='remetente')
    destinatario = models.ForeignKey(User, models.SET_NULL, blank=True, null=True, related_name='destinatario')
    nome_remetente = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Salva o nome do remetente no caso do usuário ser excluido'
    )
    nome_destinatario = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Salva o nome do destinatário no caso do usuário ser excluido',
    )
    conteudo = models.TextField()
    anexo = models.FileField(upload_to='mensagens/arquivos/', blank=True, null=True)
    data_hora_envio = models.DateTimeField(auto_now_add=True)
    data_hora_leitura = models.DateTimeField(blank=True, null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f'Mensagem entre {self.remetente} e {self.destinatario} relacionado ao {self.content_type.model}'

    def save(self, *args, **kwargs):
        if not self.nome_remetente and self.remetente:
            self.nome_remetente = self.remetente.get_full_name() or self.remetente.username

        if not self.nome_destinatario and self.destinatario:
            self.nome_destinatario = self.destinatario.get_full_name() or self.destinatario.username

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.anexo:
            self.anexo.delete()

        super().delete(*args, **kwargs)

    def get_responsavel(self, usuario):
        return 'remetente' if usuario == self.remetente else 'destinatario'
