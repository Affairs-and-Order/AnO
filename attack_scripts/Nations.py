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

    # select only needed units instead of all
    # particular_units must be a list of string unit names
    @staticmethod
    def get_particular_units_list(cId, particular_units):
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
        unit_to_amount_dict['cId'] = allAmounts[0][0]
        unit_to_amount_dict['soldiers'] = allAmounts[0][1]
        unit_to_amount_dict['artillery'] = allAmounts[0][2]
        unit_to_amount_dict['tanks'] = allAmounts[0][3]
        unit_to_amount_dict['bombers'] = allAmounts[0][4]
        unit_to_amount_dict['fighters'] = allAmounts[0][5]
        unit_to_amount_dict['apaches'] = allAmounts[0][6]
        unit_to_amount_dict['spies'] = allAmounts[0][7]
        unit_to_amount_dict['ICBMs'] = allAmounts[0][8]
        unit_to_amount_dict['nukes'] = allAmounts[0][9]
        unit_to_amount_dict['destroyer'] = allAmounts[0][10]
        unit_to_amount_dict['cruisers'] = allAmounts[0][11]
        unit_to_amount_dict['submarines'] = allAmounts[0][12]
        # make a dictionary with 3 keys, listed in the particular_units list
        unit_lst = []
        for unit in particular_units:
            unit_lst.append(unit_to_amount_dict[unit])

        connection.close()
        return unit_lst # this is a list of the format [100, 50, 50]

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

    def fight(self, enemyNation, attackTypes):
        # attackTypes is a tuple
        attackList = ["water", "ground", "air"]
        attackTypesHash = {"water": 1, "ground": 2, "air": 3}

        currentAttacks = list(attackTypes)

        for attack in attackList:
            if attackTypes[0] == attack:
                currentAttacks[0] = attackTypesHash[attack]
            if attackTypes[1] == attack:
                currentAttacks[1] = attackTypesHash[attack]

        # super simple fight between two nations soldiers
        print(attackTypes[1])
        enemyScore = enemyNation.military.soldiers + \
            abs(random.randrange(-2 *
                                 currentAttacks[1], 2 * currentAttacks[1]))
        homeScore = self.military.soldiers + \
            abs(random.randrange(-2 *
                                 currentAttacks[0], 2 * currentAttacks[0]))

        if enemyScore > homeScore:
            print("Enemy Win | ID " + str(enemyNation.id))
            self.losses += 1
            enemyNation.wins += 1
        else:
            print("Home win | ID " + str(self.id))
            enemyNation.losses += 1
            self.wins += 1

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
