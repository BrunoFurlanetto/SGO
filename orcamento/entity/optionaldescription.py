from .basevalue import BaseValue
from ..models import OrcamentoOpicional


class OptionalDescription(BaseValue):
    def __init__(self, value, percent_business_fee, percent_commission, optional_id, optional_name, days, category, description=""):
        values = [float(value)]
        for i in range(1, days):
            values.append(0)

        self.id = optional_id
        self.name = optional_name
        self.description = description
        self.category = category
        super().__init__(values, percent_business_fee, percent_commission)
        self.set_classification_code()

    def set_classification_code(self, o=None):
        try:
            opt = OrcamentoOpicional.objects.get(pk=self.id)
        except ValueError:
            self.classification_code = ''
        else:
            self.classification_code = super().set_classification_code(opt)
        print(self.classification_code)

    def do_object(self, description=False):
        information = super().do_object()
        information["id"] = self.id
        information["nome"] = self.name
        information["categoria"] = self.category
        # information["codigo_classificacao_item"] = self.classification_code

        if description:
            information["description"] = self.description

        return information
