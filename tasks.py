import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

def generate_province_revenue(): # Runs each hour

    infra = {

    ### Electricity ###
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

    ### Retail ###
    'gas_stations_plus': {'consumer_goods': 4},
    'gas_stations_money': 20000, # Costs $20k

    'general_stores_plus': {'consumer_goods': 9},
    'general_stores_money': 35000, # Costs $35k

    'farmers_markets_plus': {'consumer_goods': 15}, # Generates 15 consumer goods
    'farmers_markets_money': 110000, # Costs $110k

    'banks_plus': {'consumer_goods': 25},
    'banks_money': 800000, # Costs $800k
    
    'malls_plus': {'consumer_goods': 22},
    'malls_effect': {'pollution': 10},
    'malls_money': 300000, # Costs $300k
    ##############

    ### Public Works ###
    'city_parks': {'happiness': 3},
    'city_parks_money': 20000, # Costs $20k

    'hospitals': {'happiness': 8},
    'hospitals_money': 60000,

    'libraries': {'happiness': 5},
    'libraries_money': 90000,

    'universities': {'productivity': 12},
    'universities_money': 150000,

    'monorails': {'productivity': 15},
    'monorails_money': 210000,
    ###################

    ### Military ###
    'army_bases_money': 25000, # Costs $25k

    'harbours_money': 35000,

    'aerodomes_money': 55000,

    'admin_buildings_money': 60000,

    'silos_money': 120000,
    #################

    ### Industry ###

    'pumpjacks_money': 10000, # Costs $10k

    'coal_mines_money': 10000, # Costs $10k

    'bauxite_mines_money': 8000, # Costs $8k

    'copper_mines_money': 8000, # Costs $8k

    'uranium_mines_money': 18000, # Costs $18k

    'lead_mines_money': 12000,

    'iron_mines_money': 18000,

    ################

    ### Processing ###
    'component_factories': 220000, # Costs $220k

    'steel_mills': 180000,

    'ammunition_factories': 140000,

    'aluminium_refineries': 150000,

    'oil_refineries': 160000

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

    'army_bases', 'harbours', 'aerodomes', 'admin_buildings', 'silos'
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

            plus = True
        except KeyError:
            plus = False

        operating_costs = int(infra[f'{unit}_money'])

        try:
            effect = infra[f'{unit}_effect'][1]
            effect_amount = int(infra[f'{unit}_effect'][0])
        except KeyError:
            effect = None
            effect_amount = None

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

                if effect_amount != None:
                    effect_amount *= unit_amount # Multiply the effect amount by the amount of units the user has


                # Function for _plus
                if plus == True:

                    db.execute("SELECT %s FROM provinces WHERE id=(%s)", (plus_resource, user_id,))
                    current_plus_resource = db.fetchone()[0]

                    # Adding resource
                    new_resource_number = current_plus_resource + plus_amount # 12 is how many uranium it generates
                    db.execute("UPDATE provinces SET %s=(%s) WHERE id=(%s)", (plus_resource, new_resource_number, user_id))

                # Function for _effect
                if effect != None:

                    effect_select = f"SELECT {effect} FROM provinces " + "WHERE id=%s"
                    db.execute(effect_select, (province_id,))
                    current_effect = int(db.fetchone()[0])

                    new_effect = current_effect + effect_amount
                    db.execute(f"UPDATE provinces SET {effect}" + "=%s WHERE id=%s", (new_effect, province_id))

        conn.commit() # Commits the changes

    conn.close() # Closes the connection

generate_province_revenue()