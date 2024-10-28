from .basevalue import BaseValue


class Optional(BaseValue):
    def __init__(self, values, days, percent_business_fee, percent_commission):
        super().__init__(values, percent_business_fee, percent_commission)
        self.days = days

    def calc_value_optional(self, optional_description):
        total = 0
        discount = addition = 0

        for opt in optional_description:
            total += opt["valor"]
            discount += opt["desconto"]
            addition += opt["acrescimo"]

        value = [total]
        for i in range(1, self.days):
            value.append(0)

        self.set_values(value)
        self.set_discount(discount)
        self.set_addition(addition)

        return self.values
