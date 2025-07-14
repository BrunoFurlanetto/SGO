
from .basevalue import BaseValue
from ..models import OrcamentoMonitor, HorariosPadroes
from datetime import datetime, time
import math


class Monitor(BaseValue):
    def __init__(self, values, days, coming_id, exit_id, percent_business_fee, percent_commission):
        super().__init__(values, percent_business_fee, percent_commission)
        self.coming_id = coming_id
        self.exit_id = exit_id
        self.days = days
        self.classification_code = super().set_classification_code()

    def calc_value_monitor(self, id_tipo_monitoria):
        values = []

        try:
            object_monitor = OrcamentoMonitor.objects.get(pk=id_tipo_monitoria)
        except ValueError:
            for i in range(0, self.days):
                values.append(0.0)
        else:
            self.classification_code = super().set_classification_code(object_monitor)
            daily_monitor = float(object_monitor.valor) / float(object_monitor.racional_monitoria)
            if self.days == 1:
                values.append(float(daily_monitor))
            else:
                check_in = HorariosPadroes.objects.get(pk=self.coming_id).racional_monitor
                check_out = HorariosPadroes.objects.get(pk=self.exit_id).racional_monitor
                values.append(float(daily_monitor) * float(check_in))

                for i in range(1, (self.days - 1)):
                    values.append(float(daily_monitor))

                values.append(float(daily_monitor) * float(check_out))
        finally:
            self.values = values

            return self.values
