# FULLY MIGRATED

from abc import ABC, abstractmethod
from attack_scripts import Military
from math import floor, ceil
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
        - resource_cost: the required resources per x amount unit to be able to attack
            ex. {"ammunition": 1} <- means 1 ammunition is needed for one unit to attack
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
    resource_cost = {"ammunition": 1}

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
    resource_cost = {"ammunition": 1, "gasoline": 1}

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
    resource_cost = {"ammunition": 2}

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
    resource_cost = {"ammunition": 2, "gasoline": 2}

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
    resource_cost = {"ammunition": 2, "gasoline": 2}

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
    resource_cost = {"ammunition": 2, "gasoline": 2}

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
    resource_cost = {"ammunition": 2, "gasoline": 2}

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
    resource_cost = {"ammunition": 2, "gasoline": 2}

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
    resource_cost = {"ammunition": 2, "gasoline": 2}

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
    supply_cost = 500

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
    supply_cost = 1000

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

    def __init__(self, user_id, selected_units: dict=None, bonuses: int=None, selected_units_list: list=None, war_id=None):
        self.user_id = user_id
        self.selected_units = selected_units
        self.bonuses = bonuses
        self.supply_costs = 0
        self.available_supplies = None
        self.war_id = war_id

        # selected_units_list is needed at: Nations.py/Military->fight();
        # a list of selected_units keys
        self.selected_units_list = selected_units_list

    # this is needed because we can't store object in server side cache :(
    @classmethod
    def rebuild_from_dict(cls, sess_dict):

        # if you modify the sess_dict it'll affect the actual session, that is why I recomend to create a copy
        dic = dict(sess_dict)
        sort_out = ["supply_costs", "available_supplies"]
        store_sort_values = []

        for it in sort_out:
            temp = dic.get(it, None)
            if temp is None:
                continue

            store_sort_values.append(dic[it])
            dic.pop(it)

        try:
            reb = cls(**dic)
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
        self.supply_costs = 0
        unit_types = list(selected_units.keys())
        normal_units = self.get_military(self.user_id)
        special_units = self.get_special(self.user_id)

        available_units = normal_units.copy()
        available_units.update(special_units)

        try:
            while units_count:
                current_unit = unit_types[units_count-1]
                if current_unit not in self.allUnits:
                    return "Invalid unit type!"

                if (selected_units[current_unit] > available_units[current_unit]) or (selected_units[current_unit] < 0) :
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

                    if unit_amount is None:
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
        amount = int(floor(amount))
        # print("LOSS AMOUNT", self.user_id, unit_type, amount)
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

        if war_id is not None:
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

    # Fetch the available supplies and resources which are required and compare it to unit attack cost
    # It also saves the remaining morale to the database
    def attack_cost(self, cost: int) -> str:
        if self.available_supplies is None:
            connection = psycopg2.connect(
                database=os.getenv("PG_DATABASE"),
                user=os.getenv("PG_USER"),
                password=os.getenv("PG_PASSWORD"),
                host=os.getenv("PG_HOST"),
                port=os.getenv("PG_PORT"))
            db = connection.cursor()

            db.execute("SELECT attacker FROM wars WHERE id=(%s)", (self.war_id,))
            attacker_id = db.fetchone()

            # If the user is the attacker (maybe optimize this to store the user role in the war)
            if attacker_id:
                db.execute("SELECT attacker_supplies FROM wars WHERE id=(%s)", (self.war_id,))
                self.available_supplies = db.fetchone()[0]

            # the user is defender
            else:
                db.execute("SELECT defender_supplies FROM wars WHERE id=(%s)", (self.war_id,))
                self.available_supplies = db.fetchone()[0]

        if self.available_supplies < 200:
            return "The minimum supply amount is 200"

        self.supply_costs += cost
        if self.supply_costs > self.available_supplies:
            return "Not enough supplies available"

# DEBUGGING
if __name__ == "__main__":
    attacker = 2
    defender = 5
    war_id = 666

    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))
    db = connection.cursor()
    import time

    db.execute(f"INSERT INTO wars VALUES ({war_id},{attacker},{defender},'Raze','falas message',NULL,{time.time()},2000,2000,{time.time()}, 100, 100)")
    connection.commit()

    attack_units = Units(attacker, war_id=war_id, selected_units_list=["soldiers", "cruisers", "tanks"],
    selected_units={"soldiers": 1000, "cruisers": 100, "tanks": 50})

    defender_units = Units(defender, {
    "tanks": 544,
    "soldiers": 64,
    "artillery": 55
    }, selected_units_list=["tanks", "soldiers", "artillery"])

    # defender_units = Units(defender, {
    # "tanks": 0,
    # "soldiers": 0,
    # "artillery": 0
    # }, selected_units_list=["tanks", "soldiers", "artillery"])

    print(Military.fight(attack_units, defender_units))

    db.execute(f"DELETE FROM wars WHERE id={war_id}")
    connection.commit()
    connection.close()
