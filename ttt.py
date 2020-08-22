class Units(object):
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

    # Every child must implement this method
    # @abstrackmethod
    @staticmethod
    def attack():
        pass

    def casualties(self, unit_type, amount):
        pass

class TankUnit(Units):

    @staticmethod
    def attack(self, defending_units):
        # if defending_units == 'soldiers': +2% attack damage
        pass

class SoldierUnit(Units):

    @staticmethod
    def attack(self, defenting_units):
        pass

def battle(attacker, defender):
    # select unit against unit
    selected_attacker = "tank"
    selected_defender = "soldier"

    if selected_attacker == "tank":
        TankUnit.attack(selected_defender)
        attacker.casualties("tank", 2)
        defender.casualties("soldiers", 24)

def route():
    user1 = Units.attach_units(["tank", "soldier", "jet fighter"])
    user2 = Units.attach_units(["ships", "soldier", "xy"])
    battle(user1, user2)

# class Ob:
#     # health, damage
#     pass
#
# class Player(Ob):
#     # gear, mana
#     pass
#
# class Dragon(Ob):
#     # loot,
#     pass
