class Base_Value:
    def __init__(self, value):
        self.value = value
        self.discount = 0
        self.value_with_discount = self.calc_value_with_discount()
        self.object = self.do_object()

    def set_discount(self, value):
        self.discount = value
        return self.discount

    def set_value(self, value):
        self.value = value
        return self.value

    def calc_value_with_discount(self):
        return (self.value - self.discount)

    def calc_business_fee(self, percent):
        self.business_fee = self.value_with_discount * percent
        return self.business_fee

    def calc_comission(self, percent):
        self.comission = self.value_with_discount * percent
        return self.comission

    def do_object(self, percent_business_fee, percent_comission):
        return {
            "valor": self.value,
            "desconto": self.discount,
            "valor_com_desconto": self.value_with_discount,
            "taxa_comercial": self.calc_business_fee(percent_business_fee),
            "comissao_de_vendas": self.calc_comission(percent_comission)
        }
