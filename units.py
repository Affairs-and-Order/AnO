from abc import ABC, abstractmethod
from attack_scripts import Military
from random import randint

# Blueprint for units


class BlueprintUnit(ABC):

    """
    Every Unit class should follow and inherit this Blueprint!

    Neccessary variables:
        - unit_type: used to identify interfaces (i.e. TankUnit, SoldierUnit) for particular units
        - bonus: used to calculate the battle advantage
        - damage: used to determine the damage dealt to the target (infra, other buildings)
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


class SoldierUnit(BlueprintUnit):

    unit_type = "soldiers"

    def __init__(self, amount):
        self.amount = amount

    def attack(self, defending_units):
        if defending_units == "artillery":
            # self.damage += 55
            self.bonus += 3 * self.amount
        if defending_units == "apaches":
            self.bonus += 2 * self.amount
        if defending_units == "tanks":
            self.bonus -= 2 * self.amount
        if defending_units == "bombers":
            self.bonus -= 2 * self.amount
        return [self.damage, self.bonus]

    def buy(amount): pass


class TankUnit(BlueprintUnit):

    unit_type = "tanks"

    def __init__(self, amount):
        self.amount = amount

    def attack(self, defending_units):

        # One tank beats 4 soldiers (if one tank beat only 4 soldiers then soldiers really counter tanks because 1 tank costs the same as ~50 soldiers.)
        # One tank becomes 4x more effectiveness vs soldiers.
        if defending_units == 'soldiers':
            self.damage += 2
            self.bonus += 4 * self.amount
        if defending_units == "artillery":
            self.bonus -= 3 * self.amount
        # Micro randomization
        # One bomber beats random number of tanks (where they drop the bombs)
        # between 2 and 6
        if 'bombers' == defending_units:
            self.bonus -= randint(2, 6)*self.amount

        return [self.damage, self.bonus]

    def buy(amount): pass


class ArtilleryUnit(BlueprintUnit):

    unit_type = "artillery"

    def __init__(self, amount):
        self.amount = amount

    def attack(self, defending_units):

        # One artillery beats 3 tanks
        if defending_units == "tanks":
            self.bonus += 2 * self.amount
        if defending_units == "soldiers":
            self.bonus -= 2 * self.amount

        return [self.damage, self.bonus]

    def buy(): pass


class BomberUnit(BlueprintUnit):

    unit_type = "bombers"

    def __init__(self, amount):
        self.amount = amount

    def attack(self, defending_units):
        if defending_units == "soldiers":
            self.bonus += 2 * self.amount
        if defending_units == "tanks":
            self.bonus += 2 * self.amount
        if defending_units == "destroyers":
            self.bonus += 2 * self.amount
        if defending_units == "submarines":
            self.bonus += 2 * self.amount
        if defending_units == "fighters":
            self.bonus -= 2 * self.amount
        if defending_units == "apaches":
            self.bonus -= 2 * self.amount

        return [self.damage, self.bonus]

    def buy(amount): pass


class FighterUnit(BlueprintUnit):

    unit_type = "fighters"

    def __init__(self, amount):
        self.amount = amount

    def attack(self, defending_units):
        if defending_units == "bombers":
            # self.damage += 55
            self.bonus += 4 * self.amount
        if defending_units == "cruisers":
            self.bonus -= 2 * self.amount
        if defending_units == "apaches":
            self.bonus -= 1 * self.amount

        return [self.damage, self.bonus]

    def buy(amount): pass


class ApacheUnit(BlueprintUnit):

    unit_type = "apaches"

    def __init__(self, amount):
        self.amount = amount

    def attack(self, defending_units):
        if defending_units == "soldiers":
            self.bonus += 1 * self.amount
        if defending_units == "tanks":
            self.bonus += 1 * self.amount
        if defending_units == "bombers":
            self.bonus += 2 * self.amount
        if defending_units == "fighter":
            self.bonus += 2 * self.amount
        return [self.damage, self.bonus]

    def buy(): pass


class DestroyerUnit(BlueprintUnit):

    unit_type = "destroyers"

    def __init__(self, amount):
        self.amount = amount

    def attack(self, defending_units):
        if defending_units == "submarines":
            self.bonus += 1.6 * self.amount
        if defending_units == "bombers":
            self.bonus -= 1.5 * self.amount
        if defending_units == "cruisers":
            self.bonus -= 0.4 * self.amount
        return [self.damage, self.bonus]

    def buy(amount): pass


class CruiserUnit(BlueprintUnit):

    unit_type = "soldiers"

    def __init__(self, amount):
        self.amount = amount

    def attack(self, defending_units):
        if defending_units == "destroyers":
            self.bonus += 0.3 * self.amount
        if defending_units == "fighters":
            self.bonus += 0.1 * self.amount
        if defending_units == "apaches":
            self.bonus += 0.4 * self.amount
        if defending_units == "submarines":
            self.bonus -= 3 * self.amount
        return [self.damage, self.bonus]

    def buy(amount): pass


class SubmarineUnit(BlueprintUnit):

    unit_type = "submarines"

    def __init__(self, amount):
        self.amount = amount

    def attack(self, defending_units):
        if defending_units == "cruisers":
            self.bonus += 0.2 * self.amount
        if defending_units == "destroyers":
            self.bonus -= 0.4 * self.amount
        if defending_units == "bombers":
            self.bonus -= 4 * self.amount
        return [self.damage, self.bonus]

    def buy(): pass


class IcbmUnit(BlueprintUnit):

    unit_type = "icbm"

    def __init__(self, amount):
        self.amount = amount

    def attack(self, defending_units):
        if defending_units == "submarines":
            self.bonus -= 5 * self.amount
        return [self.damage, self.bonus]

    def buy(): pass


class NukeUnit(BlueprintUnit):

    unit_type = "nukes"

    def __init__(self, amount):
        self.amount = amount

    def attack(self, defending_units):
        if defending_units == "submarines":
            self.bonus -= 5 * self.amount
        return [self.damage, self.bonus]

    def buy(): pass


# does not have attack method, their functionality is coded separately in intelligence.py
class SpyUnit(BlueprintUnit):

    unit_type = "spies"

    def __init__(self, amount):
        self.amount = amount

    def buy(): pass


class Units(Military):

    allUnits = ["soldiers", "tanks", "artillery",
                "bombers", "fighters", "apaches"
                "destroyers", "cruisers", "submarines",
                "spies", "icbms", "nukes"]
    # spyunit not included because it has no interactions with other units, so it doesnt need to run inside the Units.attack method.
    allUnitInterfaces = [SoldierUnit, TankUnit, ArtilleryUnit, BomberUnit, FighterUnit,
                         ApacheUnit, DestroyerUnit, CruiserUnit, SubmarineUnit, IcbmUnit, NukeUnit]

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
    def attach_units(self, selected_units): # selected units is dictionary of  3 units
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
    def attack(self, attacker_unit, target, enemy_object):
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

                        # Calculate bonuses:
                        # Calculate the percentage of total units will be affected
                        defending_unit_amount = enemy_object.selected_units[target]

                        # sum of units amount
                        enemy_units_total_amount = sum(
                            enemy_object.selected_units.values())

                        # the affected percentage from sum of units
                        unit_of_army = (defending_unit_amount *
                                        100)/enemy_units_total_amount

                        # the bonus calculated based on affected percentage
                        affected_bonus = attack_effects[1]*(unit_of_army/100)

                        # Store at original attack_effects
                        # divide affected_bonus to make bonus effect less relevant
                        attack_effects[1] = affected_bonus/100

                        # DEBUGGING:
                        # print("UOA", unit_of_army, attacker_unit, target, self.user_id, affected_bonus)

                    # doesen't have any effect if unit amount is zero
                    else:
                        return (0, 0)

                    return tuple(attack_effects)
        else:
            return "Units are not attached!"

    def casualties(self, unit_type, amount):
        new_unit_amount = int(self.selected_units[unit_type]-amount)

        if new_unit_amount < 0:
            new_unit_amount = 0

        self.selected_units[unit_type] = new_unit_amount

        # Save it to the database

    def attack_cost(self, costs):
        self.supply_costs += costs


# DEBUGGING
if __name__ == "__main__":

    # CASE 1
    attacker = Units(2, {"artillery": 1000, "tanks": 1000, "soldiers": 1000},
                     selected_units_list=["artillery", "tanks", "soldiers"])
    defender = Units(1, {"submarines": 1000, "apaches": 1000, "soldiers": 1000},
                     selected_units_list=["submarines", "apaches", "soldiers"])

    Military.fight(attacker, defender)

    print("AFTER CASUALTIES")
    print(attacker.selected_units)
    print(defender.selected_units)

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
