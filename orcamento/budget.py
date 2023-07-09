import math
from .utils import get_optional_pk


class Budget:
    def __init__(self, period_id, days, comming_id, exit_id):
        self.comming_id = comming_id
        self.exit_id = exit_id
        self.period_id = period_id
        self.days = int(days)
        self.total = 0
        self.pax = 30
        self.optional = {}

    def get_period_id(self):
        return self.period_id

    def get_days(self):
        return self.days

    def get_pax(self):
        return self.pax

    def get_total(self):
        return self.total

    def get_optional(self):
        return self.optional

    def set_pax(self, int):
        self.pax = int
        return self.pax

    def monitor(self, id):
        value_monitor = 0
        # todo: BUSCAR VALORES NO DB POR PK
        # todo: DESCOBRIR COMO É ESCALADO OS VALORES DOS MONITORES...7
        # 1 Monitor para 10 pax.
        # diaria do monitor 500,
        # id desc value/diaria
        # 1  meia 100
        # 2  cpm  200

        if id == 1:  # meia monitoria
            value_monitor = 5000
        if id == 2:  # monitoria completa
            value_monitor = 8000
        value_monitor = math.ceil(value_monitor / self.pax)
        self.total += value_monitor
        return value_monitor

    def meal(self):
        # todo: pegar valores das refeições
        meal = 0

        #TODO: MANDAR PARA O BD
        coffe = 0
        lunch = 70
        dinner = 70
        snack = 30

        days_with_full_meals = self.days - 2
        if days_with_full_meals < 0:
            days_with_full_meals = 0

        i = 0
        while i < days_with_full_meals:
            meal += coffe + lunch + dinner + snack
            i += 1

        match self.comming_id:
            case 1:
                meal += coffe + lunch + dinner + snack
            case 2:
                meal += lunch + dinner + snack
            case 3:
                meal += dinner + snack
            case 4:
                meal += snack
            case _:
                meal

        match self.exit_id:
            case 1:
                meal += coffe
            case 2:
                meal += coffe + lunch
            case 3:
                meal += coffe + lunch + dinner
            case _:
                meal

        self.total += meal
        return meal

    def transport(self):
        one_day = 2000
        two_days = 2500
        three_days = 2800
        plus_day_rate = 600
        value_transport = 0
        if self.days == 1:
            value_transport = math.ceil(one_day / self.pax)
        if self.days == 2:
            value_transport = math.ceil(two_days / self.pax)
        if self.days == 3:
            value_transport = math.ceil(three_days / self.pax)
        if self.days > 3:
            plus_days = self.days - 3
            value_transport = math.ceil(
                (three_days + (plus_days * plus_day_rate)) / self.pax)
        self.total += value_transport
        return value_transport

    def add_optional(self, arr):
        for optional_id in arr:
            # todo: find optional PK
            optional = get_optional_pk(optional_id)
            self.optional[optional['name']] = optional['price']

    def add_others(self, arr):
        for optional in arr:
            self.optional[optional] = arr[optional]

    def som_optional(self):
        value_optional = 0
        for optional in self.optional:
            value_optional += self.optional[optional]
        return value_optional
