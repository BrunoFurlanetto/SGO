from .interface.transport_protocol import TransportProtocol
from ..models import ValoresTransporte
from .transport_go_and_back import TransportGoAndBack


class Transport(TransportProtocol):
    def __init__(self, values, checkin, days):
        super().__init__(values, checkin, days)
        self.tranport_go_and_back = TransportGoAndBack(values, checkin, days)

    def set_min_payers(self, min_payers):
        self.min_payers = min_payers
        self.tranport_go_and_back.set_min_payers(min_payers);
        return self.min_payers

    def calc_value_transport(self, is_transport):

        self.tranport_go_and_back.calc_value_transport(is_transport)
        values = []

        if is_transport != 'sim':
            for day in range(0, self.days):
                values.append(0.0)

            self.values = values

            return self.values
        
        
        try:
            #TODO: GET ta dando erro aqui, pois retorna mais de um valor de onibus
            obj_transport = ValoresTransporte.objects.filter(validade__gte=self.checkin)
            obj_transport = obj_transport.first()
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
            elif self.days == 3:
                value = (float(obj_transport.valor_3_dia) /
                        (1 - float(obj_transport.percentual))) / self.min_payers
            elif self.days == 4:
                value = (float(obj_transport.valor_4_dia) /
                        (1 - float(obj_transport.percentual))) / self.min_payers
            else:
                value = ((float(obj_transport.valor_5_dia) / (1 - float(obj_transport.percentual))
                          ) + ((self.days - 3) *
                               (float(obj_transport.valor_acrescimo) / (
                                       1 - float(obj_transport.percentual))))) / self.min_payers

            values.append(value)

            for i in range(1, self.days):
                values.append(0)
        finally:
            self.values = values

            return self.values

    def set_discount(self, value):
        self.tranport_go_and_back.set_discount(value)
        return super().set_discount(value)

    def set_percent_discount(self, percent):
        self.tranport_go_and_back.set_percent_discount(percent)
        return super().set_percent_discount(percent)

    def set_adjustiment(self, value):
        self.tranport_go_and_back.set_adjustiment(value)
        return super().set_adjustiment(value)
