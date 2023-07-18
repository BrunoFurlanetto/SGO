from .base_value import Base_Value


class Period(Base_Value):
    def __init__(self, id, value):
        super().__init__(value=value)
        self.id = id
