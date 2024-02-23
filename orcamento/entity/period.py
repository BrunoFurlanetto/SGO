from .basevalue import BaseValue


class Period(BaseValue):
    def __init__(self, periods):
        self.periods = periods
        values = [float(0) for period in periods]
        super().__init__(values=values)

    def calc_business_fee(self, percent):
        return 0

    def calc_commission(self, percent):
        return 0

    def get_periods(self):
        return [period.id_periodo for period in self.periods]

    def set_period_rate(self):
        taxa = 0

        for period in self.periods:
            if period.taxa_periodo >= taxa:
                taxa = period.taxa_periodo

        self.values[0] = float(taxa)

        return self.values
