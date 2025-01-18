from .basevalue import BaseValue
from ..models import HorariosPadroes
from datetime import datetime, time


class DailyRate(BaseValue):
    def __init__(self, check_in_id, check_out_id, periods, days, percent_business_fee, percent_commission):
        super().__init__([], percent_business_fee, percent_commission)
        self.check_in_id = check_in_id
        self.check_out_id = check_out_id
        self.periods = periods
        self.days = int(days)
    
    def calc_daily_rate(self, so_ceu=False):
        check_in = float(HorariosPadroes.objects.get(pk=self.check_in_id).racional)
        check_out = float(HorariosPadroes.objects.get(pk=self.check_out_id).racional)
        values = []

        if self.days == 1:
            if not so_ceu:
                value_period = float((self.periods[0]).valor)
            else:
                value_period = 0.00
            values.append(value_period)
        else:
            value_period_check_in = float(self.periods[0].valor)
            value_period_check_out = float((self.periods[len(self.periods) - 1]).valor)
            values.append(check_in * value_period_check_in)

            for i in range(1, (len(self.periods) - 1)):
                if not so_ceu:
                    value_period = float((self.periods[i]).valor)
                else:
                    value_period = 0.00

                values.append(value_period)

            values.append(check_out * value_period_check_out)

        self.set_values(values)

        return self.values
    
    def general_discount_daily(self, value):
        discount = float(value)

        if self.discount > 0:
            discount = self.discount + float(value)

        self.set_discount(discount)

    def do_object(self):
        information = super().do_object()
        daily_accomodation = self.days - 1 if self.days > 1 else 1
        value_daily_accomodation = self.get_total_values() / daily_accomodation
        values_accomodation = [value_daily_accomodation for _ in range(0, self.days)]
        total = 0
        for value in values_accomodation:
            total += float(value)

        information["comparativo_de_diarias"] = {
            "diarias_hospedagem": daily_accomodation,
            "valores_hospedagem": values_accomodation,
            "total_valores_hospedagem": total,
            "diarias_acampamento": self.days,
            "valores_acampamento": self.values,
            "total_valores_acampamento": self.get_total_values(),
        }
        return information