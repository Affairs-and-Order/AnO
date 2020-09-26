import random
import sqlite3
import os, time

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

    public_works = ["libraries", "universities", "hospitals", "city_parks", "monorails"]

    # Database management
    # TODO: find a more effective way to handle database stuff
    path = ''.join([os.path.abspath('').split("AnO")[0], 'AnO/affo/aao.db'])
    connection = sqlite3.connect(path)
    db = connection.cursor()

    def __init__(self, nationID, military=None, economy=None, provinces=None, current_wars=None):
        self.id = nationID  # integer ID

        self.military = military
        self.economy = economy
        self.provinces = provinces

        self.current_wars = current_wars
        self.wins = 0
        self.losses = 0

    def declare_war(self, target_nation):
        pass

    def get_provinces(self):
        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()
        if self.provinces == None:
            self.provinces = {"provinces_number": 0, "province_stats": {}}
            provinces_number = db.execute(
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
        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()
        id_list = db.execute(
            "SELECT attacker, defender FROM wars WHERE attacker=(?) OR defender=(?)", (self.id, self.id,)).fetchall()
        print(id_list)

    def printStatistics(self):
        print("Nation {}:\nWins {}\nLosses: {}".format(
            self.id, self.wins, self.losses))

    # Get everything from proInfra table which is in the "public works" category
    @classmethod
    def get_public_works(self, province_id):
        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()
        public_works_string = ",".join(self.public_works)
        fetch_public = db.execute(f"SELECT {public_works_string} FROM proInfra WHERE id=(?)", (province_id,)).fetchone()
        public_works_dict = {}

        for public in range(0, len(self.public_works)):
            public_works_dict[self.public_works[public]] = fetch_public[public]

        return public_works_dict

    # set the peace_date in wars table for a particular war
    @staticmethod
    def set_peace(db, connection, war_id):
        db.execute("UPDATE wars SET peace_date=(?) WHERE id=(?)", (time.time(), war_id))
        connection.commit()

class Military(Nation):
    allUnits = ["soldiers", "tanks", "artillery",
                "bombers", "fighters", "apaches",
                "destroyers", "cruisers", "submarines",
                "spies", "icbms", "nukes"]

    # description of the function: deal damage to random buildings based on particular_infra
    # particular_infra parameter example: for public_works -> {"libraries": 3, "hospitals": x, etc.}
    # note: also could use this for population damage when attack happens
    @staticmethod
    def infrastructure_damage(damage, particular_infra, province_id):
        available_buildings = []

        connection = sqlite3.connect("affo/aao.db")
        db = connection.cursor()

        for building in particular_infra.keys():
            amount = particular_infra[building]
            if amount > 0:

                # If there are multiple of the same building add those multiple times
                for i in range(0, amount):
                    available_buildings.append(building)

        # Damage logic (even include population damage)
        # health is the damage required to destroy a building
        health = 1500

        damage_effects = {}

        while damage > 0:
            if not len(available_buildings):
                break

            max_range = len(available_buildings)-1
            random_building = random.randint(0, max_range)

            target = available_buildings[random_building]

            # destroy target
            if (damage-health) >= 0:
                particular_infra[target] -= 1

                db.execute(f"UPDATE proInfra SET {target}=(?) WHERE id=(?)", (particular_infra[target], province_id))
                connection.commit()

                available_buildings.pop(random_building)

                if damage_effects.get(target, 0):
                    damage_effects[target][1] += 1
                else:
                    damage_effects[target] = ["destroyed", 1]

            # NOTE: possible feature, when a building not destroyed but could be unusable (the reparation cost lower than rebuying it)
            else: max_damage = abs(damage-health)

            damage -= health

        # will return: how many buildings are damaged or destroyed
        # format: {building_name: ["effect name", affected_amount]}
        return damage_effects

    # Returns the morale either for the attacker or the defender, and with the war_id
    @staticmethod
    def get_morale(column, attacker, defender):
        connection = sqlite3.connect("affo/aao.db")
        db = connection.cursor()
        war_id = db.execute(f"SELECT id FROM wars WHERE (attacker=(?) OR attacker=(?)) AND (defender=(?) OR defender=(?))", (attacker.user_id, defender.user_id, attacker.user_id, defender.user_id)).fetchall()[-1][0]
        morale = db.execute(f"SELECT {column} FROM wars WHERE id=(?)", (war_id,)).fetchone()[0]
        return (war_id, morale)

    # Update the morale and give back the win type name
    @staticmethod
    def morale_change(war_id, morale, column, win_type):
        connection = sqlite3.connect("affo/aao.db")
        db = connection.cursor()
        # war_id = db.execute(f"SELECT id FROM wars WHERE (attacker=(?) OR attacker=(?)) AND (defender=(?) OR defender=(?))", (attacker.user_id, defender.user_id, attacker.user_id, defender.user_id)).fetchall()[-1][0]
        # morale = db.execute(f"SELECT {column} FROM wars WHERE id=(?)", (war_id,)).fetchone()[0]

        # annihilation
        # 50 morale change
        if win_type >= 3:
            morale = morale-50
            win_condition = "annihilation"

        # definite victory
        # 35 morale change
        elif win_type >= 2:
            morale = morale-35
            win_condition = "definite victory"

        # close victory
        # 25 morale change
        else:
            morale = morale-25
            win_condition = "close victory"

        # Win the war
        if morale <= 0:
            Nation.set_peace(db, connection, war_id)
            # TODO: need a method for give the winner the pize for winning the war (this is not negotiation because the enemy completly lost the war since morale is 0)
            print("THE WAR IS OVER")

        db.execute(f"UPDATE wars SET {column}=(?) WHERE id=(?)", (morale, war_id))
        connection.commit()
        connection.close()

        return win_condition

    @staticmethod
    def special_fight(attacker, defender, target): # Units, Units, int -> str, None
        target_amount = defender.get_military(defender.user_id).get(target, None)

        if target_amount != None:
            special_unit = attacker.selected_units_list[0]
            attack_effects = attacker.attack(special_unit, target)

            # Surely destroy this percentage of the targeted units
            # NOTE: devided attack_effects[0] by 20 otherwise special units damage are too overpowered maybe give it other value
            min_destruction = target_amount*(1/5)*(attack_effects[0]/(20+attack_effects[1])*attacker.selected_units[special_unit])

            # Random bonus on unit destruction
            destruction_rate = random.uniform(0.5, 0.8)
            final_destruction = destruction_rate*min_destruction

            before_casulaties = list(dict(defender.selected_units).values())[0]
            defender.casualties(target, final_destruction)


            # infrastructure damage
            connection = sqlite3.connect('affo/aao.db')
            db = connection.cursor()
            province_id_fetch = db.execute("SELECT id FROM provinces WHERE userId=(?) ORDER BY id ASC", (defender.user_id,)).fetchall()
            random_province = province_id_fetch[random.randint(0, len(province_id_fetch)-1)][0]

            # If nuke damage public_works
            public_works = Nation.get_public_works(random_province)
            infra_damage_effects = Military.infrastructure_damage(attack_effects[0], public_works, random_province)

            # {target: losed_amount} <- the target and the destroyed amount
            return ({target: before_casulaties-list(dict(defender.selected_units).values())[0]}, infra_damage_effects)

        else:
            return "Invalid target is selected!"

    # NOTICE: in the future we could use this as an instance method unstead of static method
    '''
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

        attacker_roll = random.uniform(0, 2)
        attacker_chance = 0
        attacker_unit_amount_bonuses = 0
        attacker_bonus = 0

        defender_roll = random.uniform(0,2)
        defender_chance = 0
        defender_unit_amount_bonuses = 0
        defender_bonus = 0

        defender_infra_damage = 0

        for attacker_unit, defender_unit in zip(attacker.selected_units_list, defender.selected_units_list):

            # Unit amount chance - this way still get bonuses even if no counter unit_type
            defender_unit_amount_bonuses += defender.selected_units[defender_unit]/100 # is dict
            attacker_unit_amount_bonuses += attacker.selected_units[attacker_unit]/100

            # Compare attacker agains defender
            for unit in defender.selected_units_list:
                attack_effects = attacker.attack(attacker_unit, unit)
                attacker_bonus += calculate_bonuses(attack_effects, defender, unit)
                # used to be += attacker.attack(attacker_unit, unit, defender)[1]

                defender_infra_damage += attack_effects[0]

            # Compare defender against attacker
            for unit in attacker.selected_units_list:
                defender_bonus += calculate_bonuses(defender.attack(defender_unit, unit), attacker, unit)

        attacker_chance += attacker_roll+attacker_unit_amount_bonuses+attacker_bonus
        defender_chance += defender_roll+defender_unit_amount_bonuses+defender_bonus
        print("BONUSES", attacker_bonus, defender_bonus)
        print("CHANCES", attacker_chance, defender_chance)
        print("INFRA DAMAE", defender_infra_damage)

        # Determine the winner
        if defender_chance >= attacker_chance:
            winner = defender

            # morale column of the loser
            morale_column = "attacker_morale"

            loser = attacker
            win_type = defender_chance/attacker_chance
            winner_casulties = attacker_chance/defender_chance

        else:
            winner = attacker

            # morale column of the loser
            morale_column = "defender_morale"

            loser = defender
            win_type = attacker_chance/defender_chance
            winner_casulties = defender_chance/attacker_chance

        # Effects based on win_type (idk: destroy buildings or something)
        # loser_casulties = win_type so win_type also is the loser's casulties

        war_id, morale = Military.get_morale(morale_column, attacker, defender)
        win_condition = Military.morale_change(war_id, morale, morale_column, win_type)
        # win_condition = Military.morale_change(morale_column, win_type, attacker, defender)

        # Maybe use the damage property also in unit loss
        # TODO: make unit loss more precise
        for winner_unit, loser_unit in zip(winner.selected_units_list, loser.selected_units_list):
            w_casualties = winner_casulties*random.uniform(0.6, 1.5)*2.5
            l_casualties =  win_type*random.uniform(0.8, 1.5)*2.5

            winner.casualties(winner_unit, w_casualties)
            loser.casualties(loser_unit, l_casualties)

        # infrastructure damage
        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()
        province_id_fetch = db.execute("SELECT id FROM provinces WHERE userId=(?) ORDER BY id ASC", (defender.user_id,)).fetchall()
        random_province = province_id_fetch[random.randint(0, len(province_id_fetch)-1)][0]

        # Currently units only affect public works
        public_works = Nation.get_public_works(random_province)
        infra_damage_effects = Military.infrastructure_damage(attack_effects[0], public_works, random_province)

        # return (winner.user_id, return_winner_cas, return_loser_cas)
        return (winner.user_id, win_condition, infra_damage_effects)

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

# DEBUGGING:
if __name__ == "__main__":
    p = Nation.get_public_works(14)
    Military.infrastructure_damage(20, p)
    print(p)
