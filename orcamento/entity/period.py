from .basevalue import BaseValue


class Period(BaseValue):
    def __init__(self, periods):
        self.periods = periods
        values = [float(period.valor) for period in periods]
        super().__init__(values=values)

    def get_periods(self):
        return [period.id for period in self.periods]