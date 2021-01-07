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
    
    cId = country_id

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