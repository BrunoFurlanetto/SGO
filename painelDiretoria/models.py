from django.db import models


class Metas(models.Model):
    pax_mon = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        verbose_name='Relação participantes por monitor',
        default=0.00
    )
    min_media_diarias = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Valor mínimo da média de diarias',
        default=0.00
    )
    max_media_diarias = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Valor máximo da média de diarias',
        default=0.00
    )

    def __str__(self):
        return (f'Meta de relação participantes/monitroia: {self.pax_mon:.2f} e de média de diarias: {self.min_media_diarias:.2f}'
                f' - {self.max_media_diarias:.2f}')

    class Meta:
        permissions = (('ver_estatisticas_monitoria', 'Ver estatísticas da monitoria'),)

    @staticmethod
    def acumulado_dias(escalas):
        acumulado_diaria = 0.00
        n_participantes = sum([escala.ficha_de_evento.qtd_convidada for escala in escalas])
        n_monitores = sum([len(escala.monitores_acampamento.all()) for escala in escalas])
        acumulado_relacao = n_participantes / n_monitores

        for escala in escalas:
            for monitor in escala.monitores_acampamento.all():
                if monitor.nivel.coordenacao:
                    acumulado_diaria += float(monitor.valor_diaria_coordenacao)
                else:
                    acumulado_diaria += float(monitor.valor_diaria)

        acumulado_diaria_media = acumulado_diaria / n_monitores

        return acumulado_relacao, acumulado_diaria_media
