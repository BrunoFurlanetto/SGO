from ceu.models import Atividades
from peraltas.models import AtividadePeraltas, AtividadesEco
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
    def __init__(self, periods, days, coming_id, exit_id, days_list):
        self.coming_id = coming_id
        self.exit_id = exit_id
        self.days = int(days)
        self.days_list = days_list
        # todo: PEGAR INIT TAXAS DO BD
        self.business_fee = 0.09
        self.commission = 0.05

        self.period = Period(periods)
        self.daily_rate = DailyRate(
            check_in_id=self.coming_id,
            check_out_id=self.exit_id,
            periods=periods,
            days=self.days
        )
        self.monitor = Monitor(
            values=[],
            coming_id=self.coming_id,
            exit_id=self.exit_id,
            days=self.days
        )
        self.transport = Transport(
            days=self.days,
            values=[],
            periods=periods,
        )
        self.optional = Optional([], days)
        self.array_description_optional = []
        self.others = Optional([], days)
        self.array_description_others = []
        self.activities = Optional([], days)
        self.array_description_activities = []
        self.activities_sky = Optional([], days)
        self.array_description_activities_sky = []
        self.total = Total([])
        self.daily_rate.calc_daily_rate()

    def set_business_fee(self, business_fee):
        self.business_fee = business_fee
        return business_fee

    def set_commission(self, commission):
        self.commission = commission
        return commission

    def set_others(self, arr):
        other_array = []

        try:
            for other in arr:
                obj_other = OptionalDescription(other['valor'], False, other['id'],
                                                other['nome'], self.days, other['descricao'])
                other_array.append(obj_other.do_object(
                    percent_commission=self.commission,
                    percent_business_fee=self.business_fee,
                    description=True
                ))
        except TypeError:
            ...
        else:
            self.array_description_others = other_array

            return self.array_description_others

    def set_optional(self, arr, save=True):
        optional_array = []

        for opt in arr:
            db_optional = OrcamentoOpicional.objects.get(pk=opt[0])
            discount = 0

            if opt[1]:
                discount = opt[1]

            description = OptionalDescription(
                db_optional.valor,
                db_optional.fixo,
                db_optional.id,
                db_optional.nome,
                self.days
            )
            description.set_discount(discount)
            optional_array.append(description.do_object(
                percent_commission=self.commission,
                percent_business_fee=self.business_fee
            ))

        self.array_description_optional = optional_array
        return self.array_description_optional

    def set_activities(self, arr):
        activities_array = []

        for opt in arr:
            db_optional = AtividadesEco.objects.get(pk=opt[0])
            discount = 0

            if opt[1]:
                discount = opt[1]

            description = OptionalDescription(
                db_optional.valor,
                1,
                db_optional.id,
                db_optional.nome_atividade_eco,
                self.days
            )
            description.set_discount(discount)
            activities_array.append(description.do_object(
                percent_commission=self.commission,
                percent_business_fee=self.business_fee
            ))

        self.array_description_activities = activities_array
        return self.array_description_activities

    def set_activities_sky(self, arr):
        activities_array = []

        try:
            for opt in arr:
                db_optional = Atividades.objects.get(pk=opt)
                discount = 0

                # if opt[1]:
                #     discount = opt[1]

                description = OptionalDescription(
                    db_optional.valor,
                    1,
                    db_optional.id,
                    db_optional.atividade,
                    self.days
                )
                description.set_discount(discount)
                activities_array.append(description.do_object(
                    percent_commission=self.commission,
                    percent_business_fee=self.business_fee
                ))
        except TypeError as e:
            ...
        else:
            self.array_description_activities_sky = activities_array

            return self.array_description_activities_sky

    def return_object(self):
        description_options = self.array_description_optional
        description_options.append({
            "outros": self.array_description_others,
            "atividades": self.array_description_activities,
            "atividades_ceu": self.array_description_activities_sky
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
                "transporte_leva_e_busca": self.transport.tranport_go_and_back.do_object(
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
                ),
                "atividades": self.activities.do_object(
                    percent_commission=self.commission,
                    percent_business_fee=self.business_fee
                ),
                "atividades_ceu": self.activities_sky.do_object(
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
            "comissao_de_vendas": self.commission,
            "periodos": self.period.get_periods(),
            "days": [day.strftime('%Y-%m-%d') for day in self.days_list],
        }
