from .basevalue import BaseValue


class Total(BaseValue):
    def __init__(self, values):
        super().__init__(values)
        self.general_discount = 0

    def calc_total_value(self, daily_rate, monitor, optional, others, activities,
                         activities_sky, period, transport, days):
        self.general_discount = 0
        values = []

        for i in range(days):
            value = (float(daily_rate.get_list_values(days)[i]) + float(monitor.get_list_values(days)[i])
                     + float(optional.get_list_values(days)[i]) + float(others.get_list_values(days)[i])
                     + float(activities.get_list_values(days)[i]) + float(activities_sky.get_list_values(days)[i])
                     + float(period.get_list_values(days)[i]) + float(transport.get_list_values(days)[i]))

            values.append(value)

        self.set_values(values)
        self.general_discount = (daily_rate.discount + monitor.discount + optional.discount + others.discount +
                                 activities.discount + activities_sky.discount +
                                 period.discount + transport.discount + self.discount)

    def calc_value_with_discount(self):
        return self.get_total_values() - self.general_discount
    
    def set_discount(self, value):
        return super().set_discount(0)

    def do_object(self, percent_business_fee, percent_commission):
        return {
            "valor": self.get_total_values(),
            "desconto": self.discount,
            "desconto_geral": self.general_discount,
            "valor_final": self.calc_value_with_discount() + self.calc_business_fee(
                percent_business_fee) + self.calc_commission(percent_commission),
            "valor_com_desconto": self.calc_value_with_discount(),
            "taxa_comercial": self.calc_business_fee(percent_business_fee),
            "comissao_de_vendas": self.calc_commission(percent_commission),
            "descricao_valores": self.values
        }
