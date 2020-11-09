import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

def generate_province_revenue(): # Runs each hour

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

    ### Military (done) ###
    'army_bases_money': 25000, # Costs $25k
    'harbours_money': 35000,
    'aerodomes_money': 55000,
    'admin_buildings_money': 60000,
    'silos_money': 120000,
    ################

    ### Industry  ###

    # Requires land slots
    # 4 Producable resources per nation

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

    ### Processing ###
    'component_factories_money': 220000, # Costs $220k
    'component_factories_convert_plus': {'components': 5},

    'steel_mills_money': 180000,
    'steel_mills_convert_plus': {'steel': 15},

    'ammunition_factories_money': 140000,
    'ammunition_factories_convert_plus': {'ammunition': 10},

    'aluminium_refineries_money': 150000,
    'aluminium_refineries_convert_plus': {'aluminium': 12},

    'oil_refineries_money': 160000,
    'oil_refineries_convert_plus': {'gas': 8}

    }

    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))
        
    db = conn.cursor()

    columns = [
    'oil_burners', 'hydro_dams', 'nuclear_reactors', 'solar_fields',
    'gas_stations', 'general_stores', 'farmers_markets', 'malls',
    'banks', 'city_parks', 'hospitals', 'libraries', 'universities', 'monorails',

    "pumpjacks", "coal_mines", "bauxite_mines", "copper_mines", "uranium_mines",
    "lead_mines", "iron_mines",

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
            plus = False

        operating_costs = int(infra[f'{unit}_money'])

        try:
            effect = infra[f'{unit}_effect'][0]
            effect_amount = int(infra[f'{unit}_effect_2'][1])
        except KeyError:
            effect = None
            effect_amount = None

        try:
            effect_2 = infra[f'{unit}_effect_2'][0]
            effect_2_amount = int(infra[f'{unit}_effect_2'][1])
        except KeyError:
            effect_2 = None
            effect_2_amount = None

        try:
            effect_minus = infra[f'{unit}_effect_minus'][0]
            effect_minus_amount = int(infra[f'{unit}_effect_minus'][1])
        except KeyError:
            effect_minus = None
            effect_minus_amount = None

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


                plus_amount *= unit_amount # Multiply the resource revenue by the amount of units the user has
                operating_costs *= unit_amount # Multiply the operating costs by the amount of units the user has

                # Effect stuff
                if effect != None:
                    effect_amount *= unit_amount # Multiply the effect amount by the amount of units the user has

                if effect_2 != None:
                    effect_2_amount *= unit_amount

                if effect_minus != None:
                    effect_minus_amount *= unit_amount

                # Function for _plus
                if plus != False:

                    db.execute("SELECT %s FROM provinces WHERE id=(%s)", (plus_resource, user_id,))
                    current_plus_resource = db.fetchone()[0]

                    # Adding resource
                    new_resource_number = current_plus_resource + plus_amount # 12 is how many uranium it generates
                    db.execute("UPDATE provinces SET %s=(%s) WHERE id=(%s)", (plus_resource, new_resource_number, user_id))

                # Function for completing an effect (adding pollution, etc)
                def do_effect(eff, eff_amount, sign):

                    effect_select = f"SELECT {eff} FROM provinces " + "WHERE id=%s"
                    db.execute(effect_select, (province_id,))
                    current_effect = int(db.fetchone()[0])

                    if sign == "+":
                        new_effect = current_effect + eff_amount
                    elif sign == "-":
                        new_effect = current_effect - eff_amount

                    db.execute(f"UPDATE provinces SET {eff}" + "=%s WHERE id=%s", (new_effect, province_id))

                if effect != None:
                    # Does the effect for "_effect" 
                    do_effect(effect, effect_amount, "+") # Default settings basically
                if effect_2 != None:
                    do_effect(effect_2, effect_2_amount, "+")
                if effect_minus != None:
                    do_effect(effect_minus, effect_minus_amount, "-")


        conn.commit() # Commits the changes

    conn.close() # Closes the connection

generate_province_revenue()