# FULLY MIGRATED

import os
import psycopg2
from flask import redirect, render_template, session
from functools import wraps
from dotenv import load_dotenv
load_dotenv()


def get_flagname(user_id):
    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))
    db = connection.cursor()
    db.execute("SELECT flag FROM users WHERE id=(%s)", (user_id,))
    flag_name = db.fetchone()[0]

    if flag_name == None:
        flag_name = "default_flag.jpg"

    return flag_name

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

    cId = country_id

    db.execute("""SELECT soldiers, artillery, tanks, fighters, bombers, apaches, submarines,
    destroyers, cruisers, ICBMs, nukes, spies FROM military WHERE id=%s""", (cId,))
    military = db.fetchall()[0]

    soldiers_score = military[0] * 0.02
    artillery_score = military[1] * 1.6
    tanks_score = military[2] * 0.8
    fighters_score = military[3] * 3.5
    bombers_score = military[4] * 2.5
    apaches_score = military[5] * 3.2
    submarines_score = military[6] * 4.5
    destroyers_score = military[7] * 3
    cruisers_score = military[8] * 5.5
    icbms_score = military[9] * 250
    nukes_score = military[10] * 500
    spies_score = military[11] * 25

    """
    except:
        tanks_score = 0
        soldiers_score = 0
        artillery_score = 0
        bombers_score = 0
        fighters_score = 0
        apaches_score = 0
        destroyers_score = 0
        cruisers_score = 0
        submarines_score = 0
        spies_score = 0
        icbms_score = 0
        nukes_score = 0
        print(f"Couldn't get military data for user id: {cId}")
    """

    db.execute("SELECT gold FROM stats WHERE id=(%s)", (cId,))
    money_score = int(db.fetchone()[0]) * 0.00001

    try:
        db.execute("SELECT SUM(cityCount) FROM provinces WHERE userId=(%s)", (cId,))
        cities_score = int(db.fetchone()[0]) * 10
    except:
        cities_score = 0

    try:
        db.execute("SELECT COUNT(id) FROM provinces WHERE userId=(%s)", (cId,))
        provinces_score = int(db.fetchone()[0]) * 300
    except:
        provinces_score = 0

    try:
        db.execute("SELECT SUM(land) FROM provinces WHERE userId=%s", (cId,))
        land_score = db.fetchone()[0] * 10
    except:
        land_score = 0

    db.execute("""SELECT oil + rations + coal + uranium + bauxite + iron + lead + copper + lumber + components + steel,
    consumer_goods + aluminium + gasoline + ammunition FROM resources WHERE id=%s""", (cId,))
    resources_score = db.fetchone()[0] * 0.001

    """
    (# of provinces * 300)+(# of soldiers * 0.02)+(# of artillery*1.6)+(# of tanks*0.8)
    +(# of fighters* 3.5)+(# of bombers *2.5)+(# of apaches *3.2)+(# of subs * 4.5)+
    (# of destroyers *3.0)+(# of cruisers *5.5) + (# of ICBMS*250)+(# of Nukes * 500)
    + (# of spies*25) + (# of total cities * 10) + (# of total land * 10)+
    (total number of rss *0.001)+(total amount of money*0.00001)
    """

    influence = provinces_score + soldiers_score + artillery_score + tanks_score + \
    fighters_score + bombers_score + apaches_score + submarines_score + \
    destroyers_score + cruisers_score + icbms_score + nukes_score + \
    spies_score + cities_score + land_score + resources_score + money_score

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
