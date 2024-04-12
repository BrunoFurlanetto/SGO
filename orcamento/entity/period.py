from .basevalue import BaseValue
from ..models import TaxaPeriodo


class Period(BaseValue):
    def __init__(self, periods):
        self.periods = periods
        values = [float(0) for period in periods]
        super().__init__(values=values)

    def get_periods(self):
        return [period.id_periodo for period in self.periods]

    def set_period_rate(self):
        taxa = 0

        for period in self.periods:  # TODO: Revisar aqui pra ver como vai ser feito essa separação da taxa Maria Pia
            if TaxaPeriodo.objects.get(id=1).valor >= taxa:
                taxa = TaxaPeriodo.objects.get(id=1).valor

        self.values[0] = float(taxa)

        return self.values
