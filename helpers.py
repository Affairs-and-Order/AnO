import os
import sqlite3
from flask import redirect, render_template, request, session
from functools import wraps


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def error(code, message):
    return render_template("error.html", code=code, message=message)


def get_influence(country_id):
    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()
    cId = country_id
    # ground

    """
    tanks = db.execute("SELECT tanks FROM ground WHERE id=(?)", (cId,)).fetchone()[0]
    soldiers = db.execute("SELECT soldiers FROM ground WHERE id=(?)", (cId,)).fetchone()[0]
    artillery = db.execute("SELECT artillery FROM ground WHERE id=(?)", (cId,)).fetchone()[0]
    connection.commit()
    # air
    bombers = db.execute("SELECT bombers FROM air WHERE id=(?)", (cId,)).fetchone()[0]
    fighter_jets = db.execute("SELECT fighter_jets FROM air WHERE id=(?)", (cId,)).fetchone()[0]
    apaches = db.execute("SELECT apaches FROM air WHERE id=(?)", (cId,)).fetchone()[0]
    connection.commit()
    # water
    destroyers = db.execute("SELECT destroyers FROM water WHERE id=(?)", (cId,)).fetchone()[0]
    cruisers = db.execute("SELECT cruisers FROM water WHERE id=(?)", (cId,)).fetchone()[0]
    submarines = db.execute("SELECT submarines FROM water WHERE id=(?)", (cId,)).fetchone()[0]
    connection.commit()
    # special
    spies = db.execute("SELECT spies FROM special WHERE id=(?)", (cId,)).fetchone()[0]
    icbms = db.execute("SELECT ICBMs FROM special WHERE id=(?)", (cId,)).fetchone()[0]
    nukes = db.execute("SELECT nukes FROM special WHERE id=(?)", (cId,)).fetchone()[0]

    military = tanks + soldiers + artillery + \
    bombers + fighter_jets + apaches +\
    destroyers + cruisers + submarines + \
    spies + icbms + nukes"""

    # gold = db.execute("SELECT gold FROM stats WHERE id=(?)", (cId,)).fetchone()[0]

    influence = 1000  # gold

    return influence


def get_coalition_influence(coalition_id):

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()

    total_influence = 0

    members = db.execute(
        "SELECT userId FROM coalitions WHERE colId=(?)", (coalition_id,)).fetchall()
    for i in members:
        member_influence = get_influence(i[0])
        total_influence += member_influence

    return total_influence


def generate_province_revenue():  # Runs each turn

    infra = {
        # ELECTRICITY
        'oil_burners_plus': {'energy': 3},
        'oil_burners_money': 60000,
        'oil_burners_pollution': 25,

        'hydro_dams_plus': {'energy': 6},
        'hydro_dams_money': 250000,

        # Generates 12 energy to the province
        'nuclear_reactors_plus': {'energy': 12},
        # Costs $1.2 million to operate nuclear reactor for each turn
        'nuclear_reactors_money': 1200000,

        'solar_fields_plus': {'energy': 3},
        'solar_fields_money': 150000,  # Costs $1.5 million

        # RETAIL (requires city slots)
        'gas_stations_plus': {'consumer_goods': 4},
        'gas_stations_money': 20000,  # Costs $20k

        'general_stores_plus': {'consumer_goods': 9},
        'general_stores_money': 35000,  # Costs $35k

        # Generates 15 consumer goods
        'farmers_markets_plus': {'consumer_goods': 15},
        'farmers_markets_money': 110000,  # Costs $110k

        'malls_plus': {'consumer_goods': 22},
        'malls_money': 300000,  # Costs $300k

        'banks_plus': {'consumer_goods': 30},
        'banks_money': 800000,  # Costs $800k
    }

    conn = sqlite3.connect('affo/aao.db')  # connects to db
    db = conn.cursor()

    columns = ['oil_burners', 'hydro_dams', 'nuclear_reactors', 'solar_fields']

    infra_ids = db.execute("SELECT id FROM proInfra").fetchall()

    for unit in columns:

        plus_data = next(iter(infra[f'{unit}_plus'].items()))

        plus_resource = plus_data[0]
        plus_amount = plus_data[1]

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

            user_id = db.execute(
                "SELECT userId FROM provinces WHERE id=(?)", (province_id,)).fetchone()[0]

            unit_amount = db.execute(
                f"SELECT {unit} FROM proInfra WHERE id=(?)", (province_id,)).fetchone()[0]

            if unit_amount == 0:
                continue
            else:
                # REMOVING RESOURCE

                plus_amount *= unit_amount
                operating_costs *= unit_amount
                if pollution_amount != None:
                    pollution_amount *= unit_amount

                # ADDING ENERGY
                current_plus_resource = db.execute(
                    f"SELECT {plus_resource} FROM provinces WHERE id=(?)", (user_id,)).fetchone()[0]
                new_resource_number = current_plus_resource + \
                    plus_amount  # 12 is how many uranium it generates
                db.execute(
                    f"UPDATE provinces SET {plus_resource}=(?) WHERE id=(?)", (new_resource_number, user_id))
                # REMOVING MONEY
                current_money = int(db.execute(
                    "SELECT gold FROM stats WHERE id=(?)", (user_id,)).fetchone()[0])
                if current_money < operating_costs:
                    continue
                else:
                    new_money = current_money - operating_costs
                    db.execute(
                        "UPDATE stats SET gold=(?) WHERE id=(?)", (new_money, user_id))
                    if pollution_amount != None:
                        current_pollution = db.execute(
                            "SELECT pollution FROM provinces WHERE id=(?)", (province_id,)).fetchone()[0]
                        new_pollution = current_pollution + pollution_amount
                        db.execute(
                            "UPDATE provinces SET pollution=(?) WHERE id=(?)", (new_pollution, province_id))

        conn.commit()

    conn.close()
