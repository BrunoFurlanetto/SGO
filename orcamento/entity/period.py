from .basevalue import BaseValue


class Period(BaseValue):
    def __init__(self, id, value):
        super().__init__(value=value)
        self.id = id
