import random
import sqlite3
import os

path = "C:\\Users\\elefant\\Affairs-and-Order\\affo\\aao.db"

def calculate_bonuses(attack_effects, enemy_object, target): # int, Units, str -> int
    # Calculate the percentage of total units will be affected
    defending_unit_amount = enemy_object.selected_units[target]

    # sum of units amount
    enemy_units_total_amount = sum(enemy_object.selected_units.values())

    # the affected percentage from sum of units
    unit_of_army = (defending_unit_amount*100)/enemy_units_total_amount

    # the bonus calculated based on affected percentage
    affected_bonus = attack_effects[1]*(unit_of_army/100)

    # divide affected_bonus to make bonus effect less relevant
    attack_effects = affected_bonus/100

    # DEBUGGING:
    # print("UOA", unit_of_army, attacker_unit, target, self.user_id, affected_bonus)
    return attack_effects

# there are no instances of base class Military
class Military:
    allUnits = ["soldiers", "tanks", "artillery",
                "bombers", "fighters", "apaches",
                "destroyers", "cruisers", "submarines",
                "spies", "icbms", "nukes"]
    @staticmethod
    def special_fight(attacker, defender, target): # Units, Units, int -> str, None
        target_amount = defender.get_military(defender.user_id).get(target, None)

        if target_amount != None:
            special_unit = attacker.selected_units_list[0]
            attack_effects = attacker.attack(special_unit, target)

            # Surely destroy this percentage of the targeted units
            min_destruction = target_amount*(1/5)*(attack_effects[0]*attacker.selected_units[special_unit])

            # Random bonus on unit destruction
            destruction_rate = random.uniform(1, 2)

            final_destruction = destruction_rate*min_destruction

        else:
            return "Invalid target is selected!"

    # NOTICE: in the future we could use this as an instance method unstead of static method
    '''
    This is already checked in the Military->fight
    if your score is higher by 3x, annihilation,
    if your score is higher by 2x, definite victory
    if your score is higher, close victory,
    if your score is lower, close defeat, 0 damage,
    if your score is lower by 2x, massive defeat, 0 damage

    from annihilation (resource, field, city, depth, blockade, air):
    soldiers: resource control
    tanks: field control and city control
    artillery: field control
    destroyers: naval blockade
    cruisers: naval blockade
    submarines: depth control
    bombers: field control
    apaches: city control
    fighter jets: air control

    counters | countered by
    soldiers beat artillery, apaches | tanks, bombers
    tanks beat soldiers | artilllery, bombers
    artillery beat tanks | soldiers
    destroyers beat submarines | cruisers, bombers
    cruisers beat destroyers, fighters, apaches | submarines
    submarines beat cruisers | destroyers, bombers
    bombers beat soldiers, tanks, destroyers, submarines | fighters, apaches
    apaches beat soldiers, tanks, bombers, fighters | soldiers
    fighters beat bombers | apaches, cruisers

    resource control: soldiers can now loot enemy munitions (minimum between 1 per 100 soldiers and 50% of their total munitions)
    field control: soldiers gain 2x power
    city control: 2x morale damage
    depth control: missile defenses go from 50% to 20% and nuke defenses go from  35% to 10%
    blockade: enemy can no longer trade
    air control: enemy bomber power reduced by 60%'''
    @staticmethod
    def fight(attacker, defender): # Units, Units -> int

        attacker_roll = random.uniform(0, 10)
        attacker_chance = 0
        attacker_unit_amount_bonuses = 0
        attacker_bonus = 0

        defender_roll = random.uniform(0, 10)
        defender_chance = 0
        defender_unit_amount_bonuses = 0
        defender_bonus = 0

        for attacker_unit, defender_unit in zip(attacker.selected_units_list, defender.selected_units_list):

            # Unit amount chance - this way still get bonuses even if no counter unit_type
            defender_unit_amount_bonuses += defender.selected_units[defender_unit]/100 # is dict
            attacker_unit_amount_bonuses += attacker.selected_units[attacker_unit]/100

            # Compare attacker agains defender
            for unit in defender.selected_units_list:
                attacker_bonus += calculate_bonuses(attacker.attack(attacker_unit, unit), defender, unit)
                # used to be += attacker.attack(attacker_unit, unit, defender)[1]


            # Compare defender against attacker
            for unit in attacker.selected_units_list:
                defender_bonus += calculate_bonuses(defender.attack(defender_unit, unit), attacker, unit)

        attacker_chance += attacker_roll+attacker_unit_amount_bonuses+attacker_bonus
        defender_chance += defender_roll+defender_unit_amount_bonuses+defender_bonus

        # Determine the winner
        if defender_chance >= attacker_chance:
            winner = defender
            loser = attacker
            win_type = defender_chance//attacker_chance
            winner_casulties = attacker_chance//defender_chance

        else:
            winner = attacker
            loser = defender
            win_type = attacker_chance//defender_chance
            winner_casulties = defender_chance//attacker_chance

        # Effects based on win_type (idk: destroy buildings or something)
        # loser_casulties = win_type so win_type also is the loser's casulties

        # annihilation
        if win_type >= 3: pass

        # definite victory
        elif win_type >= 2: pass

        # close victory
        else: pass

        # Maybe use the damage property also in unit loss
        # TODO: make unit loss more precise
        for winner_unit, loser_unit in zip(winner.selected_units_list, loser.selected_units_list):
            winner.casualties(winner_unit, winner_casulties*random.uniform(0.8, 1))
            loser.casualties(loser_unit, win_type*6*random.uniform(0.8, 1))

        return winner.user_id

        # DEBUGGING:
        # print("WINNER IS:", winner.user_id)
        # print(winner_casulties, win_type)
        # print(attacker_unit_amount_bonuses, defender_unit_amount_bonuses)
        # print(attacker_roll, defender_roll)
        # print(attacker_bonus, defender_bonus)
        # print(attacker_chance, defender_chance)

    # select only needed units instead of all
    # particular_units must be a list of string unit names
    @staticmethod
    def get_particular_units_list(cId, particular_units): # int, list -> list
        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        # for unit in particular_units:

        #     # IMPORTANT: This is SQL injectable change this when move to production
        #     units[unit] = db.execute(f"SELECT {unit} FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        # non sql injectable workaround to above commented code:

        # this data come in the format [(cId, soldiers, artillery, tanks, bombers, fighters, apaches, spies, ICBMs, nukes, destroyer, cruisers, submarines)]
        allAmounts = db.execute(
            "SELECT * FROM military WHERE id=(?)", (cId,)).fetchall()
        # get the unit amounts based on the selected_units
        unit_to_amount_dict = {}
        cidunits = ['cId','soldiers', 'artillery', 'tanks','bombers','fighters','apaches', 'spies','ICBMs','nukes','destroyer','cruisers','submarines']
        for count, item in enumerate(cidunits):
            unit_to_amount_dict[item] = allAmounts[0][count]
        print(unit_to_amount_dict)
        # make a dictionary with 3 keys, listed in the particular_units list
        unit_lst = []
        for unit in particular_units:
            unit_lst.append(unit_to_amount_dict[unit])

        connection.close()
        return unit_lst # this is a list of the format [100, 50, 50]

    @staticmethod
    def get_military(cId): # int -> dict
        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()
        tanks = db.execute(
            "SELECT tanks FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        soldiers = db.execute(
            "SELECT soldiers FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        artillery = db.execute(
            "SELECT artillery FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        bombers = db.execute(
            "SELECT bombers FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        fighters = db.execute(
            "SELECT fighters FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        apaches = db.execute(
            "SELECT apaches FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        destroyers = db.execute(
            "SELECT destroyers FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        cruisers = db.execute(
            "SELECT cruisers FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        submarines = db.execute(
            "SELECT submarines FROM military WHERE id=(?)", (cId,)).fetchone()[0]

        connection.close()

        return {
            "tanks": tanks,
            "soldiers": soldiers,
            "artillery": artillery,
            "bombers": bombers,
            "fighters": fighters,
            "apaches": apaches,
            "destroyers": destroyers,
            "cruisers": cruisers,
            "submarines": submarines
        }

    @staticmethod
    def get_special(cId): # int -> dict
        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()
        spies = db.execute(
            "SELECT spies FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        icbms = db.execute(
            "SELECT ICBMs FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        nukes = db.execute(
            "SELECT nukes FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        connection.close()

        return {
            "spies": spies,
            "icbms": icbms,
            "nukes": nukes
        }

    # Check and set default_defense in nation table
    def set_defense(self, defense_string): # str -> None
        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()
        defense_list = defense_string.split(",")
        if len(defense_units) == 3:

            # default_defense is stored in the db: 'unit1,unit2,unit3'
            defense_units = ",".join(defense_units)

            db.execute("UPDATE nation SET default_defense=(?) WHERE nation_id=(?)", (defense_units, nation[1]))
            connection.commit()
        else:
            # user should never reach here, msg for beta testers
            return "Invalid number of units given to set_defense, report to admin"

class Economy:
    # TODO: expand this to cover all resources
    def __init__(self, nationID):
        self.nationID = nationID

    def get_economy(self):
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, '/affo/aao.db')
        print(filename)
        # TODO find a way to get the database to work on relative directories
        connection = sqlite3.connect(path)
        db = connection.cursor()

        # TODO fix this when the databases changes and update to include all resources
        self.gold = db.execute(
            "SELECT gold FROM stats WHERE id=(?)", (self.nationID,)).fetchone()[0]

    def grant_resources(self, resource, amount):
        # TODO find a way to get the database to work on relative directories
        connection = sqlite3.connect(path)
        db = connection.cursor()
        db.execute("UPDATE stats SET (?) = (?) WHERE id(?)",
                   (resource, amount, self.nationID))

        connection.commit()

    def transfer_resources(self, resource, amount, destinationID):
        # TODO find a way to get the database to work on relative directories
        connection = sqlite3.connect(path)
        db = connection.cursor()

        # get amount of resource
        originalUser = db.execute(
            "SELECT (?) FROM stats WHERE id=(?)", (resource, self.nationID)).fetchone()[0]
        destinationUser = db.execute(
            "SELECT (?) FROM stats WHERE id=(?)", (resource, destinationID)).fetchone()[0]

        # subtracts the resource from one nation to another
        originalUser -= amount
        destinationUser += amount

        # writes changes in db
        db.execute("UPDATE stats SET (?) = (?) WHERE id=(?)",
                   (resource, originalUser, self.nationID))
        db.execute("UPDATE stats SET (?) = (?) WHERE id(?)",
                   (resource, destinationUser, destinationID))

        connection.commit()



class Nation:

    # TODO: someone should update this docs -- marter
    """
    Description of properties:

        If values aren't passed to the parameters then should fetch from the database

        - nationID: represents the nation identifier, type: integer
        - military: represents the ...., type: unknown
        - economy: re...., type:
        - provinces: represents the provinces that belongs to the nation, type: dictionary
          -- structure: provinces_number -> number of provinces, type: integer
                        provinces_stats -> the actual information about the provinces, type: dictionary -> provinceId, type: integer
    """

    def __init__(self, nationID, military=None, economy=None, provinces=None, current_wars=None):
        self.id = nationID  # integer ID

        self.military = military
        self.economy = economy
        self.provinces = provinces

        self.current_wars = current_wars
        self.wins = 0
        self.losses = 0

        # Database management
        # TODO: find a more effective way to handle database stuff
        path = ''.join(
            [os.path.abspath('').split("AnO")[0], 'AnO/affo/aao.db'])
        self.connection = sqlite3.connect(path)
        self.db = self.connection.cursor()

    def declare_war(self, target_nation):
        pass

    def get_provinces(self):
        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()
        if self.provinces == None:
            self.provinces = {"provinces_number": 0, "province_stats": {}}
            provinces_number = self.db.execute(
                "SELECT COUNT(provinceName) FROM provinces WHERE userId=(?)", (self.id,)).fetchone()[0]
            self.provinces["provinces_number"] = provinces_number

            if provinces_number > 0:
                provinces = db.execute(
                    "SELECT * FROM provinces WHERE userId=(?)", (self.id,)).fetchall()
                for province in provinces:
                    self.provinces["province_stats"][province[1]] = {
                        "userId": province[0],
                        "provinceName": province[2],
                        "cityCount": province[3],
                        "land": province[4],
                        "population": province[5],
                        "energy": province[6],
                        "pollution": province[7]
                    }

        return self.provinces

    def get_current_wars(self):
        id_list = self.db.execute(
            "SELECT attacker, defender FROM wars WHERE attacker=(?) OR defender=(?)", (self.id, self.id,)).fetchall()
        print(id_list)

    def printStatistics(self):
        print("Nation {}:\nWins {}\nLosses: {}".format(
            self.id, self.wins, self.losses))


# DEBUGGING:
if __name__ == "__main__":
    pass
