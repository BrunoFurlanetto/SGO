class BaseValue:
    def __init__(self, value):
        self.value = float(value)
        self.discount = 0
        self.value_with_discount = self.calc_value_with_discount()

    def set_discount(self, value):
        self.discount = float(value)
        return self.discount

    def set_value(self, value):
        self.value = float(value)
        return self.value

    def calc_value_with_discount(self):
        return self.value - self.discount

    def calc_business_fee(self, percent):
        return self.value_with_discount * percent

    def calc_commission(self, percent):
        return self.value_with_discount * percent

    def do_object(self, percent_business_fee, percent_commission):
        return {
            "valor": self.value,
            "desconto": self.discount,
            "valor_com_desconto": self.value_with_discount,
            "taxa_comercial": self.calc_business_fee(percent_business_fee),
            "comissao_de_vendas": self.calc_commission(percent_commission)
        }
