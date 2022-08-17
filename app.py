from flask import Flask, request, render_template, session, redirect, send_from_directory
app = Flask(__name__)

from upgrades import upgrades
from intelligence import intelligence
from tasks import tax_income, population_growth, generate_province_revenue, war_reparation_tax
from market import market, buy_market_offer, marketoffer, my_offers
from province import createprovince, province, provinces, province_sell_buy
from military import military, military_sell_buy
from change import request_password_reset
from coalitions import leave_col, join_col, coalitions, coalition, establish_coalition, my_coalition, removing_requests, adding
from countries import country, countries, update_info
from signup import signup
from login import login
from wars import wars, find_targets
from policies import policies
import requests
import logging
from variables import MILDICT, PROVINCE_UNIT_PRICES
from flaskext.markdown import Markdown
from psycopg2.extras import RealDictCursor
from datetime import datetime
import string
import random
import datetime
import os
from helpers import login_required
import psycopg2
from dotenv import load_dotenv
load_dotenv()


# LOGGING
logging_format = '====\n%(levelname)s (%(created)f - %(asctime)s) (LINE %(lineno)d - %(filename)s - %(funcName)s): %(message)s'
logging.basicConfig(level=logging.ERROR,
                    format=logging_format, filename='errors.log',)
logger = logging.getLogger(__name__)


class RequestsHandler(logging.Handler):
    def send_discord_webhook(self, record):
        formatter = logging.Formatter(logging_format)
        message = formatter.format(record)
        url = os.getenv("DISCORD_WEBHOOK_URL")
        data = {
            "content": message,
            "username": "A&O ERROR"
        }
        requests.post(url, json=data)

    def emit(self, record):
        """Send the log records (created by loggers) to
        the appropriate destination.
        """
        self.send_discord_webhook(record)
###


Markdown(app)

try:
    environment = os.getenv("ENVIRONMENT")
except:
    environment = "DEV"

if environment == "PROD":
    app.secret_key = os.getenv("SECRET_KEY")

    handler = RequestsHandler()
    logger.addHandler(handler)

# Import written packages
# Don't put these above app = Flask(__name__), because it will cause a circular import error


def generate_error_code():
    numbers = 20
    code = ''.join(random.choice(string.ascii_lowercase + string.digits)
                   for _ in range(numbers))
    time = int(datetime.now().timestamp())
    full = f"{code}-{time}"
    return full


@app.errorhandler(404)
def page_not_found(error):
    return render_template("error.html", code=404, message="Page not found!")


@app.errorhandler(405)
def method_not_allowed(error):
    method = request.method
    if method == "POST":
        correct_method = "GET"
    elif method == "GET":
        correct_method = "POST"

    message = f"Sorry, this method is not allowed! The correct method is {correct_method}"
    return render_template("error.html", code=405, message=message)


@app.errorhandler(500)
def invalid_server_error(error):
    error_message = "Invalid Server Error. Sorry about that."
    error_code = generate_error_code()
    print(f"[ERROR! ^^^] [{error_code}] [{error}")
    return render_template("error.html", code=500, message=error_message, error_code=error_code)

# Jinja2 filter to add commas to numbers


@app.template_filter()
def commas(value):
    try:
        rounded = round(value)
        returned = "{:,}".format(rounded)
    except:
        returned = value
    return returned

# Jinja2 filter to render province building resource strings


@app.template_filter()
def prores(unit):
    change_price = False
    unit = unit.lower()
    if "," in unit:
        split_unit = unit.split(", ")
        unit = split_unit[0]
        change_price = float(split_unit[1])

    renames = {
        "Fulfillment centers": "malls",
        "Bullet trains": "monorails"
    }

    print(unit)
    unit_name = unit.replace("_", " ").capitalize()
    if unit_name == "Coal burners":
        unit_name = "Coal power plants"
    try:
        unit = renames[unit_name]
    except KeyError:
        ...

    price = PROVINCE_UNIT_PRICES[f'{unit}_price']
    if change_price:
        price = price * change_price
    try:
        resources = ", ".join(
            [f"{i[1]} {i[0]}" for i in PROVINCE_UNIT_PRICES[f"{unit}_resource"].items()])
        full = f"{unit_name} cost { commas(price) }, { resources } each"
    except:
        full = f"{unit_name} cost { commas(price) } each"
    return full

# Jinja2 filter to render military unit resource strings


@app.template_filter()
def milres(unit):
    change_price = False
    if "," in unit:
        split_unit = unit.split(", ")
        unit = split_unit[0]
        change_price = float(split_unit[1])
    price = MILDICT[unit]['price']
    if change_price:
        price = price * change_price
    try:
        resources = ", ".join(
            [f"{i[1]} {i[0]}" for i in MILDICT[unit]["resources"].items()])
        full = f"{unit.capitalize()} cost { commas(price) }, { resources } each"
    except:
        full = f"{unit.capitalize()} cost { commas(price) } each"
    return full


def get_resources():
    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"),
        cursor_factory=RealDictCursor)
    db = conn.cursor()
    cId = session["user_id"]

    try:
        db.execute(
            "SELECT * FROM resources INNER JOIN stats ON resources.id=stats.id WHERE stats.id=%s", (cId,))
        resources = dict(db.fetchone())
        conn.close()
        return resources
    except TypeError:
        return {}


@app.context_processor
def inject_user():
    return dict(get_resources=get_resources)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/robots.txt")
def robots():
    return send_from_directory("static", "robots.txt")


@app.route("/account", methods=["GET"])
@login_required
def account():
    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"),
        cursor_factory=RealDictCursor)
    db = conn.cursor()

    cId = session["user_id"]

    db.execute("SELECT username, email, date FROM users WHERE id=%s", (cId,))
    user = dict(db.fetchone())
    conn.close()

    return render_template("account.html", user=user)


@app.route("/recruitments", methods=["GET"])
@login_required
def recruitments():
    return render_template("recruitments.html")


@app.route("/businesses", methods=["GET"])
@login_required
def businesses():
    return render_template("businesses.html")


"""
@login_required
@app.route("/assembly", methods=["GET"])
def assembly():
    return render_template("assembly.html")
"""


@app.route("/logout")
def logout():
    if session.get('user_id') is not None:
        session.clear()
    else:
        pass
    return redirect("/")


@app.route("/tutorial", methods=["GET"])
def tutorial():
    return render_template("tutorial.html")


@app.route("/forgot_password", methods=["GET"])
def forget_password():
    return render_template("forgot_password.html")


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
    app.run(host='0.0.0.0', use_reloader=False)
