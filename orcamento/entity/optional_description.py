from .base_value import Base_Value


class Optional_Description(Base_Value):
    def __init__(self, value, is_fixed, optional_id, optinal_name):
        super().__init__(value)
        self.is_fixed = is_fixed
        self.id = optional_id
        self.name = optinal_name
        self.objectOptional = self.do_object()

    def do_object(self, percent_business_fee, percent_comission):
        informations = super().do_object(percent_business_fee, percent_comission)
        informations["id"] = self.id
        informations["nome"] = self.name
        informations["fixo"] = self.is_fixed
        return informations
