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
        - damage: used to determine the damage dealt to a specific target (infra, other buildings), used for percentage calculation
            * in case of nukes: damage in nuke is the pure damage to units and infrastructure (when nuke targeted to a single object/unit damage is dealt)
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
    damage = 1
    supply_cost = 5

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
    damage = 40
    supply_cost = 5

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
    damage = 80
    supply_cost = 5

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
    damage = 100
    supply_cost = 5

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
    damage = 100
    supply_cost = 5

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
    damage = 100
    supply_cost = 5

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
    damage = 100
    supply_cost = 5

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
    damage = 200
    supply_cost = 5

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
    damage = 100
    supply_cost = 5

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


# Special units attack method handeled differently (not using the fight method)
class IcbmUnit(BlueprintUnit):

    unit_type = "icbm"
    damage = 1000
    supply_cost = 400

    def __init__(self, amount):
        self.amount = amount

    def attack(self, defending_units):
        if defending_units == "submarines":
            self.bonus -= 5 * self.amount
        return [self.damage, self.bonus]

    def buy(): pass


class NukeUnit(BlueprintUnit):

    unit_type = "nukes"
    damage = 8000
    supply_cost = 100

    def __init__(self, amount):
        self.amount = amount

    def attack(self, defending_units):
        if defending_units == "submarines":
            self.bonus -= 5 * self.amount
        else:
            pass
        return [self.damage, self.bonus]

    def buy(): pass


# does not have attack method, their functionality is coded separately in intelligence.py
class SpyUnit(BlueprintUnit):

    unit_type = "spies"
    damage = 0  # does not attack anyway

    def __init__(self, amount):
        self.amount = amount

    def buy(): pass

# make an instance of this object with Units(cId)
class Units(Military):

    allUnits = ["soldiers", "tanks", "artillery",
                "bombers", "fighters", "apaches",
                "destroyers", "cruisers", "submarines",
                "spies", "icbms", "nukes"]
    # spyunit not included because it has no interactions with other units, so it doesnt need to run inside the Units.attack method.
    allUnitInterfaces = [SoldierUnit, TankUnit, ArtilleryUnit, BomberUnit, FighterUnit,
                         ApacheUnit, DestroyerUnit, CruiserUnit, SubmarineUnit, IcbmUnit, NukeUnit]

    """
    When you want the data to be validated call object.attach_units(selected_units)

    Description of properties:
        - user_id: represents which user the units belongs to, type: integer
        - selected_units: represents the unit_type and unit_amount, type: dictionary; example: {"unit_name1": unit_amount1}
        - bonuses: bonus gained from general or something like this, type: integer (i don't know if this will be implemented or not)
    """

    def __init__(self, user_id, selected_units=None, bonuses=None, selected_units_list=None):
        self.user_id = user_id
        self.selected_units = selected_units
        self.bonuses = bonuses
        self.supply_costs = 0
        self.available_supplies = None

        # selected_units_list is needed at: Nations.py/Military->fight();
        # a list of selected_units keys
        self.selected_units_list = selected_units_list

    # Validate then attach units
    # Function parameter description:
    #    - selected_units read the Units class document above
    #    - units_count how many selected_units should be given (will be validated)
    #        example: units_count = 3 when 3 different unit_type should be selected (like from warchoose)
    #        example: units_count = 1 when 1 unit_type sould be selected (like a special unit: nuke, icmb)
    def attach_units(self, selected_units, units_count):
        unit_types = list(selected_units.keys())
        normal_units = self.get_military(self.user_id)
        special_units = self.get_special(self.user_id)

        available_units = normal_units.copy()
        available_units.update(special_units)

        try:
            # units_count = 3
            while units_count:
                current_unit = unit_types[units_count-1]
                if current_unit not in self.allUnits:
                    return "Invalid unit type!"

                if selected_units[current_unit] > available_units[current_unit]:
                    return "Invalid amount selected!"

                # Check for attack cost
                for interface in self.allUnitInterfaces:
                    if interface.unit_type == current_unit:
                        supply_check = self.attack_cost(interface.supply_cost*selected_units[current_unit])

                        if supply_check:
                            return supply_check

                        break

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
        # db.execute("UPDATE military SET {}=(?) WHERE id=(?)".format("soldiers=0, tanks=123 where id=1 --"), (66, self.user_id))

        connection.commit()
        connection.close()

    # Attack with all units contained in selected_units
    def attack(self, attacker_unit, target):
        if self.selected_units:

            # Call interface to unit type
            for interface in self.allUnitInterfaces:
                if interface.unit_type == attacker_unit:

                    # Check unit amount validity
                    unit_amount = self.selected_units.get(attacker_unit, None)

                    if unit_amount == None:
                        return "Unit is not valid!"

                    # interface.supply_cost*self.selected_units[attacker_unit] - calculates the supply cost based on unit amount
                    # supply = self.attack_cost(interface.supply_cost*self.selected_units[attacker_unit])
                    # if supply:
                        # return supply

                    if unit_amount != 0:
                        interface_object = interface(unit_amount)
                        attack_effects = interface_object.attack(target)

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

        # Save it to the database
        self.selected_units[unit_type] = new_unit_amount

    # Fetch the available supplies which compared to unit attack cost and check if user can't pay for it (can't give enought supplies)
    def attack_cost(self, cost):

        if not self.available_supplies:
            import sqlite3
            connection = sqlite3.connect('affo/aao.db')
            db = connection.cursor()

            attacker_id = db.execute("SELECT attacker FROM wars WHERE attacker=(?)", (self.user_id,)).fetchone()

            # If the user is the attacker (maybe optimize this to store the user role in the war)
            if attacker_id:
                self.available_supplies = db.execute("SELECT attacker_supplies FROM wars WHERE attacker=(?)", (self.user_id,)).fetchone()[0]

            # the user is defender
            else:
                self.available_supplies = db.execute("SELECT defender_supplies FROM wars WHERE defender=(?)", (self.user_id,)).fetchone()[0]

        if self.available_supplies < 200:
            return "The minimum supply amount is 200"

        self.supply_costs += cost
        if self.supply_costs > self.available_supplies:
            return "Not enougth supplies available"

# DEBUGGING
if __name__ == "__main__":
    # l = Units(1, {"nukes": 1})
    # l = Units(11)
    # l.attach_units({"nukes": 1}, 1)
    # print(l.attack("nukes", "submarines"))

    # l.attack_cost(100)

    # l = Units(10)
    # l.attack_cost(600)

    # CASE FOR SPECIAL FIGHT
    attacker = Units(11)
    defender = Units(10)

    defender.attach_units({"soldiers": 10, "tanks": 0, "artillery": 0}, 3)
    error = attacker.attach_units({"nukes": 1}, 1)
    if error:
        print(error)

    attacker.special_fight(attacker, defender, "soldiers")


    # CASE 1
    # attacker = Units(11, {"artillery": 0, "tanks": 34, "soldiers": 24},
    #                  selected_units_list=["artillery", "tanks", "soldiers"])
    # defender = Units(10, {"submarines": 20, "apaches": 3, "soldiers": 158},
    #                  selected_units_list=["submarines", "apaches", "soldiers"])
    #
    # Military.fight(attacker, defender)
    #
    # print("AFTER CASUALTIES")
    # print(attacker.selected_units)
    # print(defender.selected_units)

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
