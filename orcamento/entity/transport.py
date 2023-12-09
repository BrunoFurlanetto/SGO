from .basevalue import BaseValue
from ..models import ValoresTransporte


class Transport(BaseValue):
    def __init__(self, values, periods, days):
        super().__init__(values)
        self.periods = periods
        self.days = days
        self.min_payers = 30

    def set_min_payers(self, min_payers):
        self.min_payers = min_payers
        return self.min_payers

    def calc_value_transport(self, is_transport):
        values = []

        if is_transport != 'sim':
            for day in range(0, self.days):
                values.append(0.0)

            self.values = values

            return self.values

        try:
            obj_transport = ValoresTransporte.objects.get(periodo__pk=self.periods[0].id)
        except ValoresTransporte.DoesNotExist:
            self.values = []

            return self.values
        else:
            if self.days == 1:
                value = (float(obj_transport.valor_1_dia) /
                         (1 - float(obj_transport.percentual))) / self.min_payers
            elif self.days == 2:
                value = (float(obj_transport.valor_2_dia) /
                         (1 - float(obj_transport.percentual))) / self.min_payers
            else:
                value = ((float(obj_transport.valor_3_dia) / (1 - float(obj_transport.percentual))
                          ) + ((self.days - 3) *
                               (float(obj_transport.valor_acrescimo) / (
                                       1 - float(obj_transport.percentual))))) / self.min_payers

            values.append(value)

            for i in range(1, self.days):
                values.append(0)
        finally:
            self.values = values

            return self.values
