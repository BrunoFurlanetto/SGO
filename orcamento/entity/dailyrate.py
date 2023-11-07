from .basevalue import BaseValue
from ..models import HorariosPadroes, OrcamentoDiaria, OrcamentoPeriodo
from datetime import datetime, time


class DailyRate(BaseValue):
    def __init__(self, check_in_id, check_out_id, periods, days):
        super().__init__([])
        print(check_in_id)
        self.check_in_id = check_in_id
        self.check_out_id = check_out_id
        self.periods = periods
        self.days = int(days)

    def calc_daily_rate(self):
        check_in = float(HorariosPadroes.objects.get(pk=self.check_in_id).racional)
        check_out = float(HorariosPadroes.objects.get(pk=self.check_out_id).racional)
        values = []
        value_period_check_in = float(self.periods[0].valor)
        value_period_check_out = float((self.periods[len(self.periods) - 1]).valor)
        values.append(check_in * value_period_check_in)
        for i in range(1, (len(self.periods) - 1)):
            value_period = float((self.periods[i]).valor)
            values.append(value_period)
        values.append(check_out * value_period_check_out)

        self.set_values(values)
        return self.values
