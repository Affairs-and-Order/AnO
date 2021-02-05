import psycopg2
import os
import time
from dotenv import load_dotenv
from attack_scripts import Economy
import variables
load_dotenv()

# Function for calculating tax income
def calc_ti(user_id):

    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = conn.cursor()

    db.execute("SELECT gold FROM stats WHERE id=%s", (user_id,))
    current_money = db.fetchone()[0]

    db.execute("SELECT consumer_goods FROM resources WHERE id=%s", (user_id,))
    consumer_goods = db.fetchone()[0]

    try:
        db.execute("SELECT SUM(population) FROM provinces WHERE userId=%s", (user_id,))
        population = db.fetchone()[0]
        if population is None:
            population = 0

        population = int(population)
        
        consumer_goods_needed = population * 0.00005
        new_consumer_goods = int(consumer_goods - consumer_goods_needed)

        population_score = int(population * 0.075)

        db.execute("SELECT SUM(land) FROM provinces WHERE userId=%s", (user_id,))
        land = db.fetchone()[0]
        if land is None:
            land = 0

        land = int(land)
        land_percentage = land * 0.02 # Land percentage up to 100% 

        if land_percentage > 1:
            land_percentage = 1

        new_income = 0
        new_income += population_score
        new_income = int(new_income)
        new_income *= land_percentage
        new_income = int(new_income)

        if new_consumer_goods >= 0:
            new_income *= 1.75
        else:
            new_consumer_goods = consumer_goods

        new_money = int(current_money + new_income)

        return new_money, new_consumer_goods
    except Exception as e:
        print(f"Error: {e} while calculating tax income for user id: {user_id}")
        return current_money, consumer_goods

def tax_income(): # Function for giving money to players

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

        money, consumer_goods = calc_ti(user_id)

        db.execute("UPDATE stats SET gold=%s WHERE id=%s", (money, user_id))
        db.execute("UPDATE resources SET consumer_goods=%s WHERE id=%s", (consumer_goods, user_id))

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

    maxPop = 1000000 # Base max population: 1 million

    try:
        db.execute("SELECT cityCount FROM provinces WHERE id=%s", (pId,))
        cities = db.fetchone()[0]
    except TypeError:
        conn.rollback()
        cities = 0

    maxPop += cities * 750000 # Each city adds 750,000 population
        
    try:
        db.execute("SELECT land FROM provinces WHERE id=%s", (pId,))
        land = db.fetchone()[0]
    except TypeError:
        conn.rollback()
        land = 0

    maxPop += land * 120000 # Each land slot adds 120,000 population

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

    # Each % increases / decreases max population by 0.55
    happiness = round((happiness - 50) * 0.011, 2) # The more you have the better

    # Each % increases / decreases max population by 0.3
    pollution = round((pollution - 50) * - 0.006, 2) # The less you have the better

    # Each % increases / decreases max population by 0.45
    productivity = round((productivity - 50) * 0.009, 2) # The less you have the better

    ###############################  

    maxPop += (maxPop * happiness) + (maxPop * pollution) + (maxPop * productivity)
    maxPop = round(maxPop)

    if maxPop < 1000000: # If max population is less than 1M
        maxPop = 1000000 # Make it 1M

    hundred_k = curPop // 100000
    rations_per_100k = 4
    new_rations = rations - (hundred_k * rations_per_100k)

    if new_rations < 1: # If there aren't enough rations for everyone, increase population by 1%
        newPop = maxPop // 100 # 1% of population
        new_rations = rations
    else: # If there are enough rations for everyone, increase population by 2%
        newPop = maxPop // 50

    fullPop = curPop + newPop

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

    db.execute("SELECT id FROM provinces")
    provinces = db.fetchall()

    for province_id in provinces:
        province_id = province_id[0]
        try:

            db.execute("SELECT userId FROM provinces WHERE id=%s", (province_id,))
            user_id = db.fetchone()[0]

            db.execute("SELECT rations FROM resources WHERE id=%s", (user_id,))
            current_rations = db.fetchone()[0]

            rations, population = calc_pg(province_id, current_rations)

            db.execute("UPDATE resources SET rations=%s WHERE id=%s", (rations, user_id))
            db.execute("UPDATE provinces SET population=%s WHERE id=%s", (population, province_id))

            conn.commit()

        except Exception as e: 
            conn.rollback()
            print(f"Couldn't complete population growth for province: {province_id}. Exception: {e}")
            continue

    conn.close()

def generate_province_revenue(): # Runs each hour

    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = conn.cursor()

    columns = variables.BUILDINGS

    province_resources = ["energy", "population", "happiness", "pollution", "productivity", "consumer_spending"]
    percentage_based = ["happiness", "productivity", "consumer_spending", "pollution"]

    energy_consumers = variables.ENERGY_CONSUMERS
    user_resources = variables.RESOURCES
    infra = variables.INFRA

    try:
        db.execute("SELECT id FROM proInfra ORDER BY id ASC")
        infra_ids = db.fetchall()
    except:
        infra_ids = []

    for province_id in infra_ids:

        province_id = province_id[0]

        db.execute("SELECT userId FROM provinces WHERE id=%s", (province_id,))
        user_id = db.fetchone()[0]

        for unit in columns:

            try:
                unit_amount_stat = f"SELECT {unit} FROM proInfra " + "WHERE id=%s"
                db.execute(unit_amount_stat, (province_id,))
                unit_amount = db.fetchone()[0]
            except:
                conn.rollback()
                continue

            # If that user doesn't have any units of this type, skip
            if unit_amount == 0:
                continue
            else:

                try:

                    try:
                        effect_minus_data = list(infra[f'{unit}_effect_minus'].items())[0]

                        effect_minus = effect_minus_data[0]
                        effect_minus_amount = effect_minus_data[1]
                    except KeyError:
                        effect_minus = None

                    # Minus stuff
                    try:
                        convert_minus = infra[f'{unit}_convert_minus']
                    except KeyError:
                        convert_minus = []

                    operating_costs = int(infra[f'{unit}_money']) * unit_amount

                    # Removing money operating costs (if user has the money)
                    db.execute("SELECT gold FROM stats WHERE id=%s", (user_id,))
                    current_money = int(db.fetchone()[0])

                    # Boolean for whether a player has enough resources, energy, money to power his building
                    has_enough_stuff = True

                    if current_money < operating_costs:
                        print(f"Couldn't update {unit} for {province_id} as they don't have enough money")
                        has_enough_stuff = False
                    else:
                        new_money = current_money - operating_costs
                        try:
                            db.execute("UPDATE stats SET gold=(%s) WHERE id=(%s)", (new_money, user_id))
                        except:
                            conn.rollback()
                            pass

                    def take_energy():

                        global has_enough_stuff

                        if unit in energy_consumers:

                            db.execute("SELECT energy FROM provinces WHERE id=%s", (province_id,))
                            current_energy = int(db.fetchone()[0])

                            new_energy = current_energy - unit_amount

                            if new_energy < 0:
                                has_enough_stuff = False
                                new_energy = 0

                            db.execute("UPDATE provinces SET energy=%s WHERE id=%s", (new_energy, province_id))

                    take_energy()

                    ## Convert minus
                    def minus_convert(name, amount):

                        global has_enough_stuff

                        resource_statement = f"SELECT {name} FROM resources " + "WHERE id=%s"
                        db.execute(resource_statement, (user_id,))
                        current_resource = int(db.fetchone()[0])

                        new_resource = current_resource - amount

                        if new_resource < 0:
                            has_enough_stuff = False
                            new_resource = 0
                        else:
                            has_enough_stuff = True

                        resource_u_statement = f"UPDATE resources SET {name}" + "=%s WHERE id=%s"
                        db.execute(resource_u_statement, (new_resource, user_id,))

                        return has_enough_stuff

                    for data in convert_minus:

                        data = list(data.items())[0]

                        minus_resource = data[0]
                        minus_amount = data[1] * unit_amount
                        has_enough_stuff = minus_convert(minus_resource, minus_amount)

                    if not has_enough_stuff:
                        print(f"Couldn't update {unit} for province id: {province_id} as they don't have enough stuff")
                        continue

                    try:
                        plus_data = list(infra[f'{unit}_plus'].items())[0]

                        plus_resource = plus_data[0]
                        plus_amount = plus_data[1]

                    except KeyError:
                        plus_data = None

                    try:
                        effect = infra[f'{unit}_effect']
                    except KeyError:
                        effect = []

                    """
                    print(f"Unit: {unit}")
                    print(f"Add {plus_amount} to {plus_resource}")
                    print(f"Remove ${operating_costs} as operating costs")
                    print(f"\n")
                    """

                    if unit == "farms":
                        
                        db.execute("SELECT land FROM provinces WHERE id=%s", (province_id,))
                        land = db.fetchone()[0]

                        plus_amount *= land / 2

                    # Function for _plus
                    if plus_data is not None:

                        plus_amount *= unit_amount # Multiply the resource revenue by the amount of units the user has

                        if plus_resource in province_resources:

                            cpr_statement = f"SELECT {plus_resource} FROM provinces" + " WHERE id=%s"
                            db.execute(cpr_statement, (province_id,))
                            current_plus_resource = int(db.fetchone()[0])

                            # Adding resource
                            new_resource_number = current_plus_resource + plus_amount

                            if plus_resource in percentage_based and new_resource_number > 100:
                                new_resource_number = 100

                            if new_resource_number < 0:
                                new_resource_number = 0

                            upd_prov_statement = f"UPDATE provinces SET {plus_resource}" + "=(%s) WHERE id=(%s)"
                            db.execute(upd_prov_statement, (new_resource_number, province_id))

                        elif plus_resource in user_resources:

                            cpr_statement = f"SELECT {plus_resource} FROM resources" + " WHERE id=%s"
                            db.execute(cpr_statement, (user_id,))
                            current_plus_resource = int(db.fetchone()[0])

                            # Adding resource
                            new_resource_number = current_plus_resource + plus_amount # 12 is how many uranium it generates

                            if new_resource_number < 0:
                                new_resource_number = 0

                            upd_res_statement = f"UPDATE resources SET {plus_resource}" + "=%s WHERE id=%s"
                            db.execute(upd_res_statement, (new_resource_number, user_id,))

                    # Function for completing an effect (adding pollution, etc)
                    def do_effect(eff, eff_amount, sign):

                        effect_select = f"SELECT {eff} FROM provinces " + "WHERE id=%s"
                        db.execute(effect_select, (province_id,))
                        current_effect = int(db.fetchone()[0])

                        if sign == "+":
                            new_effect = current_effect + eff_amount
                        elif sign == "-":
                            new_effect = current_effect - eff_amount

                        if eff in percentage_based:
                            if new_effect > 100:
                                new_effect = 100
                            if new_effect < 0:
                                new_effect = 0
                        else:
                            if new_effect < 0:
                                new_effect = 0

                        eff_update = f"UPDATE provinces SET {eff}" + "=%s WHERE id=%s"
                        db.execute(eff_update, (new_effect, province_id))

                    for data in effect:

                        data = list(data.items())[0]

                        effect_resource = data[0]
                        effect_amount = data[1] * unit_amount
                        do_effect(effect_resource, effect_amount, "+")

                    if effect_minus is not None:
                        effect_minus_amount *= unit_amount
                        do_effect(effect_minus, effect_minus_amount, "-")

                    conn.commit() # Commits the changes
                
                except Exception as e:
                    conn.rollback()
                    print(f"Couldn't update {unit} for province id: {province_id} due to exception: {e}")
                    continue

            print(f"Successfully updated {unit} for for province id: {province_id}")

        print(f"Successfully updated units for province id: {province_id}")
            
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
