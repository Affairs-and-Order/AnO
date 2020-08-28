from attack_scripts import Military

class Units(Military):

    allUnits = ["soldiers", "tanks", "artillery",
                "flying_fortresses", "fighter_jets", "apaches"
                "destroyers", "cruisers", "submarines",
                "spies", "icbms", "nukes"]

    """
    When you're debugging call Units(id, selected_units)
    When you want the data to be validated call Units.attach_units(id, selected_units)

    Description of properties:
        - user_id: represents which user the units belongs to, type: integer
        - selected_units: represents the unit_type and unit_amount, type: dictionary
        - bonuses: bonus gained from general or something like this, type: integer (i don't know if this will be implemented or not)
    """

    def __init__(self, user_id, selected_units, bonuses=None):
        self.selected_units = selected_units
        self.user_id = user_id

    #Validate then attach units
    @classmethod
    def attach_units(cls, user_id, selected_units):
        unit_types = selected_units.keys()
        if len(unit_types) == 3:
            # Additional check: selected_units are also present in allUnits
            return cls(user_id, selected_units)
        else:
            return "Invalid!"

    # Save unit records to the database
    def save(self):
        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        connection.close()

    def attack(): pass

    def casualties(self, unit_type, amount):
        new_unit_amount = self.selected_units[unit_type]-amount
        if new_unit_amount < 0:
            new_unit_amount = 0

        self.selected_units[unit_type] = new_unit_amount

    def attack_cost(self, costs): pass

class TankUnit:

    unit_type = "tank"

    @staticmethod
    def attack(defending_units):
        damage = 0 # in percentage
        if 'soldier' in defending_units:
            damage += 2

    def buy(): pass

class SoldierUnit:

    @staticmethod
    def attack():
        pass

    def buy(): pass

if __name__ == "__main__":
    # DEBUGGING

    def battle(attacker, defender):

        # If attacker is and object else fetch it from the db
        if type(attacker).__name__ == Units.__name__:
            print("hea")
        else:
            pass

        # defender = fetch from db and construct instance
        # class battle mechanics (randomize the stats)

        attacker.casualties("tank", 2)
        defender.casualties("soldier", 300)

    u1 = Units.attach_units(44, {"soldier": 100, "tank": 20, "jet": 2})
    u2 = Units.attach_units(20, {"soldier": 500, "tank": 1, "jet": 1})
    # battle(u1, u2)

    print(u1.__dict__)
    print(u2.__dict__)
