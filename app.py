# ALL MIGRATED (EXCEPT CELERY TASKS)

from flask import Flask, request, render_template, session, redirect
from celery import Celery
from helpers import login_required
import psycopg2
# Game.ping() # temporarily removed this line because it might make celery not work
from dotenv import load_dotenv
load_dotenv()
import os
from celery.schedules import crontab
import datetime

app = Flask(__name__)

try:
    environment = os.getenv("ENVIRONMENT")
except:
    environment = "DEV"

if environment == "PROD":
    app.secret_key = os.getenv("SECRET_KEY")

app.config["SESSION_PERMANENT"] = True
app.permanent_session_lifetime = datetime.timedelta(days=365)

# import written packages DONT U DARE PUT THESE IMPORTS ABOVE `app=Flask(__name__) or it causes a circular import since these files import app themselves!`
from wars import wars, find_targets
from login import login
from signup import signup
from countries import country, countries, update_info
from coalitions import leave_col, join_col, coalitions, coalition, establish_coalition, my_coalition, removing_requests, adding
from military import military, military_sell_buy
from province import createprovince, province, provinces, province_sell_buy
from market import market, buy_market_offer, marketoffer, my_offers
from tasks import tax_income, population_growth, generate_province_revenue, war_reparation_tax
from intelligence import intelligence
# from upgrades import upgrades

app.config["CELERY_BROKER_URL"] = os.getenv("CELERY_BROKER_URL")
app.config["CELERY_RESULT_BACKEND"] = os.getenv("CELERY_RESULT_BACKEND")

celery_beat_schedule = {
    "population_growth": {
        "task": "app.task_population_growth",
        # Run hourly
        "schedule": crontab(minute=0, hour='*/1'),
    },
    "generate_province_revenue": {
        "task": "app.task_generate_province_revenue",
        # Run hourly
        "schedule": crontab(minute=0, hour='*/1'),
    },
    "tax_income": {
        "task": "app.task_tax_income",
        # Run hourly
        "schedule": crontab(minute=0, hour='*/1'),
    },
    "war_reparation_tax": {
        "task": "app.task_war_reparation_tax",
        # Run every day at midnight (UTC)
        "schedule": crontab(minute=0, hour=0)
    },
    "manpower_increase": {
        "task": "app.task_manpower_increase",
        # Run everyday at midnight (UTC)
        "schedule": crontab(minute=0, hour=0)
    }
}

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
def task_population_growth():
    population_growth()

@celery.task()
def task_tax_income():
    tax_income()

@celery.task()
def task_generate_province_revenue():
    generate_province_revenue()

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

# runs one a day
# transfer x% of all resources (could depends on conditions like Raze war_type)to the winner side after a war
@celery.task()
def task_war_reparation_tax():
    war_reparation_tax()

@celery.task()
def task_manpower_increase():
    conn = psycopg2.connect(
    database=os.getenv("PG_DATABASE"),
    user=os.getenv("PG_USER"),
    password=os.getenv("PG_PASSWORD"),
    host=os.getenv("PG_HOST"),
    port=os.getenv("PG_PORT"))
    db = conn.cursor()

    db.execute("SELECT id FROM users")
    user_ids = db.fetchall()
    for id in user_ids:
        db.execute("SELECT SUM(population) FROM provinces WHERE userid=(%s)", (id[0],))
        population = db.fetchone()[0]
        if population:
            capable_population = population*0.2

            # Currently this is a constant
            army_tradition = 0.1
            produced_manpower = int(capable_population*army_tradition)

            db.execute("SELECT manpower FROM military WHERE id=(%s)", (id[0],))
            manpower = db.fetchone()[0]

            if manpower+produced_manpower >= population:
                produced_manpower = 0

            db.execute("UPDATE military SET manpower=manpower+(%s) WHERE id=(%s)",(produced_manpower, id[0]))

    conn.commit()
    conn.close()

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

# handling default error
@app.errorhandler(404)
def page_not_found(error):
    return render_template("error.html", code=404, message="Page not found!")

@app.template_filter()
def commas(value):
    return "{:,}".format(value)

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

            db.execute("""
            SELECT rations, oil, coal, uranium, bauxite, iron, lead, copper, lumber,
            components, steel, consumer_goods, aluminium, gasoline, ammunition FROM resources
            WHERE id=%s
            """, (session_id,))
            resource = db.fetchall()
            resource = list(resource[0])

            resources = {
                "money": money,
                "rations": resource[0],
                "oil": resource[1],
                "coal": resource[2],
                "uranium": resource[3],
                "bauxite": resource[4],
                "iron": resource[5],
                "lead": resource[6],
                "copper": resource[7],
                "lumber": resource[8],
                "components": resource[9],
                "steel": resource[10],
                "consumer_goods": resource[11],
                "aluminium": resource[12],
                "gasoline": resource[13],
                "ammunition": resource[14],
            }

            return resources

        except TypeError:
            resources = {}

    return dict(get_resource_amount=get_resource_amount)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/account", methods=["GET", "POST"])
@login_required
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


@app.route("/recruitments", methods=["GET", "POST"])
@login_required
def recruitments():
    if request.method == "GET":
        return render_template("recruitments.html")


@app.route("/businesses", methods=["GET", "POST"])
@login_required
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

"""
@app.route("/mass_purchase", methods=["GET"])
def mass_purchase():
    return render_template("mass_purchase.html")
"""

if __name__ == "__main__":
    app.run(host='0.0.0.0', use_reloader=True)
