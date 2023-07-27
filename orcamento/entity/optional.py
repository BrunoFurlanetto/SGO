from .basevalue import BaseValue


class Optional(BaseValue):
    pass

    def calc_value_optional(self, optional_description):
        total = 0
        discount = 0
        for opt in optional_description:
            total += opt["valor"]
            discount += opt["desconto"]

        self.set_value(total)
        self.set_discount(discount)
        return self.value
