from .basevalue import BaseValue


class Total(BaseValue):
    def __init__(self, value):
        super().__init__(value)
        self.general_discount = 0

    def calc_total_value(self, daily_rate, monitor, optional, others, period, transport):
        self.general_discount = 0
        self.value = 0
        self.value = daily_rate.value + monitor.value + optional.value + others.value + period.value + transport.value
        self.general_discount = (daily_rate.discount + monitor.discount + optional.discount + others.discount +
                                 period.discount + transport.discount + self.discount)

    def calc_value_with_discount(self):
        return self.value - self.discount - self.general_discount

    def do_object(self, percent_business_fee, percent_commission):
        return {
            "valor": self.value,
            "desconto": self.discount,
            "desconto_geral": self.general_discount,
            "valor_final": self.calc_value_with_discount() + self.calc_business_fee(percent_business_fee) + self.calc_commission(percent_commission),
            "valor_com_desconto": self.calc_value_with_discount(),
            "taxa_comercial": self.calc_business_fee(percent_business_fee),
            "comissao_de_vendas": self.calc_commission(percent_commission)
        }