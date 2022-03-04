from django.db import models


class Monitor(models.Model):
    nome = models.CharField(max_length=255)
