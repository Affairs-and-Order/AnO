from abc import ABC, abstractmethod

class Units(ABC):
    def __init__(self, selected_units):
        self.selected_units = selected_units

    # Validate then attach units
    @classmethod
    def attach_units(cls, selected_units):
        if len(selected_units) == 3:
            # Extra validation:
            # if selected units are valid:
            # update database
            return cls(selected_units)
            # else: error

        else:
            return "Invalid!"

    @abstractmethod
    def attack(): pass

    def casualties(self, unit_type, amount): pass

    def attack_cost(self, cost): pass

class TankUnit(Units):

    @staticmethod
    def attack(defending_units):
        pass

class SoldierUnit(Units):

    @staticmethod
    def attack():
        pass
