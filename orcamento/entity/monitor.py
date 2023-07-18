
from .basevalue import BaseValue
from ..models import OrcamentoMonitor, HorariosPadroes
from datetime import datetime
import math


class Monitor(BaseValue):
    def __init__(self, value, days, coming_id, exit_id):
        super().__init__(value)
        self.coming_id = coming_id
        self.exit_id = exit_id
        self.days = days

    def calc_value_monitor(self, id):
        object_monitor = OrcamentoMonitor.objects.get(pk=id)
        daily_monitor = math.ceil(
            object_monitor.valor / object_monitor.racional_monitoria)

        check_in = HorariosPadroes.objects.get(pk=self.coming_id).horario
        check_out = HorariosPadroes.objects.get(pk=self.exit_id).horario

        first_daily_monitor = 1
        if check_in.hour > datetime(year=2023, hour=12).hour:
            first_daily_monitor = 0.5

        intermediate_daily_monitor = self.days - 2
        if intermediate_daily_monitor < 0:
            intermediate_daily_monitor = 0

        last_daily_monitor = 1
        if check_out.hour < datetime(year=2023, hour=12).hour:
            last_daily_monitor = 0.5

        self.value = math.ceil(daily_monitor *
                               (first_daily_monitor + intermediate_daily_monitor + last_daily_monitor))

        return self.value
