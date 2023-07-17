import math
from .models import OrcamentoMonitor, HorariosPadroes
from datetime import datetime


class Budget:
    def __init__(self, period_id, days, comming_id, exit_id):
        self.comming_id = comming_id
        self.exit_id = exit_id
        self.period_id = period_id
        self.days = int(days)
        self.total = 0
        self.pax = 30
        self.optional = {}
        self.meal = 0
        self.monitor = 0
        self.transport = 0

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

    def get_monitor(self):
        return self.monitor

    def get_transport(self):
        return self.transport

    def get_meal(self):
        return self.meal

    def set_pax(self, int):
        self.pax = int
        return self.pax

    def set_monitor(self, id):
        object_monitor = OrcamentoMonitor.objects.get(pk=id)
        daily_monitor = math.ceil(
            object_monitor.valor / object_monitor.racional_monitoria)

        check_in = HorariosPadroes.objects.get(pk=self.comming_id).horario
        check_out = HorariosPadroes.objects.get(pk=self.exit_id).horario

        first_daily_monitor = 1
        if check_in.hour > datetime(year=2023, hour=12).hour:
            first_daily_monitor = 0.5

        intermediate_daily_monitor = self.days - 2
        if intermediate_daily_monitor < 0:
            intermediate_daily_monitor = 0

        last_daily_monitor = 1
        if check_out.hour < datetime(year=2023, hour=12).hour:
            last_daily_monitor = 0.5

        self.monitor = math.ceil(daily_monitor *
                                 (first_daily_monitor + intermediate_daily_monitor + last_daily_monitor))

        return self.monitor

    def set_meal(self):
        # todo: pegar valores das refeições
        meal = 0

        # TODO: MANDAR PARA O BD
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

    def set_transport(self):
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
