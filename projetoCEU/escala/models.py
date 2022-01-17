from django.db import models
from cadastro.models import Professores


class Escala(models.Model):
    coordenador = models.ForeignKey(Professores, on_delete=models.DO_NOTHING, related_name='coordenador_escala')
    professor_2 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING,
                                    related_name='professor_2_escala', blank=True, null=True)
    professor_3 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING,
                                    related_name='professor_3_escala', blank=True, null=True)
    professor_4 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING,
                                    related_name='professor_4_escala', blank=True, null=True)
    professor_5 = models.ForeignKey(Professores, on_delete=models.DO_NOTHING,
                                    related_name='professor_5_escala', blank=True, null=True)
    data = models.DateField()
