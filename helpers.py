# FULLY MIGRATED

import os
import psycopg2
from flask import redirect, render_template, request, session
from functools import wraps
from dotenv import load_dotenv
load_dotenv()



def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id', None):
            return redirect("/login")

        return f(*args, **kwargs)

    return decorated_function

# Check for neccessary values without them user can't access a page
# example: can't access /warchoose or /waramount without enemy_id
def check_required(func):

    @wraps(func)
    def check_session(*args, **kwargs):
        if not session.get("enemy_id", None):
            return redirect("/wars")
        return func(*args, **kwargs)

    return check_session

def error(code, message):
    return render_template("error.html", code=code, message=message)

@login_required
def get_influence(country_id):

    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()
    cId = session["user_id"]
    # re-calculate influence here
    # military score first
    # ground
    db.execute("SELECT tanks FROM military WHERE id=(%s)", (cId,))
    tanks = db.fetchone()[0]
    db.execute("SELECT soldiers FROM military WHERE id=(%s)", (cId,))
    soldiers = db.fetchone()[0]
    db.execute("SELECT artillery FROM military WHERE id=(%s)", (cId,))
    artillery = db.fetchone()[0]
    # air
    db.execute("SELECT bombers FROM military WHERE id=(%s)", (cId,))
    bombers = db.fetchone()[0]
    db.execute("SELECT fighters FROM military WHERE id=(%s)", (cId,))
    fighters = db.fetchone()[0]
    db.execute("SELECT apaches FROM military WHERE id=(%s)", (cId,))
    apaches = db.fetchone()[0]
    # water
    db.execute("SELECT destroyers FROM military WHERE id=(%s)", (cId,))
    destroyers = db.fetchone()[0]
    db.execute("SELECT cruisers FROM military WHERE id=(%s)", (cId,))
    cruisers = db.fetchone()[0]
    db.execute("SELECT submarines FROM military WHERE id=(%s)", (cId,))
    submarines = db.fetchone()[0]
    # special
    db.execute("SELECT spies FROM military WHERE id=(%s)", (cId,))
    spies = db.fetchone()[0]
    db.execute("SELECT ICBMs FROM military WHERE id=(%s)", (cId,))
    icbms = db.fetchone()[0]
    db.execute("SELECT nukes FROM military WHERE id=(%s)", (cId,))
    nukes = db.fetchone()[0]

    militaryScore = tanks * 0.4 + soldiers * 0.01 + artillery * 0.8 + bombers * 1 + fighters * 1 + apaches * 1 + destroyers * 1 + cruisers * 2 + submarines * 1 + spies * 1 + icbms * 3 + nukes * 10

    # civilian score second
    db.execute("SELECT gold FROM stats WHERE id=(%s)", (cId,))
    gold = db.fetchone()[0]

    try:
        db.execute("SELECT SUM(population) FROM provinces WHERE userId=(%s)", (cId,))
        population = int(db.fetchone()[0])
    except:
        population = 0

    try:
        db.execute("SELECT SUM(cityCount) FROM provinces WHERE userId=(%s)", (cId,))
        cities = int(db.fetchone()[0])
    except:
        cities = 0

    try:
        db.execute("SELECT COUNT(id) FROM provinces WHERE userId=(%s)", (cId,))
        provinces = int(db.fetchone()[0])
    except:
        provinces = 0

    # all resources have a set score of 100 gold, which makes score min/maxing a strategy vs balancing your assets
    resources = 0

    db.execute("SELECT * FROM resources WHERE id=(%s)", (cId,))
    resourceList = db.fetchall()

    iterator = iter(resourceList)
    next(iterator) # skip id
    for tuple in iterator:
        resources += tuple[0]

    civilianScore = gold * 0.0001 + population * 0.001 + cities * 10 + provinces * 100 + resources * 0.001

    # user may want military and civilian scores in a score breakdown later in a stats page
    influence = militaryScore + civilianScore
    influence = round(influence)

    return influence


def get_coalition_influence(coalition_id):


    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    total_influence = 0

    db.execute("SELECT userId FROM coalitions WHERE colId=(%s)", (coalition_id,))
    members = db.fetchall()
    for i in members:
        member_influence = get_influence(i[0])
        total_influence += member_influence

    return total_influence

def generate_province_revenue(): # Runs each turn

    infra = {
    ## ELECTRICITY
    'oil_burners_plus': {'energy': 3},
    'oil_burners_money': 60000,
    'oil_burners_pollution': 25,

    'hydro_dams_plus': {'energy': 6},
    'hydro_dams_money': 250000,

    'nuclear_reactors_plus': {'energy': 12}, #  Generates 12 energy to the province
    'nuclear_reactors_money': 1200000, # Costs $1.2 million to operate nuclear reactor for each turn

    'solar_fields_plus': {'energy': 3},
    'solar_fields_money': 150000, # Costs $1.5 million

    ## RETAIL (requires city slots)
    'gas_stations_plus': {'consumer_goods': 4},
    'gas_stations_money': 20000, # Costs $20k

    'general_stores_plus': {'consumer_goods': 9},
    'general_stores_money': 35000, # Costs $35k

    'farmers_markets_plus': {'consumer_goods': 15}, # Generates 15 consumer goods
    'farmers_markets_money': 110000, # Costs $110k

    'malls_plus': {'consumer_goods': 22},
    'malls_money': 300000, # Costs $300k

    'banks_plus': {'consumer_goods': 30},
    'banks_money': 800000, # Costs $800k

    'city_parks': {'happiness': 3},
    'city_parks_money': 20000, # Costs $20k

    'hospitals': {'happiness': 8},
    'hospitals_money': 60000,

    'libraries': {'happiness': 5},
    'libraries_money': 90000,
    # Add productivity too

    'universities': {'productivity': 12},
    'universities_money': 150000,

    'monorails': {'productivity': 15},
    'monorails_money': 210000,

    'army_bases_money': 25000, # Costs $25k

    'harbours_money': 35000,

    'aerodomes_money': 55000,

    'admin_buildings_money': 60000,

    'silos_money': 120000
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

    infra_ids = db.execute("SELECT id FROM proInfra").fetchall()

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
            pollution_amount = int(infra[f'{unit}_pollution'])
        except KeyError:
            pollution_amount = None

        """
        print(f"Unit: {unit}")
        print(f"Add {plus_amount} to {plus_resource}")
        print(f"Remove ${operating_costs} as operating costs")
        print(f"\n")
        """

        for province_id in infra_ids:

            province_id = province_id[0]

            db.execute("SELECT userId FROM provinces WHERE id=(%s)", (province_id,))
            user_id = db.fetchone()[0]

            db.execute("SELECT %s FROM proInfra WHERE id=(%s)", (unit, province_id,))
            unit_amount = db.fetchone()[0]

            if unit_amount == 0:
                continue
            else:
                ### REMOVING RESOURCE

                plus_amount *= unit_amount
                operating_costs *= unit_amount
                if pollution_amount != None:
                    pollution_amount *= unit_amount

                ### ADDING RESOURCES
                if plus:

                    db.execute("SELECT %s FROM provinces WHERE id=(%s)", (plus_resource, user_id,))
                    current_plus_resource = db.fetchone()[0]

                    new_resource_number = current_plus_resource + plus_amount # 12 is how many uranium it generates
                    db.execute("UPDATE provinces SET %s=(%s) WHERE id=(%s)", (plus_resource, new_resource_number, user_id))

                ###

                ### REMOVING MONEY
                db.execute("SELECT gold FROM stats WHERE id=(%s)", (user_id,))
                current_money = int(db.fetchone()[0])

                if current_money < operating_costs:
                    continue
                else:
                    new_money = current_money - operating_costs
                    db.execute("UPDATE stats SET gold=(%s) WHERE id=(%s)", (new_money, user_id))

                    if pollution_amount != None:
                        db.execute("SELECT pollution FROM provinces WHERE id=(%s)", (province_id,))
                        current_pollution = db.fetchone()[0]
                        new_pollution = current_pollution + pollution_amount
                        db.execute("UPDATE provinces SET pollution=(%s) WHERE id=(%s)", (new_pollution, province_id))

                        db.fetchone()[0]

        conn.commit()

    conn.close()
