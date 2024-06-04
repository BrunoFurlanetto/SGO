from .basevalue import BaseValue
from math import ceil

class Total(BaseValue):
    def __init__(self, values, percent_business_fee, percent_commission):
        super().__init__(values, percent_business_fee, percent_commission)
        self.general_discount = 0

    def calc_total_value(self, daily_rate, monitor, optional, others, activities,
                         activities_sky, period, transport, days):
        self.general_discount = 0
        values = []

        for i in range(days):
            value = (float(daily_rate.get_list_values(days)[i]) + float(monitor.get_list_values(days)[i])
                     + float(optional.get_list_values(days)[i]) + float(others.get_list_values(days)[i])
                     + float(activities.get_list_values(days)[i]) + float(activities_sky.get_list_values(days)[i])
                     + float(period.get_list_values(days)[i]) + float(transport.get_list_values(days)[i]))

            values.append(value)

        self.set_values(values)
        self.general_discount = (daily_rate.discount + monitor.discount + optional.discount + others.discount +
                                 activities.discount + activities_sky.discount +
                                 period.discount + transport.discount + self.discount)
        
        general_adjutiment = (
            daily_rate.get_adjustiment() + monitor.get_adjustiment() + optional.get_adjustiment() + others.get_adjustiment() +
                                 activities.get_adjustiment() + activities_sky.get_adjustiment() +
                                 period.get_adjustiment() + transport.get_adjustiment() + self.get_adjustiment()
        )

        self.set_adjustiment(general_adjutiment)

    def calc_value_with_discount(self):
        return self.get_total_values() - self.general_discount
    
    def set_discount(self, value):
        return super().set_discount(0)
    
    def get_final_value(self):
        return ceil(round(self.calc_value_with_discount() / (1 - (self.percent_business_fee + self.percent_commission)), 5)) #=ARREDONDAR.PARA.CIMA((PTF+PD+PM+PB+POp-PDesc)/(1-(TxC+TxN));0)


    def do_object(self):
        information = super().do_object()
        information["taxa_comercial"] = self.calc_business_fee(),
        information["comissao_de_vendas"] = self.calc_commission(),
        information["desconto_geral"] = self.general_discount
        information["descricao_valores"] = self.values
        information["valor_final"] = (self.get_final_value()) #=ARREDONDAR.PARA.CIMA((PTF+PD+PM+PB+POp-PDesc)/(1-(TxC+TxN));0)
        information["arredondamento"] = (self.get_final_value()) - (
            self.calc_value_with_discount() + self.calc_business_fee() + self.calc_commission()
        ) #=PF-(PTF+PD+PM+PB+POp-PDesc+PCom+PNeg)
        return information
        
