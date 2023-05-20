from django.shortcuts import render

from django.shortcuts import render
from django_cron.models import CronJobLog


def cron_job_logs(request):
    logs = CronJobLog.objects.all()
    return render(request, 'peraltas/cron_job_logs.html', {'logs': logs})
