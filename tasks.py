from celery import Celery
import psycopg2
import os
import time
from dotenv import load_dotenv
from attack_scripts import Economy
import math
import variables
from psycopg2.extras import RealDictCursor
from celery.schedules import crontab
import math
load_dotenv()

celery = Celery("tasks", broker=os.getenv("broker_url"))
celery.conf.update(
    broker_url=os.getenv("broker_url"),
    result_backend=os.getenv("broker_url"),
    CELERY_BROKER_URL=os.getenv("broker_url")
)

celery_beat_schedule = {
    "population_growth": {
        "task": "tasks.task_population_growth",
        "schedule": crontab(minute=0, hour='*/1'),  # Run hourly
    },
    "generate_province_revenue": {
        "task": "tasks.task_generate_province_revenue",
        "schedule": crontab(minute=0, hour='*/1'),  # Run hourly
    },
    "tax_income": {
        "task": "tasks.task_tax_income",
        "schedule": crontab(minute=0, hour='*/1'),  # Run hourly
    },
    "war_reparation_tax": {
        "task": "tasks.task_war_reparation_tax",
        # Run every day at midnight (UTC)
        "schedule": crontab(minute=0, hour=0)
    },
    "manpower_increase": {
        "task": "app.task_manpower_increase",
        "schedule": crontab(minute=0, hour=0) # Run everyday at midnight (UTC)
    }
}

celery.conf.update(timezone="UTC",
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    beat_schedule=celery_beat_schedule,
)

# Handles exception for an error
def handle_exception(e):
    filename = __file__
    line = e.__traceback__.tb_lineno
    print("\n-----------------START OF EXCEPTION-------------------")
    print(f"Filename: {filename}")
    print(f"Error: {e}")
    print(f"Line: {line}")
    print("-----------------END OF EXCEPTION---------------------\n")

# Returns how many rations a player needs
def rations_needed(cId):

    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = conn.cursor()

    db.execute("SELECT population, id FROM provinces WHERE userId=%s", (cId,))
    provinces = db.fetchall()

    total_rations = 0
    for population, _ in provinces:
        rations_needed = population // variables.RATIONS_PER
        total_rations += rations_needed
    return total_rations

# Returns energy production and consumption from a certain province
def energy_info(province_id): # TODO: Rewrite this function

    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    production = 0
    consumption = 0

    consumers = variables.ENERGY_CONSUMERS
    producers = variables.ENERGY_UNITS
    
    infra = variables.NEW_INFRA

    consumer_query = f"SELECT {'+'.join(consumers)}" + " FROM proInfra WHERE id=%s"
    db.execute(consumer_query, (province_id,))
    consumption = db.fetchone()[0]

    for producer in producers:
        producer_query = f"SELECT {producer}" + " FROM proInfra WHERE id=%s"
        db.execute(producer_query, (province_id,))
        producer_count = db.fetchone()[0]

        production += producer_count * infra[producer]["plus"]["energy"]

    return consumption, production

# Returns a rations score for a user, from -1 to -1.4
# -1 = Enough or more than enough rations
# -1.4 = No rations at all
def food_stats(user_id):

    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = conn.cursor()

    needed_rations = rations_needed(user_id)

    db.execute("SELECT rations FROM resources WHERE id=%s", (user_id,))
    current_rations = db.fetchone()[0]

    if needed_rations == 0: needed_rations = 1

    rcp = (current_rations / needed_rations) - 1 # Normalizes the score to 0.
    if rcp > 0: rcp = 0

    score = -1 + (rcp * variables.NO_FOOD_TAX_MULTIPLIER)

    return score

# Returns an energy score for a user, from -1 to -1.6
# -1 = Enough or more than enough energy
# -1.6 = No energy at all
def energy_stats(user_id): 

    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = conn.cursor()

    db.execute("SELECT id FROM provinces WHERE userId=%s", (user_id,))
    provinces = db.fetchall()

    total_energy_consumption = 0
    total_energy_production = 0

    for province_id in provinces:
        province_id = province_id[0]

        consumption, production = energy_info(province_id)
        total_energy_consumption += consumption
        total_energy_production += production

    if total_energy_consumption == 0: total_energy_consumption = 1

    tcp = (total_energy_production / total_energy_consumption) - 1 # Normalizes the score to 0.
    if tcp > 0: tcp = 0

    score = -1 + (tcp * variables.NO_ENERGY_TAX_MULTIPLIER)

    return score

# Function for calculating tax income
def calc_ti(user_id):

    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = conn.cursor()

    db.execute("SELECT consumer_goods FROM resources WHERE id=%s", (user_id,))
    consumer_goods = db.fetchone()[0]

    try:
        db.execute("SELECT education FROM policies WHERE user_id=%s", (user_id,))
        policies = db.fetchone()[0]
    except: 
        policies = []

    try:
        db.execute("SELECT population, land FROM provinces WHERE userId=%s", (user_id,))
        provinces = db.fetchall()

        if provinces == []: # User doesn't have any provinces
            return False, False

        income = 0
        for population, land in provinces: # Base and land calculation
            land_multiplier = (land-1) * variables.DEFAULT_LAND_TAX_MULTIPLIER
            if land_multiplier > 1: land_multiplier = 1 # Cap 100% 

            base_multiplier = variables.DEFAULT_TAX_INCOME
            if 1 in policies: # 1 Policy (1)
                base_multiplier *= 1.01 # Citizens pay 1% more tax)
            if 6 in policies: # 6 Policy (2)
                base_multiplier *= 0.98
            if 4 in policies: # 4 Policy (2)
                base_multiplier *= 0.98

            multiplier = base_multiplier+(base_multiplier*land_multiplier)
            income += (multiplier*population)

        # Consumer goods
        new_consumer_goods = 0
        max_cg = math.ceil(population / variables.CONSUMER_GOODS_PER)
        
        if consumer_goods != 0 and max_cg != 0:
            if max_cg <= consumer_goods:
                new_consumer_goods -= max_cg
                income *= variables.CONSUMER_GOODS_TAX_MULTIPLIER
            else:
                multiplier = consumer_goods / max_cg
                income *= 1+(0.5*multiplier)
                new_consumer_goods -= consumer_goods
            
        return math.floor(income), new_consumer_goods
    except Exception as e:
        handle_exception(e)
        return False, False

print(calc_ti(8))

# (x, y) - (income, removed_consumer_goods)
# * Tested no provinces
# * Tested population=100, land=1, consumer_goods=0 (1, 0)
# * Tested population=100, land=51, consumer_goods=0 (2, 0)
# * Tested population=100000, land=10, consumer_goods=10 (1770, -5)
# * Tested population=100000, land=1, consumer_goods=0 (1000, 0)

# Function for actually giving money to players
def tax_income():

    conn = psycopg2.connect(
    database=os.getenv("PG_DATABASE"),
    user=os.getenv("PG_USER"),
    password=os.getenv("PG_PASSWORD"),
    host=os.getenv("PG_HOST"),
    port=os.getenv("PG_PORT"))

    db = conn.cursor()

    db.execute("SELECT id FROM users")
    users = db.fetchall()

    for user_id in users:

        user_id = user_id[0]

        db.execute("SELECT gold FROM stats WHERE id=%s", (user_id,))
        current_money = db.fetchone()[0]

        money, consumer_goods = calc_ti(user_id)
        if not money and not consumer_goods: # Error while calculating or user doesn't have any provinces
            continue

        print(f"Updated money for user id: {user_id}. Set {current_money} money to {money} money. ({money-current_money})")

        db.execute("UPDATE stats SET gold=gold+%s WHERE id=%s", (money, user_id))
        db.execute("UPDATE resources SET consumer_goods=consumer_goods-%s WHERE id=%s", (consumer_goods, user_id))

        conn.commit()

    conn.close()

# Function for calculating population growth for a given province
def calc_pg(pId, rations):

    conn = psycopg2.connect(
    database=os.getenv("PG_DATABASE"),
    user=os.getenv("PG_USER"),
    password=os.getenv("PG_PASSWORD"),
    host=os.getenv("PG_HOST"),
    port=os.getenv("PG_PORT"))

    db = conn.cursor()

    db.execute("SELECT population FROM provinces WHERE id=%s", (pId,))
    curPop = db.fetchone()[0]

    maxPop = variables.DEFAULT_MAX_POPULATION # Base max population: 1 million

    try:
        db.execute("SELECT cityCount FROM provinces WHERE id=%s", (pId,))
        cities = db.fetchone()[0]
    except TypeError:
        conn.rollback()
        cities = 0

    maxPop += cities * variables.CITY_MAX_POPULATION_ADDITION # Each city adds 750,000 population
        
    try:
        db.execute("SELECT land FROM provinces WHERE id=%s", (pId,))
        land = db.fetchone()[0]
    except TypeError:
        conn.rollback()
        land = 0

    maxPop += land * variables.LAND_MAX_POPULATION_ADDITION # Each land slot adds 120,000 population

    try:
        db.execute("SELECT happiness FROM provinces WHERE id=%s", (pId,))
        happiness = int(db.fetchone()[0])
    except TypeError:
        conn.rollback()
        happiness = 0

    try:
        db.execute("SELECT pollution FROM provinces WHERE id=%s", (pId,))
        pollution = db.fetchone()[0]
    except TypeError:
        conn.rollback()
        pollution = 0

    try:
        db.execute("SELECT productivity FROM provinces WHERE id=%s", (pId,))
        productivity = db.fetchone()[0]
    except TypeError:
        conn.rollback()
        productivity = 0

    # Each % increases / decreases max population by 
    happiness = round((happiness - 50) * variables.DEFAULT_HAPPINESS_TAX_MULTIPLIER, 2) # The more you have the better

    # Each % increases / decreases max population by 
    pollution = round((pollution - 50) * - variables.DEFAULT_POLLUTION_MAX_POPULATION_MULTIPLIER, 2) # The less you have the better

    # Each % increases / decreases resource output by 
    productivity = round((productivity - 50) * variables.DEFAULT_PRODUCTIVITY_PRODUCTION_MUTLIPLIER, 2) # The more you have the better

    maxPop += (maxPop * happiness) + (maxPop * pollution)
    maxPop = round(maxPop)

    if maxPop < variables.DEFAULT_MAX_POPULATION:
        maxPop = variables.DEFAULT_MAX_POPULATION

    rations_increase = 0 # Default rations increase. If user has no rations it will decrease by 1% of maxPop 
    rations_needed = curPop // variables.RATIONS_PER

    if rations_needed < 1: rations_needed = 1 # Trying to not get division by zero error

    rations_needed_percent = rations / rations_needed
    if rations_needed_percent > 1:
        rations_needed_percent = 1
        
    rations_increase += round(rations_needed_percent * 2, 2)

    # Calculates the new rations of the player
    new_rations = rations - rations_needed
    if new_rations < 0:
        new_rations = 0

    newPop = (maxPop // 100) * rations_increase  # 1% of maxPop * -1 to 1

    db.execute("SELECT userid FROM provinces WHERE id=%s", (pId,))
    owner = db.fetchone()[0]

    try:
        db.execute("SELECT education FROM policies WHERE user_id=%s", (owner,))
        policies = db.fetchone()[0]
    except:
        policies = []

    if 5 in policies:
        newPop *= 1.16 # 16% increase

    fullPop = curPop + newPop

    if fullPop < 0: fullPop = 0

    return new_rations, fullPop

# Seems to be working as expected
def population_growth(): # Function for growing population

    conn = psycopg2.connect(
    database=os.getenv("PG_DATABASE"),
    user=os.getenv("PG_USER"),
    password=os.getenv("PG_PASSWORD"),
    host=os.getenv("PG_HOST"),
    port=os.getenv("PG_PORT"))

    db = conn.cursor()

    db.execute("SELECT id FROM provinces ORDER BY userId ASC")
    provinces = db.fetchall()

    for province_id in provinces:
        province_id = province_id[0]
        try:

            db.execute("SELECT userId FROM provinces WHERE id=%s", (province_id,))
            user_id = db.fetchone()[0]

            db.execute("SELECT rations FROM resources WHERE id=%s", (user_id,))
            current_rations = db.fetchone()[0]

            rations, population = calc_pg(province_id, current_rations)

            print(f"Updated rations for province id: {province_id}, user id: {user_id}")
            print(f"Set {current_rations} to {rations} ({rations - current_rations})")
            db.execute("UPDATE resources SET rations=%s WHERE id=%s", (rations, user_id))
            db.execute("UPDATE provinces SET population=%s WHERE id=%s", (population, province_id))

            conn.commit()

        except Exception as e: 
            conn.rollback()
            handle_exception(e)
            continue

    conn.close()

def find_unit_category(unit):
    categories = variables.INFRA_TYPE_BUILDINGS
    for name, list in categories.items():
        if unit in list:
            return name
    return False

"""
Tested features:
- resource giving 
- unit with enough resources selection
- energy didnt change
- removal of resources
- good monetary removal
"""

def generate_province_revenue(): # Runs each hour

    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = conn.cursor()
    dbdict = conn.cursor(cursor_factory=RealDictCursor)

    columns = variables.BUILDINGS

    province_resources = ["energy", "population", "happiness", "pollution", "productivity", "consumer_spending"]
    percentage_based = ["happiness", "productivity", "consumer_spending", "pollution"]

    energy_consumers = variables.ENERGY_CONSUMERS
    user_resources = variables.RESOURCES
    infra = variables.NEW_INFRA

    try:
        db.execute("SELECT proInfra.id, provinces.userId, provinces.land FROM proInfra INNER JOIN provinces ON proInfra.id=provinces.id ORDER BY id ASC")
        infra_ids = db.fetchall()
    except:
        infra_ids = []

    for province_id, user_id, land in infra_ids:
        db.execute("UPDATE provinces SET energy=0 WHERE id=%s", (province_id,)) # So energy would reset each turn

        dbdict.execute("SELECT * FROM upgrades WHERE user_id=%s", (user_id, ))
        upgrades = dict(dbdict.fetchone())

        try:
            db.execute("SELECT education FROM policies WHERE user_id=%s", (user_id,))
            policies = db.fetchone()[0]
        except:
            policies = []
        
        dbdict.execute("SELECT * FROM proInfra WHERE id=%s", (province_id, ))
        units = dict(dbdict.fetchone())

        for unit in columns:
            unit_amount = units[unit]
            
            if unit_amount == 0:
                continue

            unit_category = find_unit_category(unit)
            try:
                effminus = infra[unit].get('effminus', {})
                minus = infra[unit].get('minus', {})

                operating_costs = infra[unit]['money'] * unit_amount
                plus_amount = 0
                plus_amount_multiplier = 1

                if 1 in policies and unit == "universities": operating_costs *= 1.14
                if 3 in policies and unit == "universities": operating_costs *= 1.18
                if 6 in policies and unit == "universities": operating_costs *= 0.93

                ### CHEAPER MATERIALS
                if unit_category == "industry" and upgrades["cheapermaterials"]:
                    operating_costs *= 0.8
                ### ONLINE SHOPPING
                if unit == "malls" and upgrades["onlineshopping"]:
                    operating_costs *= 0.7

                # Removing money operating costs (if user has the money)
                db.execute("SELECT gold FROM stats WHERE id=%s", (user_id,))
                current_money = db.fetchone()[0]

                operating_costs = int(operating_costs)

                # Boolean for whether a player has enough resources, energy, money to power his building
                has_enough_stuff = { "status": True, "issues": [] }

                if current_money < operating_costs:
                    print(f"Couldn't update {unit} for {province_id} as they don't have enough money")
                    has_enough_stuff["status"] = False
                    has_enough_stuff["issues"].append("money")
                else:
                    try:
                        db.execute("UPDATE stats SET gold=gold-%s WHERE id=%s", (operating_costs, user_id))
                    except:
                        conn.rollback()
                        continue

                # TODO: make sure this works correctly
                if unit in energy_consumers:
                    db.execute("SELECT energy FROM provinces WHERE id=%s", (province_id,))
                    current_energy = db.fetchone()[0]

                    new_energy = current_energy - unit_amount # Each unit consumes 1 energy

                    if new_energy < 0:
                        has_enough_stuff["status"] = False
                        has_enough_stuff["issues"].append("energy")
                        new_energy = 0

                    db.execute("UPDATE provinces SET energy=%s WHERE id=%s", (new_energy, province_id))

                dbdict.execute("SELECT * FROM resources WHERE id=%s", (user_id,))
                resources = dict(dbdict.fetchone())
                for resource, amount in minus.items():
                    amount *= unit_amount
                    current_resource = resources[resource]

                    ### AUTOMATION INTEGRATION
                    if unit == "component_factories" and upgrades["automationintegration"]: amount *= 0.75
                    ### LARGER FORGES
                    if unit == "steel_mills" and upgrades["largerforges"]: amount *= 0.7

                    new_resource = current_resource - amount

                    if new_resource < 0:
                        has_enough_stuff["status"] = False
                        has_enough_stuff["issues"].append(resource)
                        print(f"F | USER: {user_id} | PROVINCE: {province_id} | {unit} ({unit_amount}) | Failed to minus {amount} of {resource} ({current_resource})")
                    else:
                        resource_u_statement = f"UPDATE resources SET {resource}" + "=%s WHERE id=%s"
                        print(f"S | MINUS | USER: {user_id} | PROVINCE: {province_id} | {unit} ({unit_amount}) | {resource} {current_resource}={new_resource} (-{current_resource-new_resource})")
                        db.execute(resource_u_statement, (new_resource, user_id,))

                if not has_enough_stuff["status"]:
                    print(f"F | USER: {user_id} | PROVINCE: {province_id} | {unit} ({unit_amount}) | Not enough {', '.join(has_enough_stuff['issues'])}")
                    continue

                plus = infra[unit].get('plus', {})

                ### BETTER ENGINEERING
                if unit == "nuclear_reactors" and upgrades["betterengineering"]: plus['energy'] += 6

                eff = infra[unit].get('eff', {})

                if unit == "universities" and 3 in policies:
                    eff["productivity"] *= 1.10
                    eff["happiness"] *= 1.10

                if unit == "hospitals":
                    if upgrades["nationalhealthinstitution"]:
                        eff["happiness"] *= 1.3
                        eff["happiness"] = int(eff["happiness"])

                if unit == "monorails":
                    if upgrades["highspeedrail"]:
                        eff["productivity"] *= 1.2
                        eff["productivity"] = int(eff["productivity"])

                """
                print(f"Unit: {unit}")
                print(f"Add {plus_amount} to {plus_resource}")
                print(f"Remove ${operating_costs} as operating costs")
                print(f"\n")
                """
                if unit == "bauxite_mines" and upgrades["strongerexplosives"]:
                    # TODO: fix this plus_amount variable
                    plus_amount_multiplier += 0.45

                if unit == "farms":
                    if upgrades["advancedmachinery"]: plus_amount_multiplier += 0.5

                    plus_amount += int(land * variables.LAND_FARM_PRODUCTION_ADDITION)

                # Function for _plus
                for resource, amount in plus.items():
                    amount += plus_amount
                    amount *= unit_amount
                    amount *= plus_amount_multiplier
                    if resource in province_resources:

                        # TODO: make this optimized
                        cpr_statement = f"SELECT {resource} FROM provinces" + " WHERE id=%s"
                        db.execute(cpr_statement, (province_id,))
                        current_plus_resource = db.fetchone()[0]

                        # Adding resource
                        new_resource_number = current_plus_resource + amount

                        if resource in percentage_based and new_resource_number > 100: new_resource_number = 100
                        if new_resource_number < 0: new_resource_number = 0 # TODO: is this line really necessary?

                        upd_prov_statement = f"UPDATE provinces SET {resource}" + "=%s WHERE id=%s"
                        print(f"S | PLUS |USER: {user_id} | PROVINCE: {province_id} | {unit} ({unit_amount}) | ADDING | {resource} | {amount}")
                        db.execute(upd_prov_statement, (new_resource_number, province_id))

                    elif resource in user_resources:
                        upd_res_statement = f"UPDATE resources SET {resource}={resource}" + "+%s WHERE id=%s"
                        print(f"S | PLUS | USER: {user_id} | PROVINCE: {province_id} | {unit} ({unit_amount}) | ADDING | {resource} | {amount}")
                        db.execute(upd_res_statement, (amount, user_id,))

                # Function for completing an effect (adding pollution, etc)
                def do_effect(eff, eff_amount, sign):

                    # TODO: one query for all this
                    effect_select = f"SELECT {eff} FROM provinces " + "WHERE id=%s"
                    db.execute(effect_select, (province_id,))
                    current_effect = db.fetchone()[0]

                    ### GOVERNMENT REGULATION
                    if unit_category == "retail" and upgrades["governmentregulation"] and eff == "pollution" and sign == "+":
                        eff_amount *= 0.75
                    ###
                    if unit == "universities" and 3 in policies:
                        eff_amount *= 1.1

                    eff_amount = math.ceil(eff_amount) # Using math.ceil so universities +18% would work

                    if sign == "+": new_effect = current_effect + eff_amount
                    elif sign == "-": new_effect = current_effect - eff_amount

                    if eff in percentage_based:
                        if new_effect > 100: new_effect = 100
                        if new_effect < 0: new_effect = 0
                    else:
                        if new_effect < 0: new_effect = 0

                    eff_update = f"UPDATE provinces SET {eff}" + "=%s WHERE id=%s"
                    db.execute(eff_update, (new_effect, province_id))

                for effect, amount in eff.items():
                    amount *= unit_amount
                    do_effect(effect, amount, "+")

                for effect, amount in effminus.items():
                    amount *= unit_amount
                    do_effect(effect, amount, "-")
            
                if 5 in policies:
                    db.execute("UPDATE provinces SET productivity=productivity*0.91 WHERE id=%s", (province_id,))
                if 4 in policies:
                    db.execute("UPDATE provinces SET productivity=productivity*1.05 WHERE id=%s", (province_id,))
                if 2 in policies:
                    db.execute("UPDATE provinces SET happiness=happiness*0.89 WHERE id=%s", (province_id,))

                conn.commit() # Commits the changes

            except Exception as e:
                conn.rollback()
                handle_exception(e)
                continue

    conn.close() # Closes the connection

def war_reparation_tax():
    conn = psycopg2.connect(
    database=os.getenv("PG_DATABASE"),
    user=os.getenv("PG_USER"),
    password=os.getenv("PG_PASSWORD"),
    host=os.getenv("PG_HOST"),
    port=os.getenv("PG_PORT"))
    db = conn.cursor()
    db.execute("SELECT id,peace_date,attacker,attacker_morale,defender,defender_morale FROM wars WHERE (peace_date IS NOT NULL) AND (peace_offer_id IS NULL)")
    truces = db.fetchall()

    for state in truces:
        war_id,peace_date,attacker,a_morale,defender,d_morale = state

        # For now we simply delete war record if no longer needed for reparation tax (NOTE: if we want history table for wars then move these peace redords to other table or reuse not needed wars table column -- marter )
        # If peace is made longer than a week (604800 = one week in seconds)
        if peace_date < (time.time()-604800):
            db.execute("DELETE FROM wars WHERE id=%s", (war_id,))

        # Transfer resources to attacker (winner)
        else:
            if d_morale <= 0:
                winner = attacker
                loser = defender
            else:
                winner = defender
                loser = attacker

            eco = Economy(loser)
            for resource in Economy.resources:
                resource_sel_stat = f"SELECT {resource} FROM resources WHERE id=%s"
                db.execute(resource_sel_stat, (loser,))
                resource_amount = db.fetchone()[0]

                db.execute("SELECT war_type FROM wars WHERE id=%s", (war_id,))
                war_type = db.fetchone()

                # This condition lower or doesn't give reparation_tax at all
                # NOTE: for now it lowers to only 5% (the basic is 20%)
                if war_type == "Raze":
                    eco.transfer_resources(resource, resource_amount*(1/20), winner)
                else:
                    # transfer 20% of all resource (TODO: implement if and alliance won how to give it)
                    eco.transfer_resources(resource, resource_amount*(1/5), winner)

    conn.commit()


@celery.task()
def task_population_growth(): population_growth()


@celery.task()
def task_tax_income(): tax_income()


@celery.task()
def task_generate_province_revenue(): generate_province_revenue()

# Runs once a day
# Transfer X% of all resources (could depends on conditions like Raze war_type) to the winner side after a war


@celery.task()
def task_war_reparation_tax(): war_reparation_tax()


@celery.task()
def task_manpower_increase():
    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))
    db = conn.cursor()

    db.execute("SELECT id FROM users")
    user_ids = db.fetchall()
    for id in user_ids:
        db.execute(
            "SELECT SUM(population) FROM provinces WHERE userid=(%s)", (id[0],))
        population = db.fetchone()[0]
        if population:
            capable_population = population*0.2

            # Currently this is a constant
            army_tradition = 0.1
            produced_manpower = int(capable_population*army_tradition)

            db.execute("SELECT manpower FROM military WHERE id=(%s)", (id[0],))
            manpower = db.fetchone()[0]

            if manpower+produced_manpower >= population:
                produced_manpower = 0

            db.execute("UPDATE military SET manpower=manpower+(%s) WHERE id=(%s)",
                       (produced_manpower, id[0]))

    conn.commit()
    conn.close()