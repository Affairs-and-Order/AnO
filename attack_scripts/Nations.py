import random
import sqlite3

class Military:
    def __init__(self, spies, troops, tanks, artillery, flyingForts, bomberJets, destroyers, cruisers, submarines, ICBMs, nukes):
        self.spies = spies
        self.troops = troops
        self.tanks = tanks
        self.artilley = artillery
        self.flyingForts = flyingForts
        self.bomberJets = bomberJets
        self.destroyers = destroyers
        self.cruisers = cruisers
        self.submarines = submarines
        self.ICMBs = ICBMs
        self.nukes = nukes        

class Economy:
    # TODO: expand this to cover all resources
    def __init__(self, nationID, gold):
        self.gold = gold

    def get_economy(self):
        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        # TODO fix this when the databases changes and update to include all resources
        self.gold = db.execute('SELECT gold FROM stats WHERE id=($), (nationID,)').fetchone()[0]

class Nation:
    def __init__(self, nationID, military, economy):
        # self = self
        self.id = nationID # integer ID
        
        self.military = military
        self.economy = economy

        self.wins = 0
        self.losses = 0


    def fight(self, enemyNation, attackTypes):

        attackTypes = {"water": 0.5 ,"ground": 1 ,"air": 0.75}
        for attack in attackTypes:
            if attackTypes[0] == attack:
                attackTypes[0] = attack
            if attackTypes[1] == attack:
                attackTypes[1] = attack


        # super simple fight between two nations troops
        enemyScore = enemyNation.military.troops + random.randint(-2 * attackTypes[1], 2 * attackTypes[1])
        homeScore = self.military.troops + random.randint(-2 * attackTypes[0], 2 * attackTypes[0])

        if enemyScore > homeScore:
            print("Enemy Win | ID " + str(enemyNation.id))
            self.losses += 1
            enemyNation.wins += 1
        else:
            print("Home win | ID " + str(self.id))
            enemyNation.losses += 1
            self.wins += 1

    def printStatistics (self):
        print("Nation {}:\nWins {}\nLosses: {}".format(self.id, self.wins, self.losses))

# temporary definitions for nations economy and military
nat1M = Military(0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0)
nat1E = Economy(0)
# create nation1
nation1 = Nation(1, nat1M, nat1E)


# temporary definitions for nations economy and military
nat2M = Military(0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0)
nat2E = Economy(0)
# create nation1
nation2 = Nation(2, nat2M, nat2E)

if __name__ == "__main__":
    for i in range(0, 3):
        nation1.fight(nation2)

    nation1.printStatistics()
    nation2.printStatistics()
