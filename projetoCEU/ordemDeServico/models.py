from django.db import models


class OdemDeServico(models.Model):
    instituicao = models.CharField(max_length=300)
    check_in = models.DateTimeField()
    check_out = models.DateTimeField()
    responsavel_grupo = models.CharField(max_length=255)
