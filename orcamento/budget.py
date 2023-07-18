import math
from .models import OrcamentoMonitor, HorariosPadroes, ValoresTransporte, OrcamentoDiaria, OrcamentoOpicional, OrcamentoPeriodo
from datetime import datetime
from .entity.period import Period
from .entity.monitor import Monitor
from .entity.daily_rate import Daily_Rate
from .entity.transport import Transport
from .entity.optional import Optional
from .entity.optional_description import Optional_Description


class Budget:
    def __init__(self, period_id, days, comming_id, exit_id):
        db_period = OrcamentoPeriodo.objects.get(pk=period_id)

        self.comming_id = comming_id
        self.exit_id = exit_id
        self.days = days

        self.period = Period(id=db_period.id, value=db_period.valor)
        self.daily_rate = Daily_Rate(
            check_in_id=self.comming_id,
            check_out_id=self.exit_id,
            period_id=self.period.id,
            days=self.days
        )
        self.monitor = Monitor(0, self.days)
        self.tranport = Transport(
            days=self.days,
            value=0,
            period_id=self.period.id,
        )
        self.optional = Optional(0)
        self.array_description_optional = []

    def set_optional(self, arr):
        optional_array = []

        for opt in arr:
            db_optional = OrcamentoOpicional.objects.get(pk=opt[0])
            discount = 0
            if db_optional.fixo:
                discount = float(opt[2])
            else:
                discount = float(opt[3])
                db_optional.valor = opt[2]
                db_optional.save()

            description = Optional_Description(
                db_optional.valor, db_optional.fixo, db_optional.id, db_optional.nome)
            description.set_discount(discount)
            optional_array.append(description.do_object())
        self.optional = optional_array

        return self.optional
