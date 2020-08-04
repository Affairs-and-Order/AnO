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
    spies + icbms + nukes
    
    gold = db.execute("SELECT gold FROM stats WHERE id=(?)", (cId,)).fetchone()[0]

    influence = military + gold

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

def get_resource_amount():
    conn = sqlite3.connect('affo/aao.db') # connects to db
    db = conn.cursor()
    session_id = session["user_id"]

    money = db.execute("SELECT gold FROM stats WHERE id=(?)", (session_id,)).fetchone()[0] # DONE

    rations = 0 # db.execute("SELECT rations FROM resources WHERE userId=(?)", (session_id,)).fetchone()[0]
    oil = db.execute("SELECT oil FROM resources WHERE id=(?)", (session_id,)).fetchone()[0] # DONE
    coal = db.execute("SELECT coal FROM resources WHERE id=(?)", (session_id,)).fetchone()[0] # DONE
    uranium = db.execute("SELECT uranium FROM resources WHERE id=(?)", (session_id,)).fetchone()[0] # DONE
    bauxite = db.execute("SELECT bauxite FROM resources WHERE id=(?)", (session_id,)).fetchone()[0] # DONE
    iron = db.execute("SELECT iron FROM resources WHERE id=(?)", (session_id,)).fetchone()[0] # DONE
    lead = db.execute("SELECT lead FROM resources WHERE id=(?)", (session_id,)).fetchone()[0] # DONE
    copper = db.execute("SELECT copper FROM resources WHERE id=(?)", (session_id,)).fetchone()[0] # DONE

    components = db.execute("SELECT components FROM resources WHERE id=(?)", (session_id,)).fetchone()[0]
    steel = db.execute("SELECT steel FROM resources WHERE id=(?)", (session_id,)).fetchone()[0]
    consumer_goods = db.execute("SELECT consumer_goods FROM resources WHERE id=(?)", (session_id,)).fetchone()[0] # DONE

    copper_plates = db.execute("SELECT copper_plates FROM resources WHERE id=(?)", (session_id,)).fetchone()[0]
    aluminium = db.execute("SELECT aluminium FROM resources WHERE id=(?)", (session_id,)).fetchone()[0]
    gasoline = db.execute("SELECT gasoline FROM resources WHERE id=(?)", (session_id,)).fetchone()[0]
    ammunition = db.execute("SELECT ammunition FROM resources WHERE id=(?)", (session_id,)).fetchone()[0]
    
    lst = [money, rations, oil, coal, uranium, bauxite, iron, lead, copper, components, steel, consumer_goods, copper_plates, aluminium, gasoline, ammunition]
    return lst

def try_col():
    conn = sqlite3.connect('affo/aao.db') # connects to db
    db = conn.cursor()
    try:
        inColit = db.execute("SELECT colId FROM coalitions WHERE userId=(?)", (session["user_id"], )).fetchone()[0]
        inCol = f"/coalition/{inColit}"
        return inCol
    except RecursionError:
        inCol = error(404, "Page Not Found")
        return inCol
    except TypeError:
        inCol = error(404, "Page Not Found")
        return inCol