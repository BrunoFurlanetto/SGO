from .base_value import Base_Value
from ..models import HorariosPadroes, OrcamentoDiaria
from datetime import datetime


class Daily_Rate(Base_Value):
    def __init__(self, check_in_id, check_out_id, period_id, days):
        super().__init__(self.calc_daily_rate())
        self.check_in_id = check_in_id
        self.check_out_id = check_out_id
        self.period_id = period_id
        self.days = days

    def calc_daily_rate(self):
        check_in = HorariosPadroes.objects.get(pk=self.check_in_id).horario
        check_out = HorariosPadroes.objects.get(pk=self.check_out_id).horario
        daily_rate_value = OrcamentoDiaria.objects.get(
            periodo__pk=self.period_id).valor
        if not daily_rate_value:
            self.value = 0
            return self.value

        first_daily_rate = 1
        if check_in.hour > datetime(year=2023, hour=12).hour:
            first_daily_rate = 0.5
        if check_in.hour > datetime(year=2023, hour=18).hour:
            first_daily_rate = 0.2

        intermediate_daily_rate = self.days - 2
        if intermediate_daily_rate < 0:
            intermediate_daily_rate = 0

        last_daily_rate = 1
        if check_out.hour < datetime(year=2023, hour=12).hour:
            last_daily_rate = 0.2
        if check_out.hour > datetime(year=2023, hour=15).hour:
            last_daily_rate = 1.2

        self.value = daily_rate_value * \
            (first_daily_rate + intermediate_daily_rate + last_daily_rate)
        return self.value
