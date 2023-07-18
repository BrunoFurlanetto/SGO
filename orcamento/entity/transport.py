from .base_value import Base_Value
from ..models import ValoresTransporte


class Transport(Base_Value):
    def __init__(self, value, period_id, days):
        super().__init__(value)
        self.period_id = period_id
        self.days = days
        self.min_payers = 30

    def set_min_payers(self, min_payers):
        self.min_payers = min_payers
        return self.min_payers

    def calc_value_trasport(self, is_transport):
        if is_transport == 'nao':
            self.value = 0
            return self.value

        obj_transport = ValoresTransporte.objects.get(
            periodo__pk=self.period_id)
        if not obj_transport:
            self.value = 0
            return self.value

        if self.days == 1:
            self.value = (obj_transport.valor_1_dia /
                          (1 - obj_transport.percentual)) / self.min_payers
            return self.value

        if self.days == 2:
            self.value = (obj_transport.valor_2_dia /
                          (1 - obj_transport.percentual)) / self.min_payers
            return self.value

        self.value = ((obj_transport.valor_3_dia / (1 - obj_transport.percentual)
                       ) + ((self.days - 3) * (obj_transport.valor_acrescimo / (1 - obj_transport.percentual)))) / self.min_payers
        return self.value
