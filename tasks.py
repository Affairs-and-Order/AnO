import psycopg2
import os
import time
from dotenv import load_dotenv
from attack_scripts import Economy
load_dotenv()

# Seems to be working as expected
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

    for user in users:

        try:

            user_id = user[0]

            try:
                db.execute("SELECT SUM(population) FROM provinces WHERE userId=%s", (user_id,))
                population = int(db.fetchone()[0])
            except:
                conn.rollback()
                population = 0

            db.execute("SELECT consumer_goods FROM resources WHERE id=%s", (user_id,))
            consumer_goods = int(db.fetchone()[0])
            consumer_goods_needed = round(population * 0.00005)
            new_consumer_goods = consumer_goods - consumer_goods_needed

            population_score = population * 0.01

            try:
                db.execute("SELECT SUM(land) FROM provinces WHERE userId=%s", (user_id,))
                land = db.fetchone()[0]
            except:
                conn.rollback()
                land = 0

            land_percentage = land * 0.02 # Land percentage up to 100% 

            if land_percentage > 1:
                land_percentage = 1

            new_income = population_score

            new_income += new_income * land_percentage

            if new_consumer_goods >= 0:
                new_income *= 1.5
                try:
                    db.execute("UPDATE resources SET consumer_goods=%s WHERE id=%s", (new_consumer_goods, user_id))
                except:
                    conn.rollback()
                    pass

            try:
                db.execute("UPDATE stats SET gold=gold+%s WHERE id=%s", (new_income, user_id,))
            except:
                conn.rollback()
                pass

            conn.commit()

        except:
            conn.rollback()
            continue

    conn.close()

# Seems to be working as expected
def population_growth(): # Function for growing population

    conn = psycopg2.connect(
    database=os.getenv("PG_DATABASE"),
    user=os.getenv("PG_USER"),
    password=os.getenv("PG_PASSWORD"),
    host=os.getenv("PG_HOST"),
    port=os.getenv("PG_PORT"))

    db = conn.cursor()

    db.execute("SELECT id FROM users")
    users = db.fetchall()


    for user in users: # Iterates over the list of players

        user_id = user[0]

        try:
            db.execute("SELECT id, population FROM provinces WHERE userId=%s", (user_id,))
            provinces = db.fetchall()
        except:
            conn.rollback()
            provinces = []

        for row in provinces:

            try:

                prov_id = row[0] # Gets the province id
                curPop = row[1]

                maxPop = 1000000 # Base max population: 1 million

                try:
                    db.execute("SELECT cityCount FROM provinces WHERE id=%s", (prov_id,))
                    cities = int(db.fetchone()[0])
                except TypeError:
                    conn.rollback()
                    cities = 0

                if cities > 0:
                    maxPop += cities * 750000 # Each city adds 750,000 population

                try:
                    db.execute("SELECT happiness FROM provinces WHERE id=%s", (prov_id,))
                    happiness = int(db.fetchone()[0])
                except TypeError:
                    conn.rollback()
                    happiness = 0

                try:
                    db.execute("SELECT pollution FROM provinces WHERE id=%s", (prov_id,))
                    pollution = int(db.fetchone()[0])
                except TypeError:
                    conn.rollback()
                    pollution = 0

                try:
                    db.execute("SELECT productivity FROM provinces WHERE id=%s", (prov_id,))
                    productivity = int(db.fetchone()[0])
                except TypeError:
                    conn.rollback()
                    productivity = 0

                # Everything working until here as expected

                ### ALL WORKING AS EXPECTED ###

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

                db.execute("SELECT rations FROM resources WHERE id=%s", (user_id,))
                rations = int(db.fetchone()[0])

                hundred_k = curPop // 100000
                rations_per_100k = 4
                new_rations = rations - (hundred_k * rations_per_100k)

                if new_rations < 1: # If there aren't enough rations for everyone, increase population by 1%
                    newPop = maxPop // 100 # 1% of population
                else: # If there are enough rations for everyone, increase population by 2%
                    newPop = maxPop // 50
                    db.execute("UPDATE resources SET rations=%s WHERE id=%s", (new_rations, user_id))

                db.execute("UPDATE provinces SET population=population+%s WHERE id=%s", (newPop, prov_id,))
                conn.commit()

            except Exception as e: 
                conn.rollback()
                print(f"Couldn't complete population growth for province: {prov_id}. Exception: {e}")
                continue

    conn.close()

def generate_province_revenue(): # Runs each hour

    # Dictionary for which units give what resources, etc
    infra = {
    ### Electricity (done) ###
    'coal_burners_plus': {'energy': 4},
    'coal_burners_minus': {'coal': 48},
    'coal_burners_money': 45000,
    'coal_burners_pollution': 7,

    'oil_burners_plus': {'energy': 3},
    'oil_burners_minus': {'oil': 56},
    'oil_burners_money': 60000,
    'oil_burners_pollution': 3,

    'hydro_dams_plus': {'energy': 6},
    'hydro_dams_money': 250000,

    'nuclear_reactors_plus': {'energy': 12}, #  Generates 12 energy to the province
    'nuclear_reactors_minus': {'uranium': 32},
    'nuclear_reactors_money': 1200000, # Costs $1.2 million to operate nuclear reactor for each turn

    'solar_fields_plus': {'energy': 3},
    'solar_fields_money': 150000, # Costs $1.5 million
    ####################

    ### Retail ### (Done)
    'gas_stations_plus': {'consumer_goods': 8},
    'gas_stations_effect': {'pollution': 4},
    'gas_stations_money': 20000, # Costs $20k

    'general_stores_plus': {'consumer_goods': 12},
    'general_stores_pollution': {'pollution': 2},
    'general_stores_money': 35000, # Costs $35k

    'farmers_markets_plus': {'consumer_goods': 17}, # Generates 15 consumer goods,
    'farmers_markets_effect': {'pollution': 5},
    'farmers_markets_money': 110000, # Costs $110k

    'banks_plus': {'consumer_goods': 25},
    'banks_money': 320000, # Costs $320k

    'malls_plus': {'consumer_goods': 34},
    'malls_effect': {'pollution': 10},
    'malls_money': 750000, # Costs $750k
    ##############

    ### Public Works ### (Done)
    'libraries_effect': {'happiness': 2},
    'libraries_effect_2': {'productivity': 2},
    'libraries_money': 90000,

    'city_parks_effect': {'happiness': 3},
    'city_parks_effect_minus': {'pollution': 6},
    'city_parks_money': 20000, # Costs $20k

    'hospitals_effect': {'happiness': 9},   
    'hospitals_money': 60000,

    'universities_effect': {'productivity': 6},
    'universities_effect_2': {'happiness': 6},
    'universities_money': 150000,

    'monorails_effect': {'productivity': 12},
    'monorails_effect_minus': {'pollution': 10}, # Removes 10 pollution
    'monorails_money': 210000,
    ###################

    ### Military (Done) ###
    'army_bases_money': 25000, # Costs $25k
    'harbours_money': 35000,
    'aerodomes_money': 55000,
    'admin_buildings_money': 60000,
    'silos_money': 120000,
    ################

    ### Industry (Done) ###

    'farms_money': 3000, # Costs $3k
    'farms_plus': {'rations': 8},
    'farms_pollution': 1,

    'pumpjacks_money': 10000, # Costs $10k
    'pumpjacks_plus': {'oil': 23},
    'pumpjacks_pollution': 2,

    'coal_mines_money': 10000, # Costs $10k
    'coal_mines_plus': {'coal': 26},
    'coal_mines_pollution': 2,

    'bauxite_mines_money': 8000, # Costs $8k
    'bauxite_mines_plus': {'bauxite': 20},

    'copper_mines_money': 8000, # Costs $8k
    'copper_mines_plus': {'copper': 32},

    'uranium_mines_money': 18000, # Costs $18k
    'uranium_mines_plus': {'uranium': 12},

    'lead_mines_money': 12000,
    'lead_mines_plus': {'lead': 18},

    'iron_mines_money': 18000,
    'iron_mines_plus': {'iron': 25},

    'lumber_mills_money': 7500,
    'lumber_mills_plus': {'lumber': 32},
    'lumber_mills_pollution': 1,

    ################

    ### Processing (Done) ###
    'component_factories_money': 220000, # Costs $220k
    'component_factories_convert_minus': {'copper': 20},
    'component_factories_convert_minus_2': {'steel': 10},
    'component_factories_convert_minus_3': {'aluminium': 15},
    'component_factories_convert_plus': {'components': 5},

    'steel_mills_money': 180000,
    'steel_mills_convert_minus': {'coal': 35},
    'steel_mills_convert_minus_2': {'iron': 35},
    'steel_mills_convert_plus': {'steel': 15},

    'ammunition_factories_money': 140000,
    'ammunition_factories_convert_minus': {'copper': 10},
    'ammunition_factories_convert_minus_2': {'lead': 20},
    'ammunition_factories_convert_plus': {'ammunition': 10},

    'aluminium_refineries_money': 150000,
    'aluminium_refineries_convert_minus': {'bauxite': 15},
    'aluminium_refineries_convert_plus': {'aluminium': 12},

    'oil_refineries_money': 160000,
    'oil_refineries_convert_minus': {'oil': 20},
    'oil_refineries_convert_plus': {'gasoline': 8}
    }

    energy_units = ["coal_burners", "oil_burners", "hydro_dams", "nuclear_reactors", "solar_fields"]

    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = conn.cursor()

    columns = [
    'coal_burners', 'oil_burners', 'hydro_dams', 'nuclear_reactors', 'solar_fields',
    'gas_stations', 'general_stores', 'farmers_markets', 'malls',
    'banks', 'city_parks', 'hospitals', 'libraries', 'universities', 'monorails',

    "farms", "pumpjacks", "coal_mines", "bauxite_mines", "copper_mines", "uranium_mines",
    "lead_mines", "iron_mines", 'lumber_mills',

    "component_factories", "steel_mills", "ammunition_factories", "aluminium_refineries",
    "oil_refineries"
    ]

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
                        plus_data = list(infra[f'{unit}_plus'].items())[0]

                        plus_resource = plus_data[0]
                        plus_amount = plus_data[1]

                    except KeyError:
                        plus_data = None

                    operating_costs = int(infra[f'{unit}_money'])

                    try:
                        effect_data = list(infra[f'{unit}_effect'].items())[0]

                        effect = effect_data[0]
                        effect_amount = effect_data[1]
                    except KeyError:
                        effect = None

                    try:
                        effect_2_data = list(infra[f'{unit}_effect_2'].items())[0]

                        effect_2 = effect_2_data[0]
                        effect_2_amount = effect_2_data[1]
                    except KeyError:
                        effect_2 = None

                    try:
                        effect_minus_data = list(infra[f'{unit}_effect_minus'].items())[0]

                        effect_minus = effect_minus_data[0]
                        effect_minus_amount = effect_minus_data[1]
                    except KeyError:
                        effect_minus = None

                    # Converting stuff
                        # Plus stuff
                    try:
                        convert_plus_data = list(infra[f'{unit}_convert_plus'].items())[0]

                        convert_plus = convert_plus_data[0]
                        convert_plus_amount = convert_plus_data[1]
                    except KeyError:
                        convert_plus = None
                        # Minus stuff
                    try:
                        convert_minus_data = list(infra[f'{unit}_convert_minus'].items())[0]

                        convert_minus = convert_minus_data[0]
                        convert_minus_amount = convert_minus_data[1]
                    except KeyError:
                        convert_minus = None

                    try:
                        convert_minus_2_data = list(infra[f'{unit}_convert_minus_2'].items())[0]

                        convert_minus_2 = convert_minus_2_data[0]
                        convert_minus_2_amount = convert_minus_2_data[1]
                    except KeyError:
                        convert_minus_2 = None

                    try:
                        convert_minus_3_data = list(infra[f'{unit}_convert_minus_3'].items())[0]

                        convert_minus_3 = convert_minus_3_data[0]
                        convert_minus_3_amount = convert_minus_3_data[1]
                    except KeyError:
                        convert_minus_3 = None


                    """
                    print(f"Unit: {unit}")
                    print(f"Add {plus_amount} to {plus_resource}")
                    print(f"Remove ${operating_costs} as operating costs")
                    print(f"\n")
                    """

                    # Removing money operating costs (if user has the money)
                    db.execute("SELECT gold FROM stats WHERE id=(%s)", (user_id,))
                    current_money = int(db.fetchone()[0])

                    operating_costs *= unit_amount # Multiply the operating costs by the amount of units the user has

                    if current_money < operating_costs:
                        continue
                    else:
                        new_money = current_money - operating_costs
                        if new_money < 0:
                            new_money = 0
                        try:
                            db.execute("UPDATE stats SET gold=(%s) WHERE id=(%s)", (new_money, user_id))
                        except:
                            conn.rollback()
                            pass

                    def take_energy():

                        if unit not in energy_units:

                            db.execute("SELECT energy FROM provinces WHERE id=%s", (province_id,))
                            current_energy = int(db.fetchone()[0])

                            new_energy = current_energy - unit_amount

                            if new_energy < 0:
                                new_energy = 0

                            db.execute("UPDATE provinces SET energy=%s WHERE id=%s", (new_energy, province_id))

                    take_energy()

                    if unit == "farms":
                        
                        db.execute("SELECT land FROM provinces WHERE id=%s", (province_id,))
                        land = db.fetchone()[0]

                        plus_amount *= land

                    province_resources = ["energy", "population", "happiness", "pollution", "productivity", "consumer_spending"]
                    percentage_based = ["happiness", "productivity", "consumer_spending", "pollution"]

                    user_resources = [
                        "rations", "oil", "coal", "uranium", "bauxite", "lead", "copper",
                        "lumber", "components", "steel", "consumer_goods", "aluminium",
                        "gasoline", "ammunition", "iron"
                    ]

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

                    if effect is not None:
                        effect_amount *= unit_amount # Multiply the effect amount by the amount of units the user has
                        do_effect(effect, effect_amount, "+") # Default settings basically
                    if effect_2 is not None:
                        effect_2_amount *= unit_amount
                        do_effect(effect_2, effect_2_amount, "+")
                    if effect_minus is not None:
                        effect_minus_amount *= unit_amount
                        do_effect(effect_minus, effect_minus_amount, "-")

                    ## Convert plus
                    if convert_plus is not None:

                        convert_plus_amount *= unit_amount

                        resource_s_statement = f"SELECT {convert_plus} FROM resources " + "WHERE id=%s"
                        db.execute(resource_s_statement, (user_id,))
                        current_resource = int(db.fetchone()[0])

                        new_resource = current_resource + convert_plus_amount

                        if new_resource < 0:
                            new_resource = 0

                        resource_u_statement = f"UPDATE resources SET {convert_plus}" + "=%s WHERE id=%s"
                        db.execute(resource_u_statement, (new_resource, user_id,))
                    ##

                    ## Convert minus
                    def minus_convert(name, amount):

                        resource_statement = f"SELECT {name} FROM resources " + "WHERE id=%s"
                        db.execute(resource_statement, (user_id,))
                        current_resource = int(db.fetchone()[0])

                        new_resource = current_resource - amount

                        if new_resource < 0:
                            new_resource = 0

                        resource_u_statement = f"UPDATE resources SET {name}" + "=%s WHERE id=%s"
                        db.execute(resource_u_statement, (new_resource, user_id,))

                    if convert_minus is not None:
                        convert_minus_amount *= unit_amount
                        minus_convert(convert_minus, convert_minus_amount)
                    if convert_minus_2 is not None:
                        convert_minus_2_amount *= unit_amount
                        minus_convert(convert_minus_2, convert_minus_2_amount)
                    if convert_minus_3 is not None:
                        convert_minus_3_amount *= unit_amount
                        minus_convert(convert_minus_3, convert_minus_3_amount)

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
