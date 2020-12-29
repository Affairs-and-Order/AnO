# FULLY MIGRATED

from abc import ABC, abstractmethod
from attack_scripts import Military
from random import randint
from typing import Union
import psycopg2
from dotenv import load_dotenv
load_dotenv()
import os

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
    supply_cost = 1

    def __init__(self, amount: int) -> None:
        self.amount = amount

    def attack(self, defending_units: str) -> list:
        if defending_units == "artillery":
            # self.damage += 55
            self.bonus += 3 * self.amount
        if defending_units == "apaches":
            self.bonus += 2 * self.amount
        return [self.damage*self.amount, self.bonus]

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
            self.bonus += 6 * self.amount

        return [self.damage*self.amount, self.bonus]

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
        return [self.damage*self.amount, self.bonus]

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

        # Micro randomization
        # One bomber beats random number of tanks (where they drop the bombs)
        # between 2 and 6
        if defending_units == "tanks":
            self.bonus += randint(2, 6)*self.amount
            # self.bonus += 2 * self.amount

        if defending_units == "destroyers":
            self.bonus += 2 * self.amount
        if defending_units == "submarines":
            self.bonus += 2 * self.amount
        return [self.damage*self.amount, self.bonus]

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
        return [self.damage*self.amount, self.bonus]

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
        elif defending_units == "tanks":
            self.bonus += 1 * self.amount
        elif defending_units == "bombers":
            self.bonus += 2 * self.amount
        elif defending_units == "fighter":
            self.bonus += 2 * self.amount
        return [self.damage*self.amount, self.bonus]

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
        return [self.damage*self.amount, self.bonus]

    def buy(amount): pass


class CruiserUnit(BlueprintUnit):

    unit_type = "cruisers"
    damage = 200
    supply_cost = 5

    def __init__(self, amount):
        self.amount = amount

    def attack(self, defending_units):
        if defending_units == "destroyers":
            self.bonus += 0.3 * self.amount
        elif defending_units == "fighters":
            self.bonus += 0.1 * self.amount
        elif defending_units == "apaches":
            self.bonus += 0.4 * self.amount
        return [self.damage*self.amount, self.bonus]

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
        return [self.damage*self.amount, self.bonus]

    def buy(): pass


# Special units attack method handeled differently (not using the fight method)
class IcbmUnit(BlueprintUnit):

    unit_type = "icbms"
    damage = 1000
    supply_cost = 400

    def __init__(self, amount):
        self.amount = amount

    def attack(self, defending_units):
        if defending_units == "submarines":
            self.bonus -= 5 * self.amount
        return [self.damage*self.amount, self.bonus]

    def buy(): pass


class NukeUnit(BlueprintUnit):

    unit_type = "nukes"
    damage = 3000
    supply_cost = 100

    def __init__(self, amount):
        self.amount = amount

    def attack(self, defending_units):
        if defending_units == "submarines":
            self.bonus -= 5 * self.amount
        else:
            pass
        return [self.damage*self.amount, self.bonus]

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

    def __init__(self, user_id, selected_units: dict=None, bonuses: int=None, selected_units_list: list=None):
        self.user_id = user_id
        self.selected_units = selected_units
        self.bonuses = bonuses
        self.supply_costs = 0
        self.available_supplies = None

        # selected_units_list is needed at: Nations.py/Military->fight();
        # a list of selected_units keys
        self.selected_units_list = selected_units_list

    # this is needed because we can't store object in server side cache :(
    @classmethod
    def rebuild_from_dict(cls, dict):
        sort_out = ["supply_costs", "available_supplies"]
        store_sort_values = []
        print("DICTT", dict)
        for it in sort_out:
            temp = dict.get(it, None)
            if temp == None:
                continue

            store_sort_values.append(dict[it])
            dict.pop(it)

        try:
            reb = cls(**dict)
        except:
            print("ERROR BECAUSE REB CAN't be created")
            raise TypeError

        for sort, value in zip(sort_out, store_sort_values):
            setattr(reb, sort, value)

        return reb

    # Validate then attach units
    # Function parameter description:
    #    - selected_units read the Units class document above
    #    - units_count how many selected_units should be given (will be validated)
    #        example: units_count = 3 when 3 different unit_type should be selected (like from warchoose)
    #        example: units_count = 1 when 1 unit_type sould be selected (like a special unit: nukes, icbms)
    def attach_units(self, selected_units: dict, units_count: int) -> Union[str, None]:
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

                print(units_count, "Csdads")
                units_count -= 1
        except Exception as e:
            print(e)
            return "Not enough unit type selected"

        # If the validation is ended successfully
        else:
            self.selected_units = selected_units
            self.selected_units_list = list(selected_units.keys())

    # Attack with all units contained in selected_units
    def attack(self, attacker_unit: str, target: str) -> Union[str, tuple, None]:
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

    def save(self):

        connection = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"))

        db = connection.cursor()

        for save_type in self.save_for:
            # Save casualties
            if save_type == "casualties":
                # The casualties method sets a suffered_casualties
                for unit_type, amount in self.suffered_casualties.items():

                    mil_statement = f"SELECT {unit_type} FROM military " + " WHERE id=(%s)"
                    db.execute(mil_statement, (self.user_id,))
                    available_unit_amount = db.fetchone()[0]

                    mil_update = f"UPDATE military SET {unit_type}" + "=(%s) WHERE id=(%s)"
                    db.execute(mil_update, (available_unit_amount-amount, self.user_id))

            # Save supplies
            elif save_type == "supplies":
                pass

        connection.commit()

    # Save casualties to the db and check for casualty validity
    # NOTE: to save the data to the db later on put it to the save method
    # unit_type -> name of the unit type, amount -> used to decreate by it
    def casualties(self, unit_type: str, amount: int) -> None:

        connection = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"))

        db = connection.cursor()

        # Make sure this is and integer
        # TODO: optimize this by creating integer at the user side
        amount = int(amount)
        unit_amount = self.selected_units[unit_type]

        if amount > unit_amount:
            amount = unit_amount

        self.selected_units[unit_type] = unit_amount-amount

        # Save records to the database
        mil_statement = f"SELECT {unit_type} FROM military " + " WHERE id=(%s)"
        db.execute(mil_statement, (self.user_id,))
        available_unit_amount = db.fetchone()[0]

        mil_update = f"UPDATE military SET {unit_type}" + "=(%s) WHERE id=(%s)"
        db.execute(mil_update, (available_unit_amount-amount, self.user_id))
        connection.commit()

    def save(self):

        connection = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"))

        db = connection.cursor()

        # Save supplies
        try:
            db.execute("SELECT id FROM wars WHERE (attacker=(%s) OR defender=(%s)) AND peace_date IS NULL", (self.user_id, self.user_id))
            war_id = db.fetchall()[-1][0]
        except:
            return "War is already over!"

        if war_id != None:
            db.execute("SELECT attacker FROM wars WHERE id=(%s)", (war_id,))
            is_attacker = db.fetchone()[0]

            if is_attacker == self.user_id:
                sign = "attacker_supplies"
            else:
                sign = "defender_supplies"

            sign_select = f"SELECT {sign} FROM wars " + " WHERE id=(%s)"
            db.execute(sign_select, (war_id,))
            current_supplies = db.fetchone()[0]

            sign_update = f"UPDATE wars SET {sign}" + "=(%s) WHERE id=(%s)"
            db.execute(sign_update, (current_supplies-self.supply_costs, war_id))

            connection.commit()
        else:
            print("ERROR DURING SAVE")
            return "ERROR DURING SAVE"

    # Fetch the available supplies which compared to unit attack cost and check if user can't pay for it (can't give enought supplies)
    # Also save the remaining morale to the database
    # TODO: decrease the supplies amount in db
    def attack_cost(self, cost: int) -> str:
        if self.available_supplies == None:

            connection = psycopg2.connect(
                database=os.getenv("PG_DATABASE"),
                user=os.getenv("PG_USER"),
                password=os.getenv("PG_PASSWORD"),
                host=os.getenv("PG_HOST"),
                port=os.getenv("PG_PORT"))

            db = connection.cursor()

            print("TRHOW ERROR MAYBE BECAUSE peace_date is set")
            db.execute("SELECT attacker FROM wars WHERE attacker=(%s) AND peace_date IS NULL", (self.user_id,))
            attacker_id = db.fetchone()
            print(attacker_id)

            # If the user is the attacker (maybe optimize this to store the user role in the war)
            if attacker_id:
                db.execute("SELECT attacker_supplies FROM wars WHERE attacker=(%s) AND peace_date IS NULL", (self.user_id,))
                self.available_supplies = db.fetchone()[0]

            # the user is defender
            else:
                db.execute("SELECT defender_supplies FROM wars WHERE defender=(%s) AND peace_date IS NULL", (self.user_id,))
                self.available_supplies = db.fetchone()[0]

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

    p = defender.attach_units({"soldiers": 10, "tanks": 0, "artillery": 0}, 3)

    print(p)

    error = attacker.attach_units({"nukes": 1}, 1)
    if error:
        print(error)

    attacker.special_fight(attacker, defender, "soldiers")
    attacker.save()

    # attacker.infrastructure_damage(1500, {})


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
    # import psycopg2
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
