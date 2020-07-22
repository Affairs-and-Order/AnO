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