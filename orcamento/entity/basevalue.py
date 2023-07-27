class BaseValue:
    def __init__(self, value):
        self.value = float(value)
        self.discount = 0

    def set_discount(self, value):
        self.discount = float(value)
        self.value_with_discount = self.calc_value_with_discount()
        return self.discount

    def set_value(self, value):
        self.value = float(value)
        self.value_with_discount = self.calc_value_with_discount()
        return self.value

    def calc_value_with_discount(self):
        return self.value - self.discount

    def calc_business_fee(self, percent):
        return (self.calc_value_with_discount() / (1 - percent)) - self.calc_value_with_discount()

    def calc_commission(self, percent):
        return (self.calc_value_with_discount() / (1 - percent)) - self.calc_value_with_discount()

    def do_object(self, percent_business_fee, percent_commission):
        return {
            "valor": self.value,
            "desconto": self.discount,
            "valor_final": self.calc_value_with_discount() + self.calc_business_fee(percent_business_fee) + self.calc_commission(percent_commission),
            "valor_com_desconto": self.calc_value_with_discount(),
            "taxa_comercial": self.calc_business_fee(percent_business_fee),
            "comissao_de_vendas": self.calc_commission(percent_commission)
        }
