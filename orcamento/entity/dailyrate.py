from .basevalue import BaseValue
from ..models import HorariosPadroes, OrcamentoDiaria
from datetime import datetime, time


class DailyRate(BaseValue):
    def __init__(self, check_in_id, check_out_id, period_id, days):
        super().__init__(0)
        print(check_in_id)
        self.check_in_id = check_in_id
        self.check_out_id = check_out_id
        self.period_id = period_id
        self.days = int(days)

    def calc_daily_rate(self):
        check_in = HorariosPadroes.objects.get(pk=self.check_in_id).horario
        check_out = HorariosPadroes.objects.get(pk=self.check_out_id).horario
        first_daily_rate = 1
        intermediate_daily_rate = self.days - 2
        last_daily_rate = 1

        try:
            daily_rate_value = float(OrcamentoDiaria.objects.get(periodo__id=self.period_id).valor)
        except OrcamentoDiaria.DoesNotExist:
            self.value = 0
            return self.value

        if check_in.hour > time(12, 0, 0).hour:
            first_daily_rate = 0.5
        if check_in.hour > time(12, 0, 0).hour:
            first_daily_rate = 0.2

        if intermediate_daily_rate < 0:
            intermediate_daily_rate = 0

        if check_out.hour < time(12, 0, 0).hour:
            last_daily_rate = 0.2
        if check_out.hour > time(12, 0, 0).hour:
            last_daily_rate = 1.2

        self.value = daily_rate_value * (first_daily_rate + intermediate_daily_rate + last_daily_rate)

        return self.value
