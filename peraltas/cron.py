from django_cron import CronJobBase, Schedule
from peraltas.models import FichaDeEvento
import requests


class AtualizarDadosCronJob(CronJobBase):
    RUN_AT_TIMES = ['00:00']

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'peraltas.atualizar_dados_cron_job'

    def do(self):
        url = 'https://pagamento.peraltas.com.br/json/turmas.json'

        response = requests.get(url)
        if response.status_code == 200:
            response = response.json()
            ficha = FichaDeEvento.objects.get(id=191)

            ficha.qtd_meninos = response[0]['totais']['totalPagantesMasculino']
            ficha.qtd_meninas = response[0]['totais']['totalPagantesFeminino']
            ficha.qtd_profs_homens = response[0]['totais']['totalProfessoresMasculino']
            ficha.qtd_profs_mulheres = response[0]['totais']['totalProfessoresFeminino']

            ficha.save()
