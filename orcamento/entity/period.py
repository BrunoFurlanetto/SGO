from .basevalue import BaseValue
from ..models import TaxaPeriodo
from ..utils import JsonError


class Period(BaseValue):
    def __init__(self, days, percent_business_fee, percent_commission):
        self.date_to_check = days[0]
        values = [float(0) for day in days]
        super().__init__(values, percent_business_fee, percent_commission)

    def set_period_rate(self):
        taxa = 0

        try:
            taxa_periodo = TaxaPeriodo.objects.get(
                inicio_vigencia__lte=self.date_to_check, 
                final_vigencia__gte=self.date_to_check,
            )
        except TaxaPeriodo.DoesNotExist:
            self.values = None
        else:
            self.classification_code = taxa_periodo.classificacao.codigo_padrao
            taxa = taxa_periodo.valor
            self.values[0] = float(taxa)

        return self.values
 