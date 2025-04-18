from .basevalue import BaseValue
from ..models import OrcamentoOpicional


class OptionalDescription(BaseValue):
    def __init__(self, value, percent_business_fee, percent_commission, optional_id, optional_name, days, category, description=""):
        values = [float(value)]
        for i in range(1, days):
            values.append(0)

        super().__init__(values, percent_business_fee, percent_commission)
        self.id = optional_id
        self.name = optional_name
        self.description = description
        self.category = category
        self.set_classification_code()

    def set_classification_code(self):
        opt = OrcamentoOpicional.objects.get(pk=self.id)

        if opt.classificacao:
            self.classification_code = opt.classificacao.codigo_padrao

    def do_object(self, description=False):
        information = super().do_object()
        information["id"] = self.id
        information["nome"] = self.name
        information["categoria"] = self.category

        if description:
            information["description"] = self.description

        return information
