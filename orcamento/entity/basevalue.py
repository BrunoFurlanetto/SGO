from math import ceil


class BaseValue:
    def __init__(self, values, percent_business_fee, percent_commission):
        self.percent_business_fee = percent_business_fee / 100
        self.percent_commission = percent_commission / 100
        self.values = values
        self.discount = 0
        self.__adjustment = 0

    def set_discount(self, value):
        self.discount = round(float(value), 2)
        self.value_with_discount = self.calc_value_with_discount()

        return self.discount

    def set_percent_discount(self, percent):
        total = self.get_total_values()
        discount = round(total * percent / 100, 2)
        self.set_discount(discount)

        return discount
    
    def set_adjustiment(self, value):
        self.__adjustment = round(float(value), 2)

        return self.__adjustment

    def get_adjustiment(self):
        return round(self.__adjustment, 2)
    
    def get_total_values(self):
        total = 0

        for value in self.values:
            total += round(float(value), 2)

        return total

    def set_values(self, values):
        self.values = [round(value, 2) for value in values]
        self.value_with_discount = self.calc_value_with_discount()

        return self.values

    def calc_value_with_discount(self):
        return self.get_total_values() - self.discount

    def calc_business_fee(self):
        return self.get_final_value() * self.percent_business_fee

    def calc_commission(self):
        return self.get_final_value() * self.percent_commission
    
    def get_list_values(self, days):
        if len(self.values) == days:
            return self.values

        mock_values = [0 for x in range(days)]
        return mock_values
    
    def get_final_value(self):
        return self.calc_value_with_discount() / (1 - (self.percent_business_fee + self.percent_commission))

    def do_object(self):
        return {
            "valor": round(self.get_total_values(), 2),
            "desconto": round(self.discount, 2),
            "valor_final": round(self.get_final_value(), 2),
                                # + self.calc_business_fee(percent_business_fee)
                                # + self.calc_commission(percent_commission)
                                # + self.get_adjustiment()),
            "valor_com_desconto": round(self.calc_value_with_discount(), 2),
            "ajuste": round(self.get_adjustiment(), 2),
            "taxa_comercial": round(self.calc_business_fee(), 2),
            "comissao_de_vendas": round(self.calc_commission(), 2),
            "valores": self.values
        }
