import random
import psycopg2
import os, time
from dotenv import load_dotenv
load_dotenv()

def calculate_bonuses(attack_effects, enemy_object, target): # int, Units, str -> int
    # Calculate the percentage of total units will be affected
    defending_unit_amount = enemy_object.selected_units[target]

    # sum of units amount
    enemy_units_total_amount = sum(enemy_object.selected_units.values())

    # the affected percentage from sum of units
    unit_of_army = (defending_unit_amount*100)/(enemy_units_total_amount+1)

    # the bonus calculated based on affected percentage
    affected_bonus = attack_effects[1]*(unit_of_army/100)

    # divide affected_bonus to make bonus effect less relevant
    attack_effects = affected_bonus/100

    # DEBUGGING:
    # print("UOA", unit_of_army, attacker_unit, target, self.user_id, affected_bonus)
    return attack_effects

class Economy:

    resources = [
    "rations", "oil", "coal", "uranium", "bauxite",
    "iron", "lead", "copper", "lumber", "components",
    "steel", "consumer_goods", "aluminium", "gasoline", "ammunition"
    ]


    def __init__(self, nationID):
        self.nationID = nationID

    def get_economy(self):

        connection = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"))
        db = connection.cursor()

        # TODO fix this when the databases changes and update to include all resources
        db.execute("SELECT gold FROM stats WHERE id=(%s)", (self.nationID,))
        self.gold = db.fetchone()[0]
    def get_particular_resources(self, resources):

        connection = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"))
        db = connection.cursor()

        resource_dict = {}

        try:
            for resource in resources:
                db.execute(f"SELECT {resource} FROM resources WHERE id=(%s)", (self.nationID,))
                resource_dict[resource] = db.fetchone()[0]
        except:

            # TODO ERROR HANDLER OR RETURN THE ERROR AS A VAlUE
            print("INVALID RESOURCE NAME")
            return "Invalid resource"

        return resource_dict


    def grant_resources(self, resource, amount):
        # TODO find a way to get the database to work on relative directories
        connection = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"))
        db = connection.cursor()

        db.execute("UPDATE stats SET (%s) = (%s) WHERE id(%s)", (resource, amount, self.nationID))

        connection.commit()

    # IMPORTANT: the amount is not validated in this method, so you should provide a valid value
    def transfer_resources(self, resource, amount, destinationID):
        connection = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"))
        db = connection.cursor()

        if resource not in self.resources:
            return "Invalid resource"

        # get amount of resource

        resource_sel_stat = f"SELECT {resource} FROM resources " + "WHERE id=%s"

        db.execute(resource_sel_stat, (self.nationID,))
        originalUser = int(db.fetchone()[0])
        db.execute(resource_sel_stat, (destinationID,))
        destinationUser = int(db.fetchone()[0])

        # subtracts the resource from one nation to another
        originalUser -= amount
        destinationUser += amount

        # writes changes in db
        db.execute(f"UPDATE resources SET {resource}=(%s) WHERE id=(%s)", (originalUser, self.nationID))
        db.execute(f"UPDATE resources SET {resource}=(%s) WHERE id=(%s)", (destinationUser, destinationID))

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

    public_works = ["libraries", "universities", "hospitals", "city_parks", "monorails"]

    # structure of upgrade dictionaries is "name_of_upgrade": "bonus gived by upgrade"
    supply_related_upgrades = {"lootingTeams": 10}
    economy_related_upgrades = {}

    # Database management
    # TODO: find a more effective way to handle database stuff
    # path = ''.join([os.path.abspath('').split("AnO")[0], 'AnO/affo/aao.db'])
    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))
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

    # Function for sending posts to nation's news page
    def news_signal(message):
        pass

    def get_provinces(self):

        connection = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"))

        db = connection.cursor()
        if self.provinces == None:
            self.provinces = {"provinces_number": 0, "province_stats": {}}
            db.execute("SELECT COUNT(provinceName) FROM provinces WHERE userId=%s", (self.id,))
            provinces_number = db.fetchone()[0]
            self.provinces["provinces_number"] = provinces_number

            if provinces_number > 0:
                db.execute("SELECT * FROM provinces WHERE userId=(?)", (self.id,))
                provinces = db.fetchall()
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

    @staticmethod
    def get_current_wars(id):

        connection = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"))

        db = connection.cursor()
        db.execute("SELECT id FROM wars WHERE (attacker=(%s) OR defender=(%s)) AND peace_date IS NULL", (id, id,))
        id_list = db.fetchall()

        # # determine wheter the user is the aggressor or the defender
        # current_wars_result = []
        # for war_id in id_list:
        # db.execute("SELECT 1 FROM wars WHERE id=(%s) AND attacker=(%s)", (war_id[0], id))
        #     is_attacker = db.fetchone()
        #
        #     if is_attacker:
        #         war_id.append("attacker")
        #     else:
        #         war_id.append("defender")

        return id_list

    def printStatistics(self):
        print("Nation {}:\nWins {}\nLosses: {}".format(
            self.id, self.wins, self.losses))

    # Get everything from proInfra table which is in the "public works" category
    @classmethod
    def get_public_works(self, province_id):

        connection = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"))

        db = connection.cursor()
        public_works_string = ",".join(self.public_works)

        infra_sel_stat = F"SELECT {public_works_string} FROM proInfra " + "WHERE id=%s"
        db.execute(infra_sel_stat, (province_id,))
        fetch_public = db.fetchone()
        public_works_dict = {}

        for public in range(0, len(self.public_works)):
            public_works_dict[self.public_works[public]] = fetch_public[public]

        return public_works_dict

    # set the peace_date in wars table for a particular war
    @staticmethod
    def set_peace(db, connection, war_id=None, options=None):

        if war_id != None:
            db.execute("UPDATE wars SET peace_date=(%s) WHERE id=(%s)", (time.time(), war_id))

        else:
            option = options["option"]
            db.execute(f"UPDATE wars SET peace_date=(%s) WHERE {option}=(%s)", (time.time(), options["value"]))

        connection.commit()

    # Get the list of owned upgrades like supply amount increaser from 200 to 210, etc.
    @classmethod
    def get_upgrades(cls, upgrade_type, user_id):

        connection = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"))

        db = connection.cursor()
        upgrades = {}

        if upgrade_type == "supplies":
            for upgrade in cls.supply_related_upgrades.keys():

                upgrade_sel_stat = f"SELECT {upgrade} FROM upgrades " + "WHERE user_id=%s"
                db.execute(upgrade_sel_stat, (user_id,))

                count = db.fetchone()[0]
                upgrades[upgrade] = count

        # returns the bonus given by the upgrade
        return upgrades

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

        connection = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"))

        db = connection.cursor()

        for building in particular_infra.keys():
            amount = particular_infra[building]
            if amount > 0:

                # If there are multiple of the same building add those multiple times
                for i in range(0, amount):
                    available_buildings.append(building)

        # Damage logic (might include population damage)
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

                infra_update_stat = f"UPDATE proInfra SET {target}" + "=%s WHERE id=(%s)"
                db.execute(infra_update_stat, (particular_infra[target], province_id))

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

        connection = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"))

        db = connection.cursor()
        db.execute(f"SELECT id FROM wars WHERE (attacker=(%s) OR attacker=(%s)) AND (defender=(%s) OR defender=(%s))", (attacker.user_id, defender.user_id, attacker.user_id, defender.user_id))
        war_id = db.fetchall()[-1][0]
        db.execute(f"SELECT {column} FROM wars WHERE id=(%s)", (war_id,))
        morale = db.fetchone()[0]
        return (war_id, morale)

    # Reparation tax
    # parameter description:
        # winners: [id1,id2...idn]
        # losers: [id1,id2...idn]
    @staticmethod

    # NOTE: currently only one winner is supported winners = [id]
    def reparation_tax(winners, losers):
    # def reparation_tax(winner_side, loser_side):

        # get remaining morale for winner (only one supported current_wars)
        connection = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"))
        db = connection.cursor()

        # db.execute(
        # "SELECT IF attacker_morale==0 THEN defender_morale ELSE attacker_morale FROM (SELECT defender_morale,attacker_morale FROM wars WHERE (attacker=%s OR defender=%s) AND (attacker=%s OR defender=%s)) L",
        # (winners[0], winners[0], losers[0], losers[0]))

        db.execute(
        "SELECT CASE WHEN attacker_morale=0 THEN defender_morale\n ELSE attacker_morale\n END\n FROM wars WHERE (attacker=%s OR defender=%s) AND (attacker=%s OR defender=%s)",
        (winners[0], winners[0], losers[0], losers[0]))
        winner_remaining_morale=db.fetchone()[0]

        # Calculate reparation tax based on remaining morale
        # if winner_remaining_morale_effect
        tax_rate = 0.2*winner_remaining_morale

        print(
        db.execute("INSERT INTO reparation_tax (winner,loser,percentage,until) VALUES (%s,%s,%s,%s)", (winners[0], losers[0], tax_rate, time.time()+5000))
        )
        print(winner_remaining_morale, tax_rate)

        connection.commit()
        connection.close()

    # Update the morale and give back the win type name
    @staticmethod
    # def morale_change(war_id, morale, column, win_type, winner, loser):
    def morale_change(column, win_type, winner, loser):

        connection = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"))

        db = connection.cursor()

        db.execute("SELECT id FROM wars WHERE (attacker=(%s) OR attacker=(%s)) AND (defender=(%s) OR defender=(%s))", (winner.user_id, loser.user_id, winner.user_id, loser.user_id))
        war_id = db.fetchall()[-1][0]

        war_column_stat = f"SELECT {column} FROM wars " + "WHERE id=(%s)"
        db.execute(war_column_stat, (war_id,))
        morale = db.fetchone()[0]

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
            # TODO: need a method for give the winner the pize for winning the war (this is not negotiation because the enemy completly lost the war since morale is 0)
            Nation.set_peace(db, connection, war_id)
            eco = Economy(winner.user_id)

            for resource in Economy.resources:

                resource_sel_stat = f"SELECT {resource} FROM resources " + "WHERE id=%s"
                db.execute(resource_sel_stat, (loser.user_id,))
                resource_amount = db.fetchone()[0]

                # transfer 20% of resource on hand (TODO: implement if and alliance won how to give it)
                eco.transfer_resources(resource, resource_amount*(1/5), winner.user_id)

            print("THE WAR IS OVER")

        db.execute(f"UPDATE wars SET {column}=(%s) WHERE id=(%s)", (morale, war_id))

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
            connection = psycopg2.connect(
                database=os.getenv("PG_DATABASE"),
                user=os.getenv("PG_USER"),
                password=os.getenv("PG_PASSWORD"),
                host=os.getenv("PG_HOST"),
                port=os.getenv("PG_PORT"))

            db = connection.cursor()

            db.execute("SELECT id FROM provinces WHERE userId=(%s) ORDER BY id ASC", (defender.user_id,))
            province_id_fetch = db.fetchall()

            # decrease special unit amount after attack
            # TODO: check if too much special_unit amount is selected
            # TODO: decreate only the selected amount when attacker (ex. db 100 soldiers, attack with 20, don't decreate from 100)
            db.execute(f"SELECT {special_unit} FROM military WHERE id=(%s)", (attacker.user_id,))
            special_unit_fetch = db.fetchone()[0]

            db.execute(f"UPDATE military SET {special_unit}=(%s) WHERE id=(%s)", (special_unit_fetch-attacker.selected_units[special_unit], attacker.user_id))

            connection.commit()

            # TODO: NEED PROPER ERROR HANDLING FOR THIS INFRA DAMAGE ex. when user doesn't have province the can't damage it (it throws error)
            if len(province_id_fetch) > 0:
                random_province = province_id_fetch[random.randint(0, len(province_id_fetch)-1)][0]

                # If nuke damage public_works
                public_works = Nation.get_public_works(random_province)
                infra_damage_effects = Military.infrastructure_damage(attack_effects[0], public_works, random_province)
            else:
                infra_damage_effects = 0

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
    # attacker, defender means the attacker and the defender user JUST in this particular fight not in the whole war
    def fight(attacker, defender): # Units, Units -> int

        # IMPORTANT: Here you can change the values for the fight chances, bonuses and even can controll casualties (in this whole funciton)
        # If you want to change the bonuses given by a particular unit then go to `units.py` and you can find those in the classes
        attacker_roll = random.uniform(1, 2)
        attacker_chance = 0
        attacker_unit_amount_bonuses = 0
        attacker_bonus = 0

        defender_roll = random.uniform(1, 2)
        defender_chance = 0
        defender_unit_amount_bonuses = 0
        defender_bonus = 0

        dealt_infra_damage = 0

        for attacker_unit, defender_unit in zip(attacker.selected_units_list, defender.selected_units_list):

            # Unit amount chance - this way still get bonuses even if no counter unit_type
            defender_unit_amount_bonuses += defender.selected_units[defender_unit]/100 # is dict
            attacker_unit_amount_bonuses += attacker.selected_units[attacker_unit]/100

            # Compare attacker agains defender
            for unit in defender.selected_units_list:
                attack_effects = attacker.attack(attacker_unit, unit)
                attacker_bonus += calculate_bonuses(attack_effects, defender, unit)
                # used to be += attacker.attack(attacker_unit, unit, defender)[1]

                dealt_infra_damage += attack_effects[0]

            # Compare defender against attacker
            for unit in attacker.selected_units_list:
                defender_bonus += calculate_bonuses(defender.attack(defender_unit, unit), attacker, unit)

        # used to be: attacker_chance += attacker_roll+attacker_unit_amount_bonuses+attacker_bonus
        #             defender_chance += defender_roll+defender_unit_amount_bonuses+defender_bonus
        attacker_chance += attacker_roll+attacker_unit_amount_bonuses+attacker_bonus
        defender_chance += defender_roll+defender_unit_amount_bonuses+defender_bonus

        # If there are not attackers or defenders
        if defender_unit_amount_bonuses == 0:
            defender_chance = 0.001
        elif attacker_unit_amount_bonuses == 0:
            attacker_chance = 0.001

        print("attacker change ", attacker_chance, attacker_roll, attacker_unit_amount_bonuses, attacker_bonus)
        print("attacker change ", defender_chance, defender_roll, defender_unit_amount_bonuses, defender_bonus)

        # Determine the winner
        if defender_chance >= attacker_chance:
            winner = defender
            loser = attacker
            win_type = defender_chance/attacker_chance
            winner_casulties = attacker_chance/defender_chance
        else:
            winner = attacker
            loser = defender
            win_type = attacker_chance/defender_chance
            winner_casulties = defender_chance/attacker_chance


        # Get the absolute side (absolute attacker and defender) in the war for determining the loser's morale column name to decrease

        connection = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"))

        db = connection.cursor()

        db.execute("SELECT attacker FROM wars WHERE (attacker=(%s) OR defender=(%s)) AND peace_date IS NULL", (winner.user_id,winner.user_id))
        abs_attacker = db.fetchone()[0]

        if winner.user_id == abs_attacker:
            # morale column of the loser
            morale_column = "defender_morale"
        else:
            # morale column of the loser
            morale_column = "attacker_morale"

        # Effects based on win_type (idk: destroy buildings or something)
        # loser_casulties = win_type so win_type also is the loser's casulties

        war_id, morale = Military.get_morale(morale_column, attacker, defender)

        # print("MORALE COLUMN", morale_column, "WINNER FROM FIGHT MEHTOD", winner.user_id)
        # print("ATTC", attacker.user_id, defender.user_id)

        # win_condition = Military.morale_change(war_id, morale, morale_column, win_type)
        win_condition = Military.morale_change(morale_column, win_type, winner, loser)

        # Maybe use the damage property also in unit loss
        # TODO: make unit loss more precise
        for winner_unit, loser_unit in zip(winner.selected_units_list, loser.selected_units_list):
            w_casualties = winner_casulties*random.uniform(0.5, 1.5)*10
            l_casualties =  win_type*random.uniform(0.8, 1.5)*10

            winner.casualties(winner_unit, w_casualties)
            loser.casualties(loser_unit, l_casualties)

        # infrastructure damage
        connection = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"))

        # db = connection.cursor()
        # db.execute("SELECT id FROM provinces WHERE userId=(%s) ORDER BY id ASC", (defender.user_id,))
        # province_id_fetch = db.fetchall()
        # random_province = province_id_fetch[random.randint(0, len(province_id_fetch)-1)][0]
        #
        # # Currently units only affect public works
        # public_works = Nation.get_public_works(random_province)
        #
        # # TODO: enforce war type like raze,etc.
        # # example for the above line: if war_type is raze then attack_effects[0]*10
        # infra_damage_effects = Military.infrastructure_damage(attack_effects[0], public_works, random_province)

        # return (winner.user_id, return_winner_cas, return_loser_cas)
        return (winner.user_id, win_condition, [dealt_infra_damage, 0])

    # select only needed units instead of all
    # particular_units must be a list of string unit names
    @staticmethod
    def get_particular_units_list(cId, particular_units): # int, list -> list

        connection = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"))

        db = connection.cursor()

        # this data come in the format [(cId, soldiers, artillery, tanks, bombers, fighters, apaches, spies, icbms, nukes, destroyer, cruisers, submarines)]
        db.execute("SELECT * FROM military WHERE id=%s", (cId,))
        allAmounts = db.fetchall()

        # get the unit amounts based on the selected_units
        unit_to_amount_dict = {}

        # TODO: maybe use the self.allUnits because it looks like repetative code
        cidunits = ['cId','soldiers', 'artillery', 'tanks','bombers','fighters','apaches', 'spies','icbms','nukes','destroyers','cruisers','submarines']
        for count, item in enumerate(cidunits):
            unit_to_amount_dict[item] = allAmounts[0][count]

        # make a dictionary with 3 keys, listed in the particular_units list
        unit_lst = []
        for unit in particular_units:
            unit_lst.append(unit_to_amount_dict[unit])

        connection.close()
        return unit_lst # this is a list of the format [100, 50, 50]

    @staticmethod
    def get_military(cId): # int -> dict

        connection = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"))

        db = connection.cursor()
        db.execute("SELECT tanks FROM military WHERE id=%s", (cId,))
        tanks = db.fetchone()[0]

        db.execute("SELECT soldiers FROM military WHERE id=%s", (cId,))
        soldiers = db.fetchone()[0]

        db.execute("SELECT artillery FROM military WHERE id=%s", (cId,))
        artillery = db.fetchone()[0]

        db.execute("SELECT bombers FROM military WHERE id=%s", (cId,))
        bombers = db.fetchone()[0]

        db.execute("SELECT fighters FROM military WHERE id=%s", (cId,))
        fighters = db.fetchone()[0]

        db.execute("SELECT apaches FROM military WHERE id=%s", (cId,))
        apaches = db.fetchone()[0]

        db.execute("SELECT destroyers FROM military WHERE id=%s", (cId,))
        destroyers = db.fetchone()[0]

        db.execute("SELECT cruisers FROM military WHERE id=%s", (cId,))
        cruisers = db.fetchone()[0]

        db.execute("SELECT submarines FROM military WHERE id=%s", (cId,))
        submarines = db.fetchone()[0]

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

        connection = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"))

        db = connection.cursor()

        db.execute("SELECT spies FROM military WHERE id=%s", (cId,))
        spies = db.fetchone()[0]

        db.execute("SELECT ICBMs FROM military WHERE id=%s", (cId,))
        icbms = db.fetchone()[0]

        db.execute("SELECT nukes FROM military WHERE id=%s", (cId,))
        nukes = db.fetchone()[0]
        connection.close()

        return {
            "spies": spies,
            "icbms": icbms,
            "nukes": nukes
        }

    # Check and set default_defense in nation table
    def set_defense(self, defense_string): # str -> None

        connection = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"))

        db = connection.cursor()
        defense_list = defense_string.split(",")
        if len(defense_units) == 3:

            # default_defense is stored in the db: 'unit1,unit2,unit3'
            defense_units = ",".join(defense_units)

            db.execute("UPDATE nation SET default_defense=(%s) WHERE nation_id=(%s)", (defense_units, nation[1]))

            connection.commit()
        else:
            # user should never reach here, msg for beta testers
            return "Invalid number of units given to set_defense, report to admin"

# DEBUGGING:
if __name__ == "__main__":
    # p = Nation.get_public_works(14)
    # Military.infrastructure_damage(20, p)
    # print(p)

    m = Military(2)
    m.reparation_tax([2], [1])
