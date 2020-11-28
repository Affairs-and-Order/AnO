# ALL MIGRATED (EXCEPT CELERY TASKS)

from flask import Flask, request, render_template, session, redirect, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
import datetime
import _pickle as pickle
import random
from celery import Celery
from helpers import login_required, error
import psycopg2
# from celery.schedules import crontab # arent currently using but will be later on
from helpers import get_influence, get_coalition_influence
# Game.ping() # temporarily removed this line because it might make celery not work
from dotenv import load_dotenv
load_dotenv()
import os

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
from intelligence import intelligence
from tasks import generate_province_revenue
# from upgrades import upgrades

app.config["CELERY_BROKER_URL"] = os.getenv("CELERY_BROKER_URL")
app.config["CELERY_RESULT_BACKEND"] = os.getenv("CELERY_RESULT_BACKEND")

celery_beat_schedule = {
    "population_growth": {
        "task": "app.populationGrowth",
        # Run every 15 seconds
        "schedule": 15.0,
    },
    "province_infrastructure": {
        "task": "app.generate_province_revenue",
        # Run every 10 seconds
        "schedule": 10.0,
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

# runs once a day
"""
@celery.task()
def warPing():
    connection = sqlite3.connect("affo/aoo.db")
    cursor = connection.cursor()
    for user in cursor.execute(f"SELECT id FROM war", ()).fetchall():
        # war has lasted more than 3 days, end the war
        if cursor.execute(f"SELECT duration FROM war WHERE id={user}").fetchone()[0] > 3:
            nationObject = pickle.load(cursor.execute(
                f"SELECT nation FROM users WHERE id={user}").fetchone()[0])
            enemyID = cursor.execute(
                f"SELECT enemy FROM war WHERE id={user}").fetchone()[0]

            enemyObject = pickle.load(cursor.execute(
                f"SELECT nation FROM users WHERE id={enemyID}").fetchone()[0])

        # otherwise, update the duration of the war
        elif cursor.execute(f"SELECT duration FROM war WHERE id={user}").fetchone()[0] < 3:
            currentDuration = cursor.execute(
                f"SELECT duration FROM war WHERE id={user}").fetchone()[0]
            cursor.execute(
                f"INSERT INTO war (duration)  VALUES ({currentDuration + 1},)", ())
            connection.commit()
"""

"""
# runs once every hour
@celery.task()
def increaseSupplies():
    connection = sqlite3.connect("affo/aoo.db")
    cursor = connection.cursor()
    for user in cursor.execute(f"SELECT id FROM users").fetchall():
        for supplies in cursor.execute(f"SELECT supplies FROM war WHERE id={user[0]}").fetchall():
            increasedSupplies = supplies[0] + 100
            cursor.execute(
                f"INSERT INTO war (supplies) VALUES ({increasedSupplies} WHERE id={user[0]})")
            connection.commit()
"""

# runs once a day
"""
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
        
        conn = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"))

        db = conn.cursor()
        session_id = session["user_id"]

        try:

            db.execute("SELECT gold FROM stats WHERE id=(%s)", (session_id,))  # DONE
            money = db.fetchone()[0]

            db.execute("SELECT rations FROM resources WHERE id=(%s)", (session_id,))
            rations = db.fetchone()[0]

            db.execute("SELECT oil FROM resources WHERE id=(%s)", (session_id,))
            oil = db.fetchone()[0]  # DONE

            db.execute("SELECT coal FROM resources WHERE id=(%s)", (session_id,))
            coal = db.fetchone()[0]  # DONE

            db.execute("SELECT uranium FROM resources WHERE id=(%s)", (session_id,))
            uranium = db.fetchone()[0]  # DONE

            db.execute("SELECT bauxite FROM resources WHERE id=(%s)", (session_id,))
            bauxite = db.fetchone()[0]  # DONE

            db.execute("SELECT iron FROM resources WHERE id=(%s)", (session_id,))
            iron = db.fetchone()[0]  # DONE

            db.execute("SELECT lead FROM resources WHERE id=(%s)", (session_id,))
            lead = db.fetchone()[0]  # DONE

            db.execute("SELECT copper FROM resources WHERE id=(%s)", (session_id,))
            copper = db.fetchone()[0]  # DONE

            db.execute("SELECT lumber FROM resources WHERE id=(%s)", (session_id,))
            lumber = db.fetchone()[0]  # DONE

            db.execute("SELECT components FROM resources WHERE id=(%s)", (session_id,))
            components = db.fetchone()[0]

            db.execute("SELECT steel FROM resources WHERE id=(%s)", (session_id,))
            steel = db.fetchone()[0]

            db.execute("SELECT consumer_goods FROM resources WHERE id=(%s)", (session_id,))
            consumer_goods = db.fetchone()[0]  # DONE

            db.execute("SELECT aluminium FROM resources WHERE id=(%s)", (session_id,))
            aluminium = db.fetchone()[0]

            db.execute("SELECT gasoline FROM resources WHERE id=(%s)", (session_id,))
            gasoline = db.fetchone()[0]

            db.execute("SELECT ammunition FROM resources WHERE id=(%s)", (session_id,))
            ammunition = db.fetchone()[0]
          
            lst = [money, rations, oil, coal, uranium, bauxite, iron, lead, copper,
                components, steel, consumer_goods, lumber, aluminium, gasoline, ammunition]

        except TypeError:
            lst = []

        return lst
    return dict(get_resource_amount=get_resource_amount)

@app.route("/", methods=["GET"])
def index():
    # renders index.html when "/" is accesed
    return render_template("index.html")

@login_required
@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "GET":

        cId = session["user_id"]

        connection = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"))

        db = connection.cursor()

        db.execute("SELECT username FROM users WHERE id=%s", (cId,))
        name = db.fetchone()[0]

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

"""
@login_required
@app.route("/assembly", methods=["GET", "POST"])
def assembly():
    if request.method == "GET":
        return render_template("assembly.html")
"""


@app.route("/logout/")
def logout():
    if session.get('user_id') is not None:
        session.clear()
    else:
        pass
    return redirect("/")


@app.route("/tutorial", methods=["GET"])
def tutorial():
    return render_template("tutorial.html")

"""
@app.route("/statistics", methods=["GET"])
def statistics():
    return render_template("statistics.html")
"""

@app.route("/my_offers", methods=["GET"])
def myoffers():
    return render_template("my_offers.html")


@app.route("/war", methods=["GET"])
def war():
    return render_template("war.html")


@app.route("/warresult", methods=["GET"])
def warresult():
    return render_template("warresult.html")


@app.route("/mass_purchase", methods=["GET"])
def mass_purchase():
    return render_template("mass_purchase.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0')
