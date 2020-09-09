from abc import ABC, abstractmethod
from attack_scripts import Military

# Blueprint for units
class BlueprintUnit(ABC):

    """
    Every Unit class should follow and inherit this Blueprint!

    Neccessary variables:
        - unit_type: used to identify interfaces (i.e. TankUnit, SoldierUnit) for particular units
        - bonus: used to calculate the battle advantage
        - damage: used to determine the casualties
    """

    @abstractmethod
    def attack(defending_units): pass

    @abstractmethod
    def buy(amount): pass

class TankUnit(BlueprintUnit):

    unit_type = "tanks"

    @staticmethod
    def attack(defending_units):

        # these values are in percentage
        damage = 0
        bonus = 0

        if 'soldiers' == defending_units:
            damage += 2
            bonus += 8

        return (damage, bonus)

    def buy(amount): pass

class SoldierUnit(BlueprintUnit):

    unit_type = "soldiers"

    @staticmethod
    def attack(defending_units):

        # these values are in percentage
        damage = 0
        bonus = 0

        if defending_units == "artillery":
            damage += 55
            bonus += 10

        elif defending_units == "apaches":
            pass

        return (damage, bonus)

    def buy(amount): pass

class ArtilleryUnit(BlueprintUnit):

    unit_type = "artillery"

    @staticmethod
    def attack(defending_units):

        # these values are in percentage
        damage = 0
        bonus = 0

        if defending_units == "tanks":
            damage += 100
            bonus += 5

        return (damage, bonus)

    def buy(): pass

class Units(Military):

    allUnits = ["soldiers", "tanks", "artillery",
                "flying_fortresses", "fighter_jets", "apaches"
                "destroyers", "cruisers", "submarines",
                "spies", "icbms", "nukes"]
    allUnitInterfaces = [SoldierUnit, TankUnit, ArtilleryUnit]

    """
    When you want the data to be validated call object.attach_units(selected_units)

    Description of properties:
        - user_id: represents which user the units belongs to, type: integer
        - selected_units: represents the unit_type and unit_amount, type: dictionary
        - bonuses: bonus gained from general or something like this, type: integer (i don't know if this will be implemented or not)
    """

    def __init__(self, user_id, selected_units=None, bonuses=None, selected_units_list=None):
        self.user_id = user_id
        self.selected_units = selected_units
        self.bonuses = bonuses
        self.supply_costs = 0
        self.selected_units_list = selected_units_list

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
        except Exception as e:
            print(e)
            return "Not enoutgh unit type selected"

        # If the validation is ended successfully
        else:
            self.selected_units = selected_units
            self.selected_units_list = list(selected_units.keys())

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
    def attack(self, attacker_unit, target, enemy_unit_object):
        if self.selected_units:

            # Call interface to unit type
            for interface in self.allUnitInterfaces:
                if interface.unit_type == attacker_unit:
                    attack_effects = interface.attack(target)

                    # random cost, change it
                    # self.attack_cost(777)

                    return attack_effects
        else:
            return "Units are not attached!"

    def casualties(self, unit_type, amount):
        new_unit_amount = self.selected_units[unit_type]-amount
        if new_unit_amount < 0:
            new_unit_amount = 0

        self.selected_units[unit_type] = new_unit_amount

    def attack_cost(self, costs):
        self.supply_costs += costs

# DEBUGGING
if __name__ == "__main__":

    # CASE 1
    defender = Units(1, {"artillery": 1, "tanks": 3, "soldiers": 158},  selected_units_list=["artillery", "tanks", "soldiers"])
    attacker = Units(2, {"artillery": 0, "tanks": 34, "soldiers": 24},  selected_units_list=["artillery", "tanks", "soldiers"])

    # l = Units(1)
    # l.attach_units({"artillery": 0, "tanks": 0, "soldiers": 0})
    # print(l.selected_units_list, l.selected_units)

    Military.fight(attacker, defender)

    # CASE 2
    # import sqlite3
    # from random import uniform
    #
    # defender = Units(1, {"artillery": 1, "tanks": 3, "soldiers": 158})
    # attacker = Units(2, {"artillery": 0, "tanks": 34, "soldiers": 24})
    #
    # # defender.attach_units({"artillery": 1, "tanks": 3, "soldiers": 158})
    # # attacker.attach_units({"artillery": 0, "tanks": 44, "soldiers": 24})
    #
    # print(defender.selected_units)
    #
    # for i in range(3):
    #     print("ROUND", i)
    #     random_event = uniform(0, 5)
    #     size_chance = attacker.selected_units["tanks"] * 30/1000
    #     unit_type_bonuses = attacker.attack('tanks', 'soldiers', defender)[1] # tank bonus against soldiers
    #     nation1_chance = random_event+size_chance*unit_type_bonuses
    #
    #     random_event = uniform(0, 5)
    #     size_chance = defender.selected_units["soldiers"] * 30/1000
    #     unit_type_bonuses = 1
    #     nation2_chance = random_event+size_chance*unit_type_bonuses
    #
    #     print(nation1_chance)
    #     print(nation2_chance)
    #
    #     defender_loss = int(attacker.selected_units["tanks"]*0.12)
    #     defender.casualties("soldiers", defender_loss)
    #
    #
    # # print(Military.get_particular_unit(1, ["soldiers", "tanks"]))
    # print(defender.selected_units)
