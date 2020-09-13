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
from app import app


@login_required
@app.route("/provinces", methods=["GET", "POST"])
def provinces():
    if request.method == "GET":

        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        cId = session["user_id"]

        cityCount = db.execute(
            "SELECT cityCount FROM provinces WHERE userId=(?) ORDER BY id ASC", (cId,)).fetchall()
        population = db.execute(
            "SELECT population FROM provinces WHERE userId=(?) ORDER BY id ASC", (cId,)).fetchall()
        name = db.execute(
            "SELECT provinceName FROM provinces WHERE userId=(?) ORDER BY id ASC", (cId,)).fetchall()
        pId = db.execute(
            "SELECT id FROM provinces WHERE userId=(?) ORDER BY id ASC", (cId,)).fetchall()
        land = db.execute(
            "SELECT land FROM provinces WHERE userId=(?) ORDER BY id ASC", (cId,)).fetchall()

        connection.close()

        # zips the above SELECT statements into one list.
        pAll = zip(cityCount, population, name, pId, land)

        return render_template("provinces.html", pAll=pAll)


@login_required
@app.route("/province/<pId>", methods=["GET", "POST"])
def province(pId):
    if request.method == "GET":
        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        name = db.execute("SELECT provinceName FROM provinces WHERE id=(?)", (pId,)).fetchone()[0]
        population = db.execute(
            "SELECT population FROM provinces WHERE id=(?)", (pId,)).fetchone()[0]
        pollution = db.execute(
            "SELECT pollution FROM provinces WHERE id=(?)", (pId,)).fetchone()[0]

        cityCount = db.execute(
            "SELECT cityCount FROM provinces WHERE id=(?)", (pId,)).fetchone()[0]
        land = db.execute(
            "SELECT land FROM provinces WHERE id=(?)", (pId,)).fetchone()[0]

        oil_burners = db.execute(
            "SELECT oil_burners FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]
        hydro_dams = db.execute(
            "SELECT hydro_dams FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]
        nuclear_reactors = db.execute(
            "SELECT nuclear_reactors FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]
        solar_fields = db.execute(
            "SELECT solar_fields FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]

        gas_stations = db.execute(
            "SELECT gas_stations FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]
        general_stores = db.execute(
            "SELECT general_stores FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]
        farmers_markets = db.execute(
            "SELECT farmers_markets FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]
        malls = db.execute(
            "SELECT malls FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]
        banks = db.execute(
            "SELECT banks FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]

        city_parks = db.execute(
            "SELECT city_parks FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]
        hospitals = db.execute(
            "SELECT hospitals FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]
        libraries = db.execute(
            "SELECT libraries FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]
        universities = db.execute(
            "SELECT universities FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]
        monorails = db.execute(
            "SELECT monorails FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]

        connection.close()

        return render_template("province.html", pId=pId, population=population, name=name,
                               cityCount=cityCount, land=land, pollution=pollution,
                               oil_burners=oil_burners, hydro_dams=hydro_dams, nuclear_reactors=nuclear_reactors, solar_fields=solar_fields,
                               gas_stations=gas_stations, general_stores=general_stores, farmers_markets=farmers_markets, malls=malls,
                               banks=banks, city_parks=city_parks, hospitals=hospitals, libraries=libraries, universities=universities,
                               monorails=monorails)


@login_required
@app.route("/createprovince", methods=["GET", "POST"])
def createprovince():

    cId = session["user_id"]
    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()

    if request.method == "POST":

        pName = request.form.get("name")

        db.execute("INSERT INTO provinces (userId, provinceName) VALUES (?, ?)", (cId, pName))
        province_id = db.execute("SELECT id FROM provinces WHERE userId=(?) AND provinceName=(?)", (cId, pName)).fetchone()[0]
        db.execute("INSERT INTO proInfra (id) VALUES (?)", (province_id,))
        current_user_gold = db.execute("SELECT gold FROM stats WHERE id=(?)", (cId,)).fetchone()[0]
        province_price = 50000 # Provinces cost 50k
        new_user_gold = current_user_gold - province_price
        db.execute("UPDATE stats SET gold=(?) WHERE id=(?)", (new_user_gold, cId))

        connection.commit()
        connection.close()

        return redirect("/provinces")
    else:

        current_province_amount = db.execute("SELECT COUNT(id) FROM provinces WHERE userId=(?)", (cId,)).fetchone()[0]
        multiplier = 1 + (0.25 * current_province_amount)
        price = int(50000 * multiplier)
        return render_template("createprovince.html", price=price)

def get_used_slots(pId): # pId = province id

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()

    oil_burners = db.execute("SELECT oil_burners FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]
    hydro_dams = db.execute("SELECT hydro_dams FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]
    nuclear_reactors = db.execute("SELECT nuclear_reactors FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]
    solar_fields = db.execute("SELECT solar_fields FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]

    gas_stations = db.execute("SELECT gas_stations FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]
    general_stores = db.execute("SELECT general_stores FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]
    farmers_markets = db.execute("SELECT farmers_markets FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]
    malls = db.execute("SELECT malls FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]
    banks = db.execute("SELECT banks FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]

    city_parks = db.execute("SELECT city_parks FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]
    hospitals = db.execute("SELECT hospitals FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]
    libraries = db.execute("SELECT libraries FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]
    universities = db.execute("SELECT universities FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]
    monorails = db.execute("SELECT monorails FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]

    infra_list = [oil_burners, hydro_dams, nuclear_reactors, solar_fields,
    gas_stations, general_stores, farmers_markets, malls, banks,
    city_parks, hospitals, libraries, universities, monorails]

    total_slots = sum(infra_list)

    return total_slots

@login_required
@app.route("/<way>/<units>/<province_id>", methods=["POST"])
def province_sell_buy(way, units, province_id):

    if request.method == "POST":

        cId = session["user_id"]

        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        try:
            ownProvince = db.execute(
                "SELECT id FROM provinces WHERE id=(?) AND userId=(?)", (province_id, cId,)).fetchone()[0]
            ownProvince = True
        except TypeError:
            ownProvince = False

        if ownProvince == False:
            return error(400, "You don't own this province")

        allUnits = [
            "land", "cityCount",
            "oil_burners", "hydro_dams", "nuclear_reactors", "solar_fields",
            "gas_stations", "general_stores", "farmers_markets", "malls", "banks",
            "city_parks", "hospitals", "libraries", "universities", "monorails",

            "army_bases", "harbours", "aerodomes", "admin_buildings", "silos"
        ]

        max_4 = [
            "gas_stations", "general_stores", "farmers_markets", "malls",
            "banks", "city_parks", "hospitals"
        ]    

        gold = int(db.execute("SELECT gold FROM stats WHERE id=(?)", (cId,)).fetchone()[0])
        wantedUnits = int(request.form.get(units))

        if units == "cityCount":
            current_cityCount = db.execute("SELECT cityCount FROM provinces WHERE id=(?)", (province_id,)).fetchone()[0]
            multiplier = 1 + ((0.10 * wantedUnits) * current_cityCount) # 10% Increase in cost for each city.
            cityCount_price = int(1000 * multiplier) # Each city costs 1000 without the multiplier
        else:
            cityCount_price = 0

        unit_prices = {
            "land": 100,
            "cityCount": cityCount_price,

            "oil_burners": 350,
            "hydro_dams": 450,
            "nuclear_reactors": 700,
            "solar_fields": 550,

            "gas_stations": 500,
            "general_stores": 500,
            "farmers_markets": 500,
            "malls": 500,
            "banks": 500,

            "city_parks": 500,
            "hospitals": 500,
            "libraries": 500,
            "universities": 500,
            "monorails": 500,

            "army_bases": 500,
            "harbours": 500,
            "aerodomes": 500,
            "admin_buildings": 500,
            "silos": 500
        }

        if units not in allUnits:
            return error("No such unit exists.", 400)

        if units == "land" or units == "cityCount":
            table = "provinces"
        else:
            table = "proInfra"

        price = unit_prices[f"{units}"]
        curUnStat = f'SELECT {units} FROM {table} WHERE id=?'
        totalPrice = int(wantedUnits * price)
        currentUnits = int(db.execute(curUnStat, (province_id,)).fetchone()[0])

        total_infra_slots = int(db.execute("SELECT cityCount FROM provinces WHERE id=(?)", (province_id,)).fetchone()[0])
        used_slots = int(get_used_slots(province_id))
        free_infra_slots = total_infra_slots - used_slots

        if way == "sell":

            if wantedUnits > currentUnits:  # checks if unit is legit
                return error("You don't have enough units", 400)

            unitUpd = f"UPDATE {table} SET {units}=(?) WHERE id=(?)"
            db.execute(unitUpd, ((currentUnits - wantedUnits), province_id))
            db.execute("UPDATE stats SET gold=(?) WHERE id=(?)", ((gold + wantedUnits * price), cId))

        elif way == "buy":

            if int(totalPrice) > int(gold):  # checks if user wants to buy more units than he has gold
                return error("You don't have enough gold", 400)

            if units in max_4 and currentUnits + wantedUnits >= 4:
                return error(400, "You can't have more than 4 of this unit")


            if free_infra_slots < wantedUnits:
                return error(400, f"You don't have enough city slots to buy {wantedUnits} units. Buy more cities to fix this problem")

            db.execute("UPDATE stats SET gold=(?) WHERE id=(?)",
                       (int(gold)-int(totalPrice), cId,))

            updStat = f"UPDATE {table} SET {units}=(?) WHERE id=(?)"
            db.execute(updStat, ((currentUnits + wantedUnits), province_id))

        else:
            error(404, "Page not found")

        connection.commit()
        connection.close()

        return redirect(f"/province/{province_id}")

