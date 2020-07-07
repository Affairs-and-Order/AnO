import random
import sqlite3
import _pickle as pickle
import json
import random

path = "affo/aao.db"


def ping():  # delete this before launch
    print("found game script")


class Military:
    def __init__(self, nationID=None):
        self.units = {
            "soldiers": {"name": "soldiers", "type": "ground", "amount": 0, "damage": 1, "cost": 50, "inBattle": 0},
            "tanks": {"name": "tanks", "type": "ground", "amount": 0, "damage": 3, "cost": 50, "inBattle": 0},
            "artillery": {"name": "artillery", "type": "ground", "amount": 0, "damage": 1, "cost": 50, "inBattle": 0},

            "flying_fortresses": {"name": "flying_fortresses", "type": "air", "amount": 0, "damage": 2, "cost": 50,
                                  "inBattle": 0},
            "fighter_jets": {"name": "fighter_jets", "type": "air", "amount": 0, "damage": 3, "cost": 50,
                             "inBattle": 0},
            "apaches": {"name": "apaches", "type": "air", "amount": 0, "damage": 3, "cost": 50, "inBattle": 0},

            "destroyers": {"name": "destroyers", "type": "water", "amount": 0, "damage": 1, "cost": 50, "inBattle": 0},
            "cruisers": {"name": "cruisers", "type": "water", "amount": 0, "damage": 2, "cost": 50, "inBattle": 0},
            "submarines": {"name": "submarines", "type": "water", "amount": 0, "damage": 3, "cost": 50, "inBattle": 0},

            "ICBMs": {"name": "ICBMs", "type": "special", "amount": 0, "damage": 4, "cost": 50, "inBattle": 0},
            "nukes": {"name": "nukes", "type": "special", "amount": 0, "damage": 4, "cost": 50, "inBattle": 0},
            "spies": {"name": "spies", "type": "special", "amount": 0, "damage": 4, "cost": 50, "inBattle": 0}
        }
        self.nationID = nationID

    # inits the military variables
    def get_military(self):
        connection = sqlite3.connect(path)
        db = connection.cursor()
        i = 0
        for unit in self.units:
            print(self.units[unit]["type"])
            self.units[unit]["amount"] = db.execute(
                f"SELECT {unit} FROM {self.units[unit]['type']} WHERE id={self.nationID}", ())
            # delete this line and uncomment the line below this after the attack system is finished
            # self.units[unit]["inBattle"] = db.execute(f"SELECT {unit} FROM inBattle WHERE id={self.nationID}",()).fetchone()[0]
            i += 1


class Economy:
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
        connection = sqlite3.connect(path)
        db = connection.cursor()
        resourceList = []

        i = 0
        for resou in self.resources:
            self.resources[resou] = db.execute(f"SELECT {self.resourcesNames[i]} FROM resources WHERE id=(?)", (self.nationID,)).fetchone()[0]
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
            db.execute("UPDATE stats SET gold=(?) WHERE id=(?)", ((int(gold) + int(wantedUnits) * int(military.units[requested]["cost"])), military.nationID,))

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

        # needs to be reworked soon
        self.provinceAmount = 12
        self.warList = []
        self.inBattleUnits = []

        self.allies = []

    # increases morale but decreases attack power
    def fortify(self, usedSupplies, unitType, unitAmount, enemyNation):
        connection = sqlite3.connect(path)
        cursor = connection.cursor()

        currentMorale = cursor.execute(f"SELECT morale FROM war WHERE id={self.id}")
        updatedMorale = currentMorale * 1.25
        cursor.execute(f"UPDATE war SET morale={updatedMorale} WHERE id={self.id}")
        # province id

    # activates a turn for a war
    def turn(self, unitType, usedSupplies, Type, attackedProvince, enemyNation):
        connection = sqlite3.connect(path)
        cursor = connection.cursor()

        supplies = cursor.execute(f"SELECT supplies FROM war WHERE id={self.id}").fetchone()[0]

        # if supplies is 200 or more then allow turn
        if supplies >= 200:
            if Type == "defend":
                self.fortify(usedSupplies, unitType, unitAmount, enemyNation)

            if Type == "attack":
                # effectiveness multiplier < 100

                self.inBattleUnits.append(unitType)

                effectiveness = 0.09 * usedSupplies * unitType["damage"]
                provincePopulation = \
                cursor.execute("SELECT population FROM provinces WHERE provinceId=?", (attackedProvince,)).fetchone()[0]
                PopulationLoss = provincePopulation - effectiveness * 10

                cursor.execute(f"UPDATE war SET population={PopulationLoss} WHERE provinceId={attackedProvince})")
                connection.commit()

                currentMorale = cursor.execute(f"SELECT morale FROM war WHERE id={self.id}", ()).fetchone[0]
                updatedMorale = currentMorale - effectiveness

                cursor.execute(f"UPDATE war SET morale ({updatedMorale})", ())
                connection.commit()

        # else return -1
        else:
            return -1
    
    calculateAdvantage = lambda n, m, v, t, e : (n+v) * ((t*e)/10 + m)

    def calculateBattleAdvantage(self):
        # now the variables are out of scope...
        try:
            attackPower = 0
            for unit in self.inBattleUnits:

                attackPower += unit["damage"]
                battleAdvantage = random.random(-1, 1)  # add a very small amount of randomness to the battle, shouldn't cause any major game changing events

                attackerMorale = cursor.execute(f"SELECT morale FROM war WHERE id={self.id}", ()).fetchone()[0]
                defenderMorale = cursor.execute(f"SELECT morale FROM war WHERE id={self.warList[war]}", ()).fetchone()[0]

                techScore = 100  # cursor.execute(f"SELECT techScore FROM war WHERE id={self.foobar}", ()).fetchone()[0]
                defenderTechScore = 100  # cursor.execute(f"SELECT techScore FROM war WHERE id={enemy.foobar}", ()).fetchone()[0]

                if attackerMorale > defenderMorale:
                    battleAdvantage += 1
                else:
                    battleAdvantage -= 1

                if techScore > defenderTechScore:
                    battleAdvantage += 1
                else:
                    battleAdvantage -= 1                



                
                # TODO: add more components that will effect the end battle advantage

                return battleAdvantage



        except Exception as e:
            print("[WARNING] Unable to execute attack: {}".format(e))

    # sets up a war
    def attack(self, unitType, enemyNation):
        if enemyNation.province > self.provinceAmount:
            raise Exception("enemy province number cannot be higher than the attacker's province number!")
        elif len(self.warList) >= 5:
            raise Exception("user can only be in 5 wars at a time")
        else:
            self.warList.append(enemyNation)
            self.inBattleUnits.append(unitType)

            connection = sqlite3.connect(path)
            cursor = connection.cursor()

            # subtracts used units from the database and puts them in the inBattleUnits array
            currentUnitCount = cursor.execute(f"SELECT {unitType['name']} FROM {unitType['type']} WHERE id={self.id}")
            subtractedUnitCount = currentUnitCount - unitType["amount"]
            cursor.execute(
                f"UPDATE {unitType['type']} SET {unitType['name']} VALUES ({subtractedUnitCount}) WHERE id={self.id}")
            connection.commit()

            currentUnits = cursor.execute(f"SELECT {unitType} FROM {unitType['type']} WHERE id={self.id}").fetchone()[0]
            duringAttack = currentUnits - unitAmount

            cursor.execute(f"UPDATE {unitType['type']} SET {unitType} = {duringAttack} WHERE id={self.id}", ())
            cursor.execute(f"INSERT INTO war (id, morale, inBattle, enemy, duration) VALUES ({self.id}, 100, {unitAmount}, {enemyNation.id}, DEFAULT)",())
            totalBattlingUnits = 0
            for unit in self.inBattleUnits:
                totalBattlingUnits += unit["amount"]

            battleAdvantage = self.calculateBattleAdvantage()

    def checkWar(self, war):
        '''checks who is winning a war'''
        # from the perspective of the attacker
        connection = sqlite3.connect(path)
        cursor = connection.cursor()

        """

        Things to add:
        - ongoing global wars in app.py
        - add current war (ie. in Nation.attack) to DB
        
        def attack (unitType, numberOfUnits, enemyNation):
            self.warlist.append(enemyNation.id)

            # it would have to be a dict and we would use JSON to store it to the db

        """

        if attackerMorale == 0:
            return self
        elif attackerMorale > 0 and defenderMorale > 0:
            return 0
        elif defenderMorale == 0:
            a = Economy(self.warList[war])
            b = Military(self.warList[war])

            # the final object
            c = Nation(self.warList[war], b, a)
            return c

    # this saves the nation obj to the database using pickle (in bytes) 
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
