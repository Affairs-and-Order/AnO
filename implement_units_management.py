from attack_scripts import Military

class TankUnit:

    unit_type = "tanks"

    @staticmethod
    def attack(defending_units):
        damage = 0 # in percentage
        if 'soldiers' in defending_units:
            damage += 2

    def buy(): pass

class SoldierUnit:

    unit_type = "soldiers"

    @staticmethod
    def attack(defending_units):
        pass

    def buy(): pass

class Units(Military):

    allUnits = ["soldiers", "tanks", "artillery",
                "flying_fortresses", "fighter_jets", "apaches"
                "destroyers", "cruisers", "submarines",
                "spies", "icbms", "nukes"]
    allUnitInterfaces = [SoldierUnit, TankUnit]

    """
    When you want the data to be validated call object.attach_units(selected_units)

    Description of properties:
        - user_id: represents which user the units belongs to, type: integer
        - selected_units: represents the unit_type and unit_amount, type: dictionary
        - bonuses: bonus gained from general or something like this, type: integer (i don't know if this will be implemented or not)
    """

    def __init__(self, user_id, selected_units=None, bonuses=None):
        self.user_id = user_id
        self.selected_units = selected_units
        self.bonuses = bonuses

    # Validate then attach units
    def attach_units(self, selected_units):
        unit_types = list(selected_units.keys())
        normal_units = self.get_military(self.user_id)
        special_units = self.get_special(self.user_id)

        available_units = normal_units.copy()
        available_units.update(special_units)

        try:
            units_count = 3
            while units_count:
                current_unit = unit_types[units_count-1]
                if current_unit not in self.allUnits:
                    return "Invalid unit type!"

                if selected_units[current_unit] > available_units[current_unit]:
                    return "Invalid amount selected!"

                units_count -= 1
        except:
            return "Not enoutgh unit type selected"

        # If the validation is ended successfully
        else:
            self.selected_units = selected_units

    # Save unit records to the database
    def save(self):
        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        # IMPORTANT: this is used during development because it is SQL injectable
        # print("RUN")
        # db.execute("UPDATE military SET {}=(?) WHERE id=(?)".format("soldiers=0, tanks=123 where id=1 --"), (66, self.user_id))

        connection.commit()
        connection.close()

    # Attack with all units contained in selected_units
    def attack(self):
        if self.selected_units:
            unit_types = list(self.selected_units.keys())

            # Call interface to unit type
            for unit_type in unit_types:
                for interface in self.allUnitInterfaces:
                    if interface.unit_type == unit_type:
                        interface.attack(['x'])
                        break
        else:
            return "Units are not attached!"

    def casualties(self, unit_type, amount):
        new_unit_amount = self.selected_units[unit_type]-amount
        if new_unit_amount < 0:
            new_unit_amount = 0

        self.selected_units[unit_type] = new_unit_amount

    def attack_cost(self, costs): pass

# DEBUGGING
if __name__ == "__main__":
    import sqlite3
    from random import randint

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()
    default_defense = db.execute("SELECT default_defense FROM nation WHERE nation_id=(?)", (1,)).fetchall()
    connection.close()

    defender = Units(1, default_defense[0])
    attacker = Units(2)
    attacker.attach_units({"artillery": 0, "tanks": 0, "soldiers": 0})

    for roll in range(3):


    # attacker.attack()
    # defender.save()

    print("SELECTED UNITS", attacker.selected_units)
