from ..models import ValoresTransporte
from .interface.transport_protocol import TransportProtocol

class TransportGoAndBack(TransportProtocol):
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
            value = (
                float(obj_transport.leva_e_busca) 
                / (1 - float(obj_transport.percentual))
                ) / self.min_payers
            
            values.append(value)
            for i in range(1, self.days):
                values.append(0)
        finally:
            self.values = values

            return self.values