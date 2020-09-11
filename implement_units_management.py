from abc import ABC, abstractmethod
from attack_scripts import Military
from random import randint

# keeping this just for memory purposes?

# Blueprint for units
class BlueprintUnit(ABC):

    """
    Every Unit class should follow and inherit this Blueprint!

    Neccessary variables:
        - unit_type: used to identify interfaces (i.e. TankUnit, SoldierUnit) for particular units
        - bonus: used to calculate the battle advantage
        - damage: used to determine the casualties
    """

    damage = 0
    bonus = 0

    """
    attack method:

        Calculates the advantage or disagvantage based on the enemy unit type.

        return: a tuple which contains (damage, bonus)

    buy method:
        return
    """
    @abstractmethod
    def attack(defending_units): pass

    @abstractmethod
    def buy(amount): pass

class TankUnit(BlueprintUnit):

    unit_type = "tanks"

    def __init__(self, amount):
        self.amount = amount

    def attack(self, defending_units):

        # One tank beats 4 soldiers
        if 'soldiers' == defending_units:
            self.damage += 2
            self.bonus += 4*self.amount

        # One artillery beats 3 tanks
        elif 'artillery' == defending_units:
            self.bonus -= 4*self.amount

        # Micro randomization
        # One bomber beats random number of tanks (where they drop the bombs)
        # between 2 and 6
        elif 'bombers' == defending_units:
            self.bonus -= randint(2, 6)*self.amount

        elif 'apaches' == defending_units:
            self.bonus -= 15

        return (self.damage, self.bonus)

    def buy(amount): pass

class SoldierUnit(BlueprintUnit):

    unit_type = "soldiers"

    def __init__(self, amount):
        self.amount = amount

    #
    def attack(self, defending_units):
        if defending_units == "artillery":
            self.damage += 55
            self.bonus += 5

        elif defending_units == "apaches":
            pass

        return (self.damage, self.bonus)

    def buy(amount): pass

class ArtilleryUnit(BlueprintUnit):

    unit_type = "artillery"

    def __init__(self, amount):
        self.amount = amount

    def attack(self, defending_units):
        if defending_units == "tanks":
            self.damage += 100
            self.bonus += 5

        return (self.damage, self.bonus)

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

                    # Check unit amount validity
                    unit_amount = self.selected_units.get(attacker_unit, None)

                    if unit_amount == None:
                        return "Unit is not valid!"
                    elif unit_amount != 0:
                        interface_object = interface(unit_amount)
                        attack_effects = interface_object.attack(target)

                        target_percentage = enemy_unit_object.selected_units[target]/1000
                        print("EFFECTS", attack_effects[1]*target_percentage, target, attacker_unit)

                    # doesen't have any effect if unit amount is zero
                    else:
                        return (0, 0)

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
    defender = Units(1, {"artillery": 20, "tanks": 3, "soldiers": 158},  selected_units_list=["artillery", "tanks", "soldiers"])
    attacker = Units(2, {"artillery": 0, "tanks": 34, "soldiers": 24},  selected_units_list=["artillery", "tanks", "soldiers"])

    # print(attacker.attack('soldiers', 'tanks', None))
    # print(attacker.attack('tanks', 'soldiers', None))
    # print(attacker.attack('tanks', 'soldiers', None))

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