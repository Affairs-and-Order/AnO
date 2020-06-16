import random
import sqlite3
import _pickle as pickle

path = "affo/aao.db"


def ping():  # delete this before launch
    print("found game script")

class Military:
    def __init__(self, nationID=None):
        # getting kind of big, might want to move to db
        self.units = {
            "soldiers": {"type": "ground", "amount": 0, "damage": 1, "cost": 50, "inBattle": 0},
            "tanks": {"type": "ground", "amount": 0, "damage": 3, "cost": 50, "inBattle": 0},
            "artillery": {"type": "ground", "amount": 0, "damage": 1, "cost": 50, "inBattle": 0},

            "flying_fortresses": {"type": "air", "amount": 0, "damage": 2, "cost": 50, "inBattle": 0},
            "fighter_jets": {"type": "air", "amount": 0, "damage": 3, "cost": 50, "inBattle": 0},
            "apaches": {"type": "air", "amount": 0, "damage": 3, "cost": 50, "inBattle": 0},

            "destroyers": {"type": "water", "amount": 0, "damage": 1, "cost": 50, "inBattle": 0},
            "cruisers": {"type": "water", "amount": 0, "damage": 2, "cost": 50, "inBattle": 0},
            "submarines": {"type": "water", "amount": 0, "damage": 3, "cost": 50, "inBattle": 0},

            "ICBMs": {"type": "special", "amount": 0, "damage": 4, "cost": 50, "inBattle": 0},
            "nukes": {"type": "special", "amount": 0, "damage": 4, "cost": 50, "inBattle": 0},
            "spies": {"type": "special", "amount": 0, "damage": 4, "cost": 50, "inBattle": 0}
        }
        self.nationID = nationID

    # inits the military variables
    def get_military(self):
        connection = sqlite3.connect(path)
        db = connection.cursor()
        i = 0
        for unit in self.units:
            print(self.units[unit]["type"])
            self.units[unit]["amount"] = db.execute(f"SELECT {unit} FROM {self.units[unit]['type']} WHERE id={self.nationID}",())
            # delete this line and uncomment the line below this after the attack system is finished
            #self.units[unit]["inBattle"] = db.execute(f"SELECT {unit} FROM inBattle WHERE id={self.nationID}",()).fetchone()[0]
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

        self.provinceAmount = 12
        self.warList = []

    # currently reworking this
    def attack(self, category, unitType, unitAmount, enemyNation):
        if enemyNation.province > self.provinceAmount:
            raise Exception("enemy province number cannot be higher than the attacker's province number!")
        else:
            self.warList.append(enemyNation)
            connection = sqlite3.connect(path)
            cursor = connection.cursor()

            currentUnits = cursor.execute(f"SELECT {unitType} FROM {unitType['type']} WHERE id={self.id}").fetchone()[0]
            duringAttack = currentUnits - unitAmount

            cursor.execute(f"UPDATE {unitType['type']} SET {unitType} = {duringAttack} WHERE id={self.id}", ())
            cursor.execute(f"INSERT INTO war (id, morale, inBattle, enemy, duration) VALUES ({self.id}, 100, {unitAmount}, {enemyNation.id}, 0)", ())


    def checkWar(self, war):
        connection = sqlite3.connect(path)
        cursor = connection.cursor()

        attackerMorale = cursor.execute(f"SELECT morale FROM war WHERE id={self.id}", ()).fetchone()[0]
        defenderMorale = cursor.execute(f"SELECT morale FROM war WHERE id={self.warList[war]}", ()).fetchone()[0]

        if attackerMorale == 0:
            return self
        elif attackerMorale > 0 and defenderMorale > 0:
            return 0
        elif defenderMorale == 0:
            a = Economy(self.warList[war])
            b = Military(self.warList[war])
            c = Nation(self.warList[war], b, a)
            return c

    def saveToDB(self):
        connection = sqlite3.connect(path)
        cursor = connection.cursor()

        nationObject = pickle.dump(self)
        cursor.execute(f"INSERT INTO users (nation) VALUES ({nationObject})")
        print(f"saved object to database for user {self.id}")
        return 1

    def loadFromDB(self):

        connection = sqlite3.connect(path)
        cursor = connection.cursor()

        nationObject = pickle.load(cursor.execute(f"SELECT nation FROM users WHERE id={self.id}"))