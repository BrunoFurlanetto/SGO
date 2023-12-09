from .basevalue import BaseValue


class OptionalDescription(BaseValue):
    def __init__(self, value, is_fixed, optional_id, optional_name, days, description=""):
        values = [float(value)]
        for i in range(1, days):
            values.append(0)

        super().__init__(values)
        self.is_fixed = is_fixed
        self.id = optional_id
        self.name = optional_name
        self.description = description

    def do_object(self, percent_business_fee, percent_commission, description=False):
        information = super().do_object(percent_business_fee, percent_commission)
        information["id"] = self.id
        information["nome"] = self.name
        information["fixo"] = self.is_fixed

        if description:
            information["description"] = self.description
        return information
