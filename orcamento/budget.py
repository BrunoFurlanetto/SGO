from ceu.models import Atividades
from peraltas.models import AtividadePeraltas, AtividadesEco
from .models import OrcamentoOpicional, ValoresPadrao
from .entity.period import Period
from .entity.monitor import Monitor
from .entity.dailyrate import DailyRate
from .entity.transport import Transport
from .entity.optional import Optional
from .entity.optionaldescription import OptionalDescription
from .entity.total import Total
from .utils import JsonError


class Budget:
    def __init__(self, periods, days, coming_id, exit_id, days_list, business_fee=None, commission=None):
        self.coming_id = coming_id
        self.exit_id = exit_id
        self.days = int(days)
        self.days_list = days_list

        if business_fee is None:
            self.business_fee = float(ValoresPadrao.objects.get(id_taxa='taxa_comercial').valor_padrao)
        else:
            self.business_fee = business_fee
        if commission is None:    
            self.commission = float(ValoresPadrao.objects.get(id_taxa='comissao').valor_padrao)
        else: 
            self.commission = commission

        self.period = Period(
            days=days_list,
            percent_business_fee=self.business_fee,
            percent_commission=self.commission,
        )
        self.daily_rate = DailyRate(
            check_in_id=self.coming_id,
            check_out_id=self.exit_id,
            periods=periods,
            days=self.days,
            percent_business_fee=self.business_fee,
            percent_commission=self.commission,
        )
        self.monitor = Monitor(
            values=[],
            coming_id=self.coming_id,
            exit_id=self.exit_id,
            days=self.days,
            percent_business_fee=self.business_fee,
            percent_commission=self.commission,
        )
        self.transport = Transport(
            days=self.days,
            values=[],
            checkin=days_list[0],
            percent_business_fee=self.business_fee,
            percent_commission=self.commission,
        )
        self.optional = Optional([], days, self.business_fee, self.commission)
        self.array_description_optional = []
        self.others = Optional([], days, self.business_fee, self.commission)
        self.array_description_others = []
        self.activities = Optional([], days, self.business_fee, self.commission)
        self.array_description_activities = []
        self.activities_sky = Optional([], days, self.business_fee, self.commission)
        self.array_description_activities_sky = []
        self.total = Total([], self.business_fee, self.commission)
        self.daily_rate.calc_daily_rate()

    def calculate(self, data, gerencia, valores_op):
        # self.set_commission(gerencia["comissao"]) if "comissao" in gerencia else ...
        # self.set_business_fee(gerencia["taxa_comercial"]) if "taxa_comercial" in gerencia else ...
        opt_data = []
        act_data = []
        act_sky_data = []

        # self.transport.set_min_payers(data["minimo_pagantes"]) if "minimo_pagantes" in data else ...
        self.transport.set_min_payers(gerencia["minimo_onibus"]) if "minimo_onibus" in gerencia else ...
        # self.set_business_fee(data["taxa_comercial"]) if "taxa_comercial" in data else ...
        # self.set_commission(data["comissao_de_vendas"]) if "comissao_de_vendas" in data else ...
        # self.period.set_discount(gerencia["desconto_produto"]) if "desconto_produto" in gerencia else ...
        # self.period.set_discount(data["desconto_periodo_viagem"]) if "desconto_periodo_viagem" in data else ...
        # self.daily_rate.set_discount(data["desconto_diarias"]) if "desconto_diarias" in data else ...

        self.daily_rate.set_discount(gerencia["desconto_produto"]) if "desconto_produto" in gerencia else ...
        self.monitor.calc_value_monitor(data['tipo_monitoria'])
        self.monitor.set_discount(gerencia["desconto_monitoria"]) if "desconto_monitoria" in gerencia else ...
        # self.monitor.set_discount(
        #     data["desconto_tipo_monitoria"]) if "desconto_tipo_monitoria" in gerencia else ...
        self.transport.calc_value_transport(data.get("transporte"))
        self.transport.set_discount(gerencia["desconto_transporte"]) if "desconto_transporte" in gerencia else ...
        # self.transport.set_discount(data["desconto_transporte"]) if "desconto_transporte" in data else ...
        # self.total.set_discount(gerencia["desconto_geral"]) if "desconto_geral" in gerencia else ...

        # Veriricação se aplica tava MP
        self.period.set_period_rate() if data.get('orcamento_promocional', '') == '' and not data[
            'only_sky'] and data.get('promocional', '') != 'on' else ...

        if not self.period.values:
            return

        # discout with percent
        self.transport.set_percent_discount(
            gerencia["desconto_transporte_percent"]) if "desconto_transporte_percent" in gerencia else ...
        self.monitor.set_percent_discount(
            gerencia["desconto_monitoria_percent"]) if "desconto_monitoria_percent" in gerencia else ...
        self.daily_rate.set_percent_discount(
            gerencia["desconto_produto_percent"]) if "desconto_produto_percent" in gerencia else ...
        # self.daily_rate.set_percent_discount(
        #     data["desconto_diarias_percent"]) if "desconto_diarias_percent" in data else ...

        # adjustment values
        self.daily_rate.set_adjustiment(gerencia["ajuste_diaria"]) if "ajuste_diaria" in gerencia else ...
        
        # OPICIONAIS
        if len(valores_op) == 0:
            if "opcionais" in data:
                opt_data = [[opt, 0, 0, 0] for opt in data['opcionais']]
        else:
            for key, value in valores_op.items():
                opt_data.append(value)

        self.set_optional(opt_data)
        self.optional.calc_value_optional(self.array_description_optional)
        # self.set_activities(act_data)
        # self.activities.calc_value_optional(self.array_description_activities)
        # self.set_activities_sky(act_sky_data)
        # self.activities_sky.calc_value_optional(self.array_description_activities_sky)
        self.set_others(data.get("opcionais_extra"))
        self.others.calc_value_optional(self.array_description_others)

        if data.get('transporte') and data.get('transporte') == 'sim' and len(
                self.transport.tranport_go_and_back.values) == 0:
            return
        
        # CAlCULAR TOTAL
        is_go_and_back = data.get('is_go_and_back') == "vai_e_volta"
        self.total.calc_total_value(
            monitor=self.monitor,
            period=self.period,
            optional=self.optional,
            others=self.others,
            activities=self.activities,
            activities_sky=self.activities_sky,
            daily_rate=self.daily_rate,
            transport=self.transport.tranport_go_and_back if is_go_and_back else self.transport,
            days=data["n_dias"],
        )

    # def set_business_fee(self, business_fee):
    #     self.business_fee = business_fee
    #     return business_fee

    # def set_commission(self, commission):
    #     self.commission = commission
    #     return commission

    def set_others(self, arr):
        other_array = []

        try:
            for other in arr:
                obj_other = OptionalDescription(
                    other['valor'],
                    self.business_fee,
                    self.commission, 
                    other['id'],
                    other['nome'], 
                    self.days, 
                    "extra", 
                    other['descricao'],
                    )
                other_array.append(obj_other.do_object(
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
            try:
                discount = opt[1]
            except IndexError:
                ...

            description = OptionalDescription(
                db_optional.valor,
                self.business_fee,
                self.commission, 
                db_optional.id,
                db_optional.nome,
                self.days,
                db_optional.categoria.nome_categoria,
            )
            description.set_discount(discount)
            optional_array.append(description.do_object())

        self.array_description_optional = optional_array

        return self.array_description_optional

    def set_activities(self, arr):
        activities_array = []

        for opt in arr:
            db_optional = OrcamentoOpicional.objects.get(pk=opt[0])
            discount = 0

            if opt[1]:
                discount = opt[1]

            description = OptionalDescription(
                db_optional.valor,
                self.business_fee,
                self.commission, 
                db_optional.id,
                db_optional.nome,
                self.days,
                db_optional.categoria,
            )
            description.set_discount(discount)
            activities_array.append(description.do_object())

        self.array_description_activities = activities_array
        return self.array_description_activities

    def set_activities_sky(self, arr):
        activities_array = []

        try:
            for opt in arr:
                db_optional = OrcamentoOpicional.objects.get(pk=opt[0])
                discount = 0

                # if opt[1]:
                #     discount = opt[1]

                description = OptionalDescription(
                    db_optional.valor,
                    self.business_fee,
                    self.commission,
                    db_optional.id,
                    db_optional.nome,
                    self.days,
                    db_optional.categoria,
                )
                description.set_discount(discount)
                activities_array.append(description.do_object())
        except TypeError as e:
            ...
        except Exception as e:
            print(f'Erro: ({e}!')
        else:
            self.array_description_activities_sky = activities_array

            return self.array_description_activities_sky

    def return_object(self):
        description_options = self.array_description_optional + self.array_description_others + self.array_description_activities + self.array_description_activities_sky
        # description_options.append({
        #     "outros": self.array_description_others,
        #     "atividades": self.array_description_activities,
        #     "atividades_ceu": self.array_description_activities_sky
        # })
        return {
            "periodo_viagem": self.period.do_object(),
            "n_dias": self.days,
            "minimo_pagantes": self.transport.min_payers,
            "valores": {
                "tipo_monitoria": self.monitor.do_object(),
                "diaria": self.daily_rate.do_object(),
                "transporte": self.transport.do_object(),
                "transporte_leva_e_busca": self.transport.tranport_go_and_back.do_object(),
                "opcionais": self.optional.do_object(),
                "opcionais_extras": self.others.do_object(),
                # "opcionais_ecoturismo": self.activities.do_object(),
                # "opcionais_ceu": self.activities_sky.do_object()
            },
            "descricao_opcionais": description_options,
            "total": self.total.do_object(
            ),
            "desconto_geral": self.total.general_discount,
            "taxa_comercial": self.business_fee,
            "comissao_de_vendas": self.commission,
            "days": [day.strftime('%Y-%m-%d') for day in self.days_list],
        }
