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
    flying_fortresses = db.execute("SELECT flying_fortresses FROM air WHERE id=(?)", (cId,)).fetchone()[0]
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
    flying_fortresses + fighter_jets + apaches +\
    destroyers + cruisers + submarines + \
    spies + icbms + nukes"""
    
    # gold = db.execute("SELECT gold FROM stats WHERE id=(?)", (cId,)).fetchone()[0]

    influence = 1000 # gold

    return influence

def get_coalition_influence(coalition_id):

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()

    total_influence = 0

    members = db.execute("SELECT userId FROM coalitions WHERE colId=(?)", (coalition_id,)).fetchall()
    for i in members:
        member_influence = get_influence(i[0])
        total_influence += member_influence

    return total_influence

def generate_province_revenue():

    infra = {
    'oil_burners_plus': {'uranium': 12},
    'oil_burners_minus': {'oil': 4},

    'hydro_dams_plus': {'uranium': 8},
    'hydro_dams_minus': {'oil': 2},

    'nuclear_reactors_plus': {'uranium': 24},
    'nuclear_reactors_minus': {'iron': 8},

    'solar_fields_plus': {'iron': 4},
    'solar_fields_minus': {'oil': 0}
    }

    conn = sqlite3.connect('affo/aao.db') # connects to db
    db = conn.cursor()

    columns = ['oil_burners', 'hydro_dams', 'nuclear_reactors', 'solar_fields']

    infra_ids = db.execute("SELECT id FROM proInfra").fetchall()

    for unit in columns:
        plus_data = next(iter(infra[f'{unit}_plus'].items()))

        plus_resource = plus_data[0]
        plus_amount = plus_data[1]

        minus_data = next(iter(infra[f'{unit}_minus'].items()))

        minus_resource = minus_data[0]
        minus_amount = minus_data[1]

        """
        print(f"Unit: {unit}")
        print(f"Add {plus_amount} to {plus_resource}")
        print(f"Remove {minus_amount} of {minus_resource}")
        print(f"\n")
        """
    
        for province_id in infra_ids:

            province_id = province_id[0]

            user_id = db.execute("SELECT userId FROM provinces WHERE id=(?)", (province_id,)).fetchone()[0]

            ### REMOVING
            current_minus_resource = db.execute(f"SELECT {minus_resource} FROM resources WHERE id=(?)", (user_id,)).fetchone()[0]
            if current_minus_resource < minus_amount:
                continue
            else:
                new_minus_resource_amount = current_minus_resource - minus_amount
                db.execute(f"UPDATE resources SET {minus_resource}=(?) WHERE id=(?)", (new_minus_resource_amount, user_id))

                ### ADDING
                current_plus_resource = db.execute(f"SELECT {plus_resource} FROM resources WHERE id=(?)", (user_id,)).fetchone()[0]
                new_resource_number = current_plus_resource + plus_amount # 12 is how many uranium it generates
                db.execute(f"UPDATE resources SET {plus_resource}=(?) WHERE id=(?)", (new_resource_number, user_id))

    conn.commit()
    conn.close()