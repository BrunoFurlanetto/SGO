from .models import OrcamentoOpicional, \
    OrcamentoPeriodo
from .entity.period import Period
from .entity.monitor import Monitor
from .entity.dailyrate import DailyRate
from .entity.transport import Transport
from .entity.optional import Optional
from .entity.optionaldescription import OptionalDescription
from .entity.total import Total


class Budget:
    def __init__(self, period_id, days, coming_id, exit_id):
        db_period = OrcamentoPeriodo.objects.get(pk=period_id)
        self.coming_id = coming_id
        self.exit_id = exit_id
        self.days = int(days)
        # todo: PEGAR INIT TAXAS DO BD
        self.business_fee = 0.09
        self.commission = 0.05

        self.period = Period(id=db_period.id, value=db_period.valor)
        self.daily_rate = DailyRate(
            check_in_id=self.coming_id,
            check_out_id=self.exit_id,
            period_id=self.period.id,
            days=self.days
        )
        self.monitor = Monitor(
            value=0,
            coming_id=self.coming_id,
            exit_id=self.exit_id,
            days=self.days
        )
        self.transport = Transport(
            days=self.days,
            value=0,
            period_id=self.period.id,
        )
        self.optional = Optional(0)
        self.array_description_optional = []
        self.others = Optional(0)
        self.array_description_others = []
        self.total = Total(0)
        self.daily_rate.calc_daily_rate()

    def set_business_fee(self, business_fee):
        self.business_fee = business_fee
        return business_fee

    def set_commission(self, commission):
        self.commission = commission
        return commission

    def set_others(self, arr):
        other_array = []
        for other in arr:
            obj_other = OptionalDescription(other['valor'], False, other['id'], other['nome'], other['descricao'])
            other_array.append(obj_other.do_object(
                percent_commission=self.commission,
                percent_business_fee=self.business_fee,
                description=True
            ))

        self.array_description_others = other_array
        return self.array_description_others

    def set_optional(self, arr, save=True):
        optional_array = []

        for opt in arr:
            db_optional = OrcamentoOpicional.objects.get(pk=opt[0])
            discount = 0

            if opt[1]:
                discount=opt[1]


            description = OptionalDescription(
                db_optional.valor,
                db_optional.fixo,
                db_optional.id,
                db_optional.nome
            )
            description.set_discount(discount)
            optional_array.append(description.do_object(
                percent_commission=self.commission,
                percent_business_fee=self.business_fee
            ))

        self.array_description_optional = optional_array
        return self.array_description_optional

    def return_object(self):
        description_options = self.array_description_optional
        description_options.append({
            "outros": self.array_description_others
        })
        return {
            "periodo_viagem": self.period.do_object(
                percent_commission=self.commission,
                percent_business_fee=self.business_fee
            ),
            "n_dias": self.days,
            "minimo_pagantes": self.transport.min_payers,
            "valores": {
                "tipo_monitoria": self.monitor.do_object(
                    percent_commission=self.commission,
                    percent_business_fee=self.business_fee
                ),
                "diaria": self.daily_rate.do_object(
                    percent_commission=self.commission,
                    percent_business_fee=self.business_fee
                ),
                "transporte": self.transport.do_object(
                    percent_commission=self.commission,
                    percent_business_fee=self.business_fee
                ),
                "opcionais": self.optional.do_object(
                    percent_commission=self.commission,
                    percent_business_fee=self.business_fee
                ),
                "outros": self.others.do_object(
                    percent_commission=self.commission,
                    percent_business_fee=self.business_fee
                )
            },
            "descricao_opcionais": description_options,
            "total": self.total.do_object(
                percent_commission=self.commission,
                percent_business_fee=self.business_fee
            ),
            "desconto_geral": self.total.general_discount,
            "taxa_comercial": self.business_fee,
            "comissao_de_vendas": self.commission
        }
