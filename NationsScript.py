import random
import sqlite3
import os

path = "affo/aao.db"


def ping():  # delete this before launch
    print("found nations script")


class Military:
    def __init__(self, nationID=None):
        # getting kind of big, might want to move to db
        self.units = {
            "spies": {"type": "ground", "amount": 0, "damage": 1, "cost": 50, "inBattle": 0},
            "troops": {"type": "ground", "amount": 0, "damage": 2, "cost": 50, "inBattle": 0},
            "tanks": {"type": "ground", "amount": 0, "damage": 3, "cost": 50, "inBattle": 0},
            "artillery": {"type": "ground", "amount": 0, "damage": 1, "cost": 50, "inBattle": 0},
            "flyingForts": {"type": "air", "amount": 0, "damage": 2, "cost": 50, "inBattle": 0},
            "bomberJets": {"type": "air", "amount": 0, "damage": 3, "cost": 50, "inBattle": 0},
            "destroyers": {"type": "water", "amount": 0, "damage": 1, "cost": 50, "inBattle": 0},
            "cruisers": {"type": "water", "amount": 0, "damage": 2, "cost": 50, "inBattle": 0},
            "submarines": {"type": "water", "amount": 0, "damage": 3, "cost": 50, "inBattle": 0},
            "ICMBs": {"type": "special", "amount": 0, "damage": 4, "cost": 50, "inBattle": 0},
            "nukes": {"type": "special", "amount": 0, "damage": 4, "cost": 50, "inBattle": 0}
        }
        self.nationID = nationID

    # inits the military variables
    def get_military(self):
        connection = sqlite3.connect(path)
        db = connection.cursor()
        i = 0
        for unit in self.units:
            self.units[unit]["amount"] = db.execute("SELECT (?) FROM (?) WHERE id=(?)", (
            self.units.keys()[i], self.units[unit]["type"], self.nationID,)).fetchone()[0]
            self.units[unit]["inBattle"] = \
            db.execute("SELECT (?) FROM inBattle WHERE id=(?)", (self.units.keys()[i], self.nationID)).fetchone()[0]
            i += 1


class Economy:
    # TODO: expand this to cover all resources
    def __init__(self, nationID):
        self.nationID = nationID

        self.resources = {
            "gold": 0,
            "plutonium": 0,
            "consumer_goods": 0,
            "uranium": 0,
            "iron": 0,
            "coal": 0,
            "coal": 0,
            "oil": 0,
            "lead": 0,
            "ilicon": 0,
            "copper": 0,
            "bauxite": 0,
        }

        self.resourcesNames = ["gold", "plutonium", "consumer_goods", "uranium", "iron", "coal", "coal", "oil", "lead",
                               "ilicon", "copper", "bauxite"]

    def get_economy(self):
        # TODO find a way to get the database to work on relative directories
        connection = sqlite3.connect(path)
        db = connection.cursor()
        resourceList = []

        # TODO fix this when the databases changes and update to include all resources
        i = 0
        for resou in self.resources:
            self.resources[resou] = \
            db.execute(f"SELECT {self.resourcesNames[i]} FROM resources WHERE id=(?)", (self.nationID,)).fetchone()[0]
            resourceList.append(self.resources[resou])
            i += 1

        return resourceList

    # doesnt work at the moment, do not use
    def buy_sell(self, way, requested, military):

        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        gold = db.execute("SELECT gold FROM stats WHERE id=(?)", (military.nationID,)).fetchone()[0]
        wantedUnits = military.units[requested]
        curUnStat = f'SELECT {military.units[requested]} FROM {military.units[requested]["type"]} WHERE id=?'
        totalPrice = int(wantedUnits) * military.units[requested]["cost"]
        currentUnits = db.execute(curUnStat, (military.nationID,)).fetchone()[0]

        if way == "sell":

            unitUpd = f"UPDATE {military.units[requested]['type']} SET {military.units[requested]}=(?) WHERE id=(?)"
            db.execute(unitUpd, (int(currentUnits) - int(wantedUnits), military.nationID))
            db.execute("UPDATE stats SET gold=(?) WHERE id=(?)",
                       ((int(gold) + int(wantedUnits) * int(military.units[requested]["cost"])), military.nationID,))  # clean

        elif way == "buy":
            db.execute("UPDATE stats SET gold=(?) WHERE id=(?)", (int(gold) - int(totalPrice), military.nationID,))
            updStat = f"UPDATE {military.units[requested]['type']} SET {military.units[requested]}=(?) WHERE id=(?)"
            db.execute(updStat, ((int(currentUnits) + int(wantedUnits)), military.nationID))  # fix weird table

    def grant_resources(self, resource, amount):
        connection = sqlite3.connect(path)  # TODO find a way to get the database to work on relative directories
        db = connection.cursor()

        currentResource = db.execute(f"SELECT {resource} FROM resources WHERE id=(?)", (self.nationID,)).fetchone()[0]
        db.execute(f"UPDATE resources SET {resource} = (?) WHERE id=(?)", (currentResource + amount, self.nationID))

        connection.commit()

    def transfer_resources(self, resource, amount, destinationID):
        connection = sqlite3.connect(path)  # TODO find a way to get the database to work on relative directories
        db = connection.cursor()

        # get amount of resource
        originalUser = db.execute(f"SELECT {resource} FROM stats WHERE id=(?)", (self.nationID)).fetchone()[0]
        destinationUser = db.execute(f"SELECT {resource} FROM stats WHERE id=(?)", (destinationID)).fetchone()[0]

        # subtracts the resource from one nation to another
        originalUser -= amount
        destinationUser += amount

        # writes changes in db
        db.execute(f"UPDATE stats SET {resource} = (?) WHERE id=(?)", (originalUser, self.nationID))
        db.execute(f"UPDATE stats SET {resource} = (?) WHERE id(?)", (destinationUser, destinationID))

        connection.commit()


class Nation:
    def __init__(self, nationID, military, economy):
        # self = self
        self.id = nationID  # integer ID

        self.military = military
        self.economy = economy

        self.wins = 0
        self.losses = 0

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

        # super simple fight between two nations troops
        print(attackTypes[1])
        enemyScore = enemyNation.military.troops + abs(random.randrange(-2 * currentAttacks[1], 2 * currentAttacks[1]))
        homeScore = self.military.troops + abs(random.randrange(-2 * currentAttacks[0], 2 * currentAttacks[0]))

        if enemyScore > homeScore:
            print("Enemy Win | ID " + str(enemyNation.id))
            self.losses += 1
            enemyNation.wins += 1
        else:
            print("Home win | ID " + str(self.id))
            enemyNation.losses += 1
            self.wins += 1

    def printStatistics(self):
        print("Nation {}:\nWins {}\nLosses: {}".format(self.id, self.wins, self.losses))


carsonsEconomy = Economy(1)
carsonsEconomy.get_economy()
carsonsEconomy.grant_resources("gold", 20)
# carsonsEconomy.get_economy()
