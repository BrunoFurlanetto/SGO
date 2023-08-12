from .basevalue import BaseValue


class Total(BaseValue):
    def __init__(self, value):
        super().__init__(value)
        self.general_discount = 0

    def calc_total_value(self, daily_rate, monitor, optional, others, period, transport):
        self.general_discount = 0
        self.value = 0
        self.value = daily_rate.value + monitor.value + optional.value + others.value + period.value + transport.value
        self.general_discount = (daily_rate.discount + monitor.discount + optional.discount + others.discount +
                                 period.discount + transport.discount + self.discount)
