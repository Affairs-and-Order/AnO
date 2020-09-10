import random
import sqlite3
import os

path = "C:\\Users\\elefant\\Affairs-and-Order\\affo\\aao.db"


class Military:
    def __init__(self, spies, soldiers, tanks, artillery, bombers, fighters, destroyers, cruisers, submarines, ICBMs, nukes):
        self.spies = spies
        self.soldiers = soldiers
        self.tanks = tanks
        self.artilley = artillery
        self.bombers = bombers
        self.fighters = fighters  # was bomberJets
        self.destroyers = destroyers
        self.cruisers = cruisers
        self.submarines = submarines
        self.ICMBs = ICBMs
        self.nukes = nukes

    # NOTICE: in the future we could use this as an instance method unstead of static method
    @staticmethod
    def fight(attacker, defender): # dictionary in format {'unit': amount, 'unit': amount, 'unit': amount}

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
            defender_unit_amount_bonuses += defender.selected_units[defender_unit]*10/1000
            attacker_unit_amount_bonuses += attacker.selected_units[attacker_unit]*10/1000

            # Compare attacker agains defender
            for unit in defender.selected_units_list:
                attacker_bonus += attacker.attack(attacker_unit, unit, defender)[1]

            # Compare defender against attacker
            for unit in attacker.selected_units_list:
                defender_bonus += defender.attack(defender_unit, unit, attacker)[1]

        attacker_chance += attacker_roll+attacker_unit_amount_bonuses+attacker_bonus
        defender_chance += defender_roll+defender_unit_amount_bonuses+defender_bonus

        # Determine the winner
        if defender_chance >= attacker_chance:
            winner = defender
            win_type = defender_chance//attacker_chance

        else:
            winner = attacker
            win_type = attacker_chance//defender_chance

        # annihilation
        if win_type >= 3:
            winner

        # definite victory
        elif win_type >= 2: pass

        # close victory
        else: pass

        # DEBUGGING:
        # print(attacker_unit_amount_bonuses, defender_unit_amount_bonuses)
        # print(attacker_roll, defender_roll)
        # print(attacker_bonus, defender_bonus)
        # print(attacker_chance, defender_chance)

    # select only needed units instead of all
    @staticmethod
    def get_particular_unit(cId, particular_units):
        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()
        units = {}
        for unit in particular_units:

            # IMPORTANT: This is SQL injectable change this when move to production
            units[unit] = db.execute(f"SELECT {unit} FROM military WHERE id=(?)", (cId,)).fetchone()[0]

        connection.close()
        return units

    @staticmethod
    def get_military(cId):
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
    def get_special(cId):
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

    # @staticmethod
    # def get_default_defense(cId):
    #     connection = sqlite3.connect('affo/aao.db')
    #     db = connection.cursor()
    #     default_defense = db.execute("SELECT default_defense FROM nation WHERE nation_id=(?)", (1,)).fetchall()
    #     connection.close()

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
    n = Nation(3, None, None)
    n.get_provinces()
    print(n.provinces)

    n.get_current_wars()

    # # temporary definitions for nations economy and military
    # nat1M = Military(0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    # nat1E = Economy(2).get_economy()
    # # create nation1
    # nation1 = Nation(1, nat1M, nat1E)
    #
    # # temporary definitions for nations economy and military
    # nat2M = Military(0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    # nat2E = Economy(0)
    # # create nation1
    # nation2 = Nation(2, nat2M, nat2E)
    #
    # for i in range(0, 3):
    #     nation1.fight(nation2, ("water", "air"))
    #
    # nation1.printStatistics()
    # nation2.printStatistics()
