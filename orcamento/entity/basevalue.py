class BaseValue:
    def __init__(self, values):
        self.values = values
        self.discount = 0

    def set_discount(self, value):
        self.discount = float(value)
        self.value_with_discount = self.calc_value_with_discount()
        return self.discount

    def get_total_values(self):
        total = 0
        for value in self.values:
            total += float(value)
        return total

    def set_values(self, values):
        self.values = values
        self.value_with_discount = self.calc_value_with_discount()
        return self.values

    def calc_value_with_discount(self):
        return self.get_total_values() - self.discount

    def calc_business_fee(self, percent):
        return (self.calc_value_with_discount() / (1 - percent)) - self.calc_value_with_discount()

    def calc_commission(self, percent):
        return (self.calc_value_with_discount() / (1 - percent)) - self.calc_value_with_discount()

    def get_list_values(self, days):
        if len(self.values) == days:
            return self.values

        mock_values = [0 for x in range(days)]
        return mock_values

    def do_object(self, percent_business_fee, percent_commission):
        return {
            "valor": self.get_total_values(),
            "desconto": self.discount,
            "valor_final": self.calc_value_with_discount() + self.calc_business_fee(percent_business_fee) + self.calc_commission(percent_commission),
            "valor_com_desconto": self.calc_value_with_discount(),
            "taxa_comercial": self.calc_business_fee(percent_business_fee),
            "comissao_de_vendas": self.calc_commission(percent_commission),
            "valores": self.values
        }
