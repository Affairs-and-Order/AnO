import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

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

        user_id = user[0]

        try:
            db.execute("SELECT SUM(population) FROM provinces WHERE userId=%s", (user_id,))
            population = int(db.fetchone()[0])
        except:
            population = 0

        db.execute("SELECT consumer_goods FROM resources WHERE id=%s", (user_id,))
        consumer_goods = int(db.fetchone()[0])
        consumer_goods_needed = round(population * 0.00005)
        new_consumer_goods = consumer_goods - consumer_goods_needed

        db.execute("SELECT gold FROM stats WHERE id=%s", (user_id,))
        money = int(db.fetchone()[0])

        new_income = money + population * 0.01

        if new_consumer_goods >= 0:
            new_income *= 1.5
            db.execute("UPDATE resources SET consumer_goods=%s WHERE id=%s", (new_consumer_goods, user_id))

        db.execute("UPDATE stats SET gold=%s WHERE id=%s", (new_income, user_id,))

        conn.commit()

    conn.close()

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

    rations_per_100k = 4

    for user in users: # Iterates over the list of players

        user_id = user[0]

        db.execute("SELECT id, population FROM provinces WHERE userId=%s", (user_id,))
        provinces = db.fetchall()

        for row in provinces:

            prov_id = row[0] # Gets the province id
            curPop = int(row[1])

            maxPop = 1000000 # Base max population: 1 million

            try:
                db.execute("SELECT cityCount FROM provinces WHERE id=%s", (prov_id,))
                cities = int(db.fetchone()[0])
            except TypeError:
                cities = 0

            if cities > 0:
                maxPop += cities * 2000000 # Each city adds 2m population

            try:
                db.execute("SELECT happiness FROM provinces WHERE id=%s", (prov_id,))
                happiness = int(db.fetchone()[0])
            except TypeError:
                happiness = 0

            try:
                db.execute("SELECT pollution FROM provinces WHERE id=%s", (prov_id,))
                pollution = int(db.fetchone()[0])
            except TypeError:
                pollution = 0

            try:
                db.execute("SELECT productivity FROM provinces WHERE id=%s", (prov_id,))
                productivity = int(db.fetchone()[0])
            except TypeError:
                productivity = 0

            # Each % increases / decreases max population by 0.55
            happiness = (happiness - 50) * 0.55 # The more you have the better 

            # Each % increases / decreases max population by 0.3
            pollution = (pollution - 50) * -0.3 # The less you have the better

            # Each % increases / decreases max population by 0.45
            productivity = (productivity - 50) * 0.45 # The less you have the better

            maxPop += maxPop * happiness + maxPop * pollution + maxPop * productivity

            if maxPop < 1000000: # If max population is less than 1M
                maxPop = 1000000 # Make it 1M

            db.execute("SELECT rations FROM resources WHERE id=%s", (user_id,))
            rations = int(db.fetchone()[0])

            hundred_k = curPop // 100000
            new_rations = rations - (hundred_k * rations_per_100k)

            if new_rations < 1: # If there aren't enough rations for everyone, increase population by 1%
                newPop = curPop + maxPop // 100 # 1% of population
            else: # If there are enough rations for everyone, increase population by 2%
                db.execute("UPDATE resources SET rations=%s WHERE id=%s", (new_rations, user_id))
                newPop = curPop + maxPop // 50 # 2% of population

            db.execute("UPDATE provinces SET population=%s WHERE id=%s", (newPop, prov_id,))
            conn.commit()

    conn.close()

def generate_province_revenue(): # Runs each hour

    # Dictionary for which units give what resources, etc
    infra = {
    ### Electricity (done) ### 
    'coal_burners_plus': {'energy': 4},
    'coal_burners_minus': {'coal': 48},
    'coal_burners_money': 45000,
    'coal_burners_pollution': 30,

    'oil_burners_plus': {'energy': 3},
    'oil_burners_minus': {'coal': 56},
    'oil_burners_money': 60000,
    'oil_burners_pollution': 25,

    'hydro_dams_plus': {'energy': 6},
    'hydro_dams_money': 250000,

    'nuclear_reactors_plus': {'energy': 12}, #  Generates 12 energy to the province
    'nuclear_reactors_minus': {'uranium': 32},
    'nuclear_reactors_money': 1200000, # Costs $1.2 million to operate nuclear reactor for each turn

    'solar_fields_plus': {'energy': 3},
    'solar_fields_money': 150000, # Costs $1.5 million
    ####################

    ### Retail ### (Done)
    'gas_stations_plus': {'consumer_goods': 12},
    'gas_stations_effect': {'pollution': 4},
    'gas_stations_money': 20000, # Costs $20k

    'general_stores_plus': {'consumer_goods': 9},
    'general_stores_pollution': {'pollution': 1},
    'general_stores_money': 35000, # Costs $35k

    'farmers_markets_plus': {'consumer_goods': 16}, # Generates 15 consumer goods,
    'farmers_markets_effect': {'pollution': 6},
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

    'hospitals_effect': {'population': 8},
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
    'farms_plus': {'rations': 30},

    'pumpjacks_money': 10000, # Costs $10k
    'pumpjacks_plus': {'oil': 23},

    'coal_mines_money': 10000, # Costs $10k
    'coal_mines_plus': {'coal': 26},

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

    "pumpjacks", "coal_mines", "bauxite_mines", "copper_mines", "uranium_mines",
    "lead_mines", "iron_mines", 'lumber_mills',

    "component_factories", "steel_mills", "ammunition_factories", "aluminium_refineries",
    "oil_refineries"
    ]

    try:
        db.execute("SELECT id FROM proInfra")
        infra_ids = db.fetchall()
    except:
        infra_ids = []

    for unit in columns:

        try:
            plus_data = next(iter(infra[f'{unit}_plus'].items()))

            plus_resource = plus_data[0]
            plus_amount = plus_data[1]

        except KeyError:
            plus_data = None

        operating_costs = int(infra[f'{unit}_money'])

        try:
            effect_data = next(iter(infra[f'{unit}_effect'].items()))

            effect = effect_data[0]
            effect_amount = effect_data[1]
        except KeyError:
            effect = None

        try:
            effect_2_data = next(iter(infra[f'{unit}_effect_2'].items()))
            
            effect_2 = effect_2_data[0]
            effect_2_amount = effect_2_data[1]
        except KeyError:
            effect_2 = None

        try:
            effect_minus_data = next(iter(infra[f'{unit}_effect_minus'].items()))

            effect_minus = effect_minus_data[0]
            effect_minus_amount = effect_minus_data[1]
        except KeyError:
            effect_minus = None

        # Converting stuff
            # Plus stuff
        try:
            convert_plus_data = next(iter(infra[f'{unit}_convert_plus'].items()))

            convert_plus = convert_plus_data[0]
            convert_plus_amount = convert_plus_data[1]
        except KeyError:
            convert_plus = None
            # Minus stuff
        try:
            convert_minus_data = next(iter(infra[f'{unit}_convert_minus'].items()))

            convert_minus = convert_minus_data[0]
            convert_minus_amount = convert_minus_data[1]
        except KeyError:
            convert_minus = None

        try:
            convert_minus_2_data = next(iter(infra[f'{unit}_convert_minus_2'].items()))

            convert_minus_2 = convert_minus_2_data[0]
            convert_minus_2_amount = convert_minus_2_data[1]
        except KeyError:
            convert_minus_2 = None

        try:
            convert_minus_3_data = next(iter(infra[f'{unit}_convert_minus_3'].items()))

            convert_minus_3 = convert_minus_3_data[0]
            convert_minus_3_amount = convert_minus_3_data[1]
        except KeyError:
            convert_minus_3 = None

        for province_id in infra_ids:

            province_id = province_id[0]

            db.execute("SELECT userId FROM provinces WHERE id=(%s)", (province_id,))
            user_id = db.fetchone()[0]

            unit_amount_stat = f"SELECT {unit} FROM proInfra " + "WHERE id=%s"
            db.execute(unit_amount_stat, (province_id,))
            unit_amount = db.fetchone()[0]

            # If that user doesn't have any units of this type, skip
            if unit_amount == 0:
                continue
            else:

                """
                print(f"Unit: {unit}")
                print(f"Add {plus_amount} to {plus_resource}")
                print(f"Remove ${operating_costs} as operating costs")
                print(f"\n")
                """

                # Removing money operating costs (if user has the money)
                db.execute("SELECT gold FROM stats WHERE id=(%s)", (user_id,))
                current_money = int(db.fetchone()[0])

                if current_money < operating_costs:
                    continue
                else:
                    new_money = current_money - operating_costs
                    db.execute("UPDATE stats SET gold=(%s) WHERE id=(%s)", (new_money, user_id))

                def take_energy():

                    if unit not in energy_units:

                        db.execute("SELECT energy FROM provinces WHERE id=%s", (province_id,))
                        current_energy = int(db.fetchone()[0])

                        new_energy = current_energy - unit_amount

                        if new_energy >= 0:
                            
                            db.execute("UPDATE provinces SET energy=%s WHERE id=%s", (new_energy, province_id,))

                take_energy()

                plus_amount *= unit_amount # Multiply the resource revenue by the amount of units the user has
                operating_costs *= unit_amount # Multiply the operating costs by the amount of units the user has

                # Effect stuff
                if effect != None:
                    effect_amount *= unit_amount # Multiply the effect amount by the amount of units the user has

                if effect_2 != None:
                    effect_2_amount *= unit_amount

                if effect_minus != None:
                    effect_minus_amount *= unit_amount

                    
                province_resources = ["energy", "population", "happiness", "pollution", "productivity", "consumer_spending"]
                percentage_based = ["happiness", "productivity", "consumer_spending", "pollution"]

                user_resources = [
                    "rations", "oil", "coal", "uranium", "bauxite", "lead", "copper",
                    "lumber", "components", "steel", "consumer_goods", "aluminium",
                    "gasoline", "ammunition", "iron"
                ]

                # Function for _plus
                if plus_data != None:

                    if plus_resource in province_resources:

                        cpr_statement = f"SELECT {plus_resource} FROM provinces" + " WHERE id=(%s)"
                        db.execute(cpr_statement, (province_id,))
                        current_plus_resource = int(db.fetchone()[0])

                        # Adding resource
                        new_resource_number = current_plus_resource + plus_amount

                        if plus_resource in percentage_based and new_resource_number > 100:
                            new_resource_number = 100

                        upd_prov_statement = f"UPDATE provinces SET {plus_resource}" + "=(%s) WHERE id=(%s)"
                        db.execute(upd_prov_statement, (new_resource_number, province_id))

                    elif plus_resource in user_resources:
                        
                        cpr_statement = f"SELECT {plus_resource} FROM resources" + " WHERE id=(%s)"
                        db.execute(cpr_statement, (user_id,))
                        current_plus_resource = int(db.fetchone()[0])

                        # Adding resource
                        new_resource_number = current_plus_resource + plus_amount # 12 is how many uranium it generates

                        upd_res_statement = f"UPDATE resources SET {plus_resource}" + "=(%s) WHERE id=(%s)"
                        db.execute(upd_res_statement, (new_resource_number, province_id))
                    else:
                        print(f"unknown plus data: {plus_resource}")

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

                    db.execute(f"UPDATE provinces SET {eff}" + "=%s WHERE id=%s", (new_effect, province_id))

                if effect != None:
                    # Does the effect for "_effect" 
                    do_effect(effect, effect_amount, "+") # Default settings basically
                if effect_2 != None:
                    do_effect(effect_2, effect_2_amount, "+")
                if effect_minus != None:
                    do_effect(effect_minus, effect_minus_amount, "-")

                ## Convert plus
                if convert_plus != None:

                    resource_s_statement = f"SELECT {convert_plus} FROM resources " + "WHERE id=%s"
                    db.execute(resource_s_statement, (user_id,))
                    current_resource = int(db.fetchone()[0])

                    new_resource = current_resource + convert_plus_amount

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

                if convert_minus != None:
                    minus_convert(convert_minus, convert_minus_amount)
                if convert_minus_2 != None:
                    minus_convert(convert_minus_2, convert_minus_2_amount)
                if convert_minus_3 != None:
                    minus_convert(convert_minus_3, convert_minus_3_amount)

        conn.commit() # Commits the changes

    conn.close() # Closes the connection

generate_province_revenue()