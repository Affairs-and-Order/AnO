from flask import Flask, request, render_template, session, redirect, flash
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
import datetime
import _pickle as pickle
import random
from celery import Celery
from helpers import login_required, error
import sqlite3
# from celery.schedules import crontab # arent currently using but will be later on
from helpers import get_influence, get_coalition_influence
# Game.ping() # temporarily removed this line because it might make celery not work

from attack_scripts import Military

app = Flask(__name__)


# import written packages DONT U DARE PUT THESE IMPORTS ABOVE `app=Flask(__name__) or it causes a circular import since these files import app themselves!`
from testroutes import testfunc
from wars import wars, find_targets
from login import login
from signup import signup
from countries import country, countries, update_info
from coalitions import leave_col, join_col, coalitions, coalition, establish_coalition, my_coalition, removing_requests, adding
from military import military, military_sell_buy
from province import createprovince, province, provinces, province_sell_buy
from market import market, buy_market_offer, marketoffer, my_offers
from discord import update_discord

#basic cache configuration
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config["CELERY_BROKER_URL"] = 'amqp://ano:ano@localhost:5672/ano'
app.config["CELERY_RESULT_BACKEND"] = 'amqp://ano:ano@localhost:5672/ano'

celery_beat_schedule = {
    "population_growth": {
        "task": "app.populationGrowth",
        # Run every 15 seconds
        "schedule": 15.0,
    },
    "province_infrastructure": {
        "task": "app.generate_province_revenue",
        # Run every 10 seconds
        "schedule": 10.0
    }
}

"""
    "check_war": {
        "task": "app.warPing",
        # Run every day
        "schedule": 8600.0,
    },

    "increase_supplies": {
        "task": "app.increaseSupplies",
        # Runs every hour
        "schedule": 3600.0,
    }
"""


# Initialize Celery and update its config
celery = Celery(app.name)
celery.conf.update(
    result_backend=app.config["CELERY_RESULT_BACKEND"],
    broker_url=app.config["CELERY_BROKER_URL"],
    timezone="UTC",
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    beat_schedule=celery_beat_schedule,
)

@celery.task()
def populationGrowth():
    conn = sqlite3.connect('affo/aao.db') # connects to db
    db = conn.cursor()
    pop = db.execute("SELECT population, id FROM stats").fetchall() # selects id, population from the stats table and gets all the results for it

    for row in pop: # iterates over every result in population
        user_id = row[1] # sets the user_id variable to the "id" result from the query
        curPop = row[0]  # sets the current population variable to the "population" result from the query
        newPop = curPop + (int(curPop/10)) # gets the current population value and adds the same value / 10 to it
        db.execute("UPDATE stats SET population=(?) WHERE id=(?)", (newPop, user_id,)) # updates the db with the new value for population
        conn.commit() # commits everything new
    conn.close()

@celery.task()
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
    }

    conn = sqlite3.connect('affo/aao.db') # connects to db
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

            user_id = db.execute("SELECT userId FROM provinces WHERE id=(?)", (province_id,)).fetchone()[0]

            unit_amount = db.execute(f"SELECT {unit} FROM proInfra WHERE id=(?)", (province_id,)).fetchone()[0]

            if unit_amount == 0:
                continue
            else:
                ### REMOVING RESOURCE

                plus_amount *= unit_amount
                operating_costs *= unit_amount
                if pollution_amount != None:
                    pollution_amount *= unit_amount

                ### ADDING ENERGY
                current_plus_resource = db.execute(f"SELECT {plus_resource} FROM provinces WHERE id=(?)", (user_id,)).fetchone()[0]
                new_resource_number = current_plus_resource + plus_amount # 12 is how many uranium it generates
                db.execute(f"UPDATE provinces SET {plus_resource}=(?) WHERE id=(?)", (new_resource_number, user_id))
                ### REMOVING MONEY
                current_money = int(db.execute("SELECT gold FROM stats WHERE id=(?)", (user_id,)).fetchone()[0])
                if current_money < operating_costs:
                    continue
                else:
                    new_money = current_money - operating_costs
                    db.execute("UPDATE stats SET gold=(?) WHERE id=(?)", (new_money, user_id))
                    if pollution_amount != None:
                        current_pollution = db.execute("SELECT pollution FROM provinces WHERE id=(?)", (province_id,)).fetchone()[0]
                        new_pollution = current_pollution + pollution_amount
                        db.execute("UPDATE provinces SET pollution=(?) WHERE id=(?)", (new_pollution, province_id))

        conn.commit()

    conn.close()

"""
# runs once a day
@celery.task()
def warPing():
    connection = sqlite3.connect("affo/aoo.db")
    cursor = connection.cursor()
    for user in cursor.execute(f"SELECT id FROM war", ()).fetchall():
        # war has lasted more than 3 days, end the war
        if cursor.execute(f"SELECT duration FROM war WHERE id={user}").fetchone()[0] > 3:
            nationObject = pickle.load(cursor.execute(f"SELECT nation FROM users WHERE id={user}").fetchone()[0])
            enemyID = cursor.execute(f"SELECT enemy FROM war WHERE id={user}").fetchone()[0]

            enemyObject = pickle.load(cursor.execute(f"SELECT nation FROM users WHERE id={enemyID}").fetchone()[0])

        # otherwise, update the duration of the war
        elif cursor.execute(f"SELECT duration FROM war WHERE id={user}").fetchone()[0] < 3:
            currentDuration = cursor.execute(f"SELECT duration FROM war WHERE id={user}").fetchone()[0]
            cursor.execute(f"INSERT INTO war (duration)  VALUES ({currentDuration + 1},)", ())
            connection.commit()

# runs once every hour
@celery.task()
def increaseSupplies():
    connection = sqlite3.connect("affo/aoo.db")
    cursor = connection.cursor()
    for user in cursor.execute(f"SELECT id FROM users").fetchall():
        for supplies in cursor.execute(f"SELECT supplies FROM war WHERE id={user[0]}").fetchall():
            increasedSupplies = supplies[0] + 100
            cursor.execute(f"INSERT INTO war (supplies) VALUES ({increasedSupplies} WHERE id={user[0]})")
            connection.commit()

# runs once a day
@celery.task()
def eventCheck():
    rng = random.randint(1, 100)
    events = {
    }
    if rng == 50:
        pass
    # will decide if natural disasters occure
"""

@app.context_processor
def inject_user():
    def get_resource_amount():
        conn = sqlite3.connect('affo/aao.db') # connects to db
        db = conn.cursor()
        session_id = session["user_id"]

        money = db.execute("SELECT gold FROM stats WHERE id=(?)", (session_id,)).fetchone()[0] # DONE

        rations = db.execute("SELECT rations FROM resources WHERE id=(?)", (session_id,)).fetchone()[0]
        oil = db.execute("SELECT oil FROM resources WHERE id=(?)", (session_id,)).fetchone()[0] # DONE
        coal = db.execute("SELECT coal FROM resources WHERE id=(?)", (session_id,)).fetchone()[0] # DONE
        uranium = db.execute("SELECT uranium FROM resources WHERE id=(?)", (session_id,)).fetchone()[0] # DONE
        bauxite = db.execute("SELECT bauxite FROM resources WHERE id=(?)", (session_id,)).fetchone()[0] # DONE
        iron = db.execute("SELECT iron FROM resources WHERE id=(?)", (session_id,)).fetchone()[0] # DONE
        lead = db.execute("SELECT lead FROM resources WHERE id=(?)", (session_id,)).fetchone()[0] # DONE
        copper = db.execute("SELECT copper FROM resources WHERE id=(?)", (session_id,)).fetchone()[0] # DONE
        lumber = db.execute("SELECT lumber FROM resources WHERE id=(?)", (session_id,)).fetchone()[0] # DONE

        components = db.execute("SELECT components FROM resources WHERE id=(?)", (session_id,)).fetchone()[0]
        steel = db.execute("SELECT steel FROM resources WHERE id=(?)", (session_id,)).fetchone()[0]
        consumer_goods = db.execute("SELECT consumer_goods FROM resources WHERE id=(?)", (session_id,)).fetchone()[0] # DONE

        aluminium = db.execute("SELECT aluminium FROM resources WHERE id=(?)", (session_id,)).fetchone()[0]
        gasoline = db.execute("SELECT gasoline FROM resources WHERE id=(?)", (session_id,)).fetchone()[0]
        ammunition = db.execute("SELECT ammunition FROM resources WHERE id=(?)", (session_id,)).fetchone()[0]

        lst = [money, rations, oil, coal, uranium, bauxite, iron, lead, copper, components, steel, consumer_goods, lumber, aluminium, gasoline, ammunition]
        return lst
    return dict(get_resource_amount=get_resource_amount)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html") # renders index.html when "/" is accesed


@login_required
@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "GET":

        cId = session["user_id"]

        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        name = db.execute("SELECT username FROM users WHERE id=(?)", (cId,)).fetchone()[0]

        connection.close()

        return render_template("account.html", name=name)

@login_required
@app.route("/recruitments", methods=["GET", "POST"])
def recruitments():
    if request.method == "GET":
        return render_template("recruitments.html")

@login_required
@app.route("/businesses", methods=["GET", "POST"])
def businesses():
    if request.method == "GET":
        return render_template("businesses.html")

@login_required
@app.route("/assembly", methods=["GET", "POST"])
def assembly():
    if request.method == "GET":
        return render_template("assembly.html")



"""@app.route("/logout", methods=["GET"])
def logout():
    session.pop('user_id', None)
    return redirect("/login")"""

@app.route("/tutorial", methods=["GET"])
def tutorial():
    return render_template("tutorial.html")

@app.route("/statistics", methods=["GET"])
def statistics():
    return render_template("statistics.html")

@app.route("/my_offers", methods=["GET"])
def myoffers():
    return render_template("my_offers.html")

@app.route("/war", methods=["GET"])
def war():
    return render_template("war.html")

@app.route("/wartarget", methods=["GET"])
def wartarget():
    return render_template("wartarget.html")

@app.route("/warresult", methods=["GET"])
def warresult():
    return render_template("warresult.html")

# available to run if double click the file
if __name__ == "__main__":
    app.run(debug=True) # Runs the app with debug mode on
