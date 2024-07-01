from ..models import ValoresTransporte
from .interface.transport_protocol import TransportProtocol


class TransportGoAndBack(TransportProtocol):
    def __init__(self, values, checkin, days, percent_business_fee, percent_commission):
        super().__init__(values, checkin, days, percent_business_fee, percent_commission)

    def calc_value_transport(self, is_transport):
        values = []
        if is_transport != 'sim':
            for day in range(0, self.days):
                values.append(0.0)

            self.values = values

            return self.values

        try:
            obj_transport = ValoresTransporte.objects.get(
                inicio_validade__lte=self.checkin,
                final_validade__gte=self.checkin,
            )
        except ValoresTransporte.DoesNotExist:
            values = []
        else:
            value = (float(obj_transport.leva_e_busca)
                     / (1 - float(obj_transport.percentual))
                     ) / self.min_payers

            values.append(value)
            for i in range(1, self.days):
                values.append(0)
        finally:
            self.values = values

            return self.values
