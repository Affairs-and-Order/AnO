# FULLY MIGRATED

from flask import Flask, request, render_template, session, redirect, flash
from tempfile import mkdtemp
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
from app import app
from dotenv import load_dotenv
import os
load_dotenv()

@login_required
@app.route("/provinces", methods=["GET", "POST"])
def provinces():
    if request.method == "GET":
        
        connection = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"))

        db = connection.cursor()

        cId = session["user_id"]

        db.execute("SELECT cityCount FROM provinces WHERE userId=(%s) ORDER BY id ASC", (cId,))
        cityCount = db.fetchall()
        db.execute("SELECT population FROM provinces WHERE userId=(%s) ORDER BY id ASC", (cId,))
        population = db.fetchall()
        db.execute("SELECT provinceName FROM provinces WHERE userId=(%s) ORDER BY id ASC", (cId,))
        name = db.fetchall()
        db.execute("SELECT id FROM provinces WHERE userId=(%s) ORDER BY id ASC", (cId,))
        pId = db.fetchall()
        db.execute("SELECT land FROM provinces WHERE userId=(%s) ORDER BY id ASC", (cId,))
        land = db.fetchall()
        db.execute("SELECT happiness FROM provinces WHERE userId=(%s) ORDER BY id ASC", (cId,))
        happiness = db.fetchall()
        db.execute("SELECT productivity FROM provinces WHERE userId=(%s) ORDER BY id ASC", (cId,))
        productivity = db.fetchall()

        connection.close()

        # zips the above SELECT statements into one list.
        pAll = zip(cityCount, population, name, pId, land, happiness, productivity)

        return render_template("provinces.html", pAll=pAll)


@login_required
@app.route("/province/<pId>", methods=["GET"])
def province(pId):

    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()
    cId = session["user_id"]

    db.execute("SELECT userId FROM provinces WHERE id=(%s)", (pId,))
    province_user = db.fetchone()[0]
    db.execute("SELECT location FROM stats WHERE id=(%s)", (province_user,))
    location = db.fetchone()[0]
    
    if province_user == cId:
        ownProvince = True
    else:
        ownProvince = False

    db.execute("SELECT provinceName FROM provinces WHERE id=(%s)", (pId,))
    name = db.fetchone()[0]
    db.execute("SELECT population FROM provinces WHERE id=(%s)", (pId,))
    population = db.fetchone()[0]
    db.execute("SELECT pollution FROM provinces WHERE id=(%s)", (pId,))
    pollution = db.fetchone()[0]
    db.execute("SELECT happiness FROM provinces WHERE id=(%s)", (pId,))
    happiness = db.fetchone()[0]
    db.execute("SELECT productivity FROM provinces WHERE id=(%s)", (pId,))
    productivity = db.fetchone()[0]
    db.execute("SELECT happiness FROM provinces WHERE id=(%s)", (pId,))
    consumer_spending = db.fetchone()[0]

    db.execute("SELECT cityCount FROM provinces WHERE id=(%s)", (pId,))
    cityCount = db.fetchone()[0]
    db.execute("SELECT land FROM provinces WHERE id=(%s)", (pId,))
    land = db.fetchone()[0]

    db.execute("SELECT coal_burners FROM proInfra WHERE id=(%s)", (pId,))
    coal_burners = db.fetchone()[0]
    db.execute("SELECT oil_burners FROM proInfra WHERE id=(%s)", (pId,))
    oil_burners = db.fetchone()[0]
    db.execute("SELECT hydro_dams FROM proInfra WHERE id=(%s)", (pId,))
    hydro_dams = db.fetchone()[0]
    db.execute("SELECT nuclear_reactors FROM proInfra WHERE id=(%s)", (pId,))
    nuclear_reactors = db.fetchone()[0]
    db.execute("SELECT solar_fields FROM proInfra WHERE id=(%s)", (pId,))
    solar_fields = db.fetchone()[0]

    db.execute("SELECT gas_stations FROM proInfra WHERE id=(%s)", (pId,))
    gas_stations = db.fetchone()[0]
    db.execute("SELECT general_stores FROM proInfra WHERE id=(%s)", (pId,))
    general_stores = db.fetchone()[0]
    db.execute("SELECT farmers_markets FROM proInfra WHERE id=(%s)", (pId,))
    farmers_markets = db.fetchone()[0]
    db.execute("SELECT malls FROM proInfra WHERE id=(%s)", (pId,))
    malls = db.fetchone()[0]
    db.execute("SELECT banks FROM proInfra WHERE id=(%s)", (pId,))
    banks = db.fetchone()[0]

    db.execute("SELECT city_parks FROM proInfra WHERE id=(%s)", (pId,))
    city_parks = db.fetchone()[0]
    db.execute("SELECT hospitals FROM proInfra WHERE id=(%s)", (pId,))
    hospitals = db.fetchone()[0]
    db.execute("SELECT libraries FROM proInfra WHERE id=(%s)", (pId,))
    libraries = db.fetchone()[0]
    db.execute("SELECT universities FROM proInfra WHERE id=(%s)", (pId,))
    universities = db.fetchone()[0]
    db.execute("SELECT monorails FROM proInfra WHERE id=(%s)", (pId,))
    monorails = db.fetchone()[0]

    db.execute("SELECT army_bases FROM proInfra WHERE id=(%s)", (pId,))
    army_bases = db.fetchone()[0]
    db.execute("SELECT harbours FROM proInfra WHERE id=(%s)", (pId,))
    harbours = db.fetchone()[0]
    db.execute("SELECT aerodomes FROM proInfra WHERE id=(%s)", (pId,))
    aerodomes = db.fetchone()[0]
    db.execute("SELECT admin_buildings FROM proInfra WHERE id=(%s)", (pId,))
    admin_buildings = db.fetchone()[0]
    db.execute("SELECT silos FROM proInfra WHERE id=(%s)", (pId,))
    silos = db.fetchone()[0]

    ### Industry ###
    db.execute("SELECT farms FROM proInfra WHERE id=(%s)", (pId,))
    farms = db.fetchone()[0]
    try:
        db.execute("SELECT pumpjacks FROM proInfra WHERE id=(%s)", (pId,))
        pumpjacks = db.fetchone()[0]
    except:
        pumpjacks = None
    try:
        db.execute("SELECT coal_mines FROM proInfra WHERE id=(%s)", (pId,))
        coal_mines = db.fetchone()[0]
    except:
        coal_mines = None
    try:
        db.execute("SELECT bauxite_mines FROM proInfra WHERE id=(%s)", (pId,))
        bauxite_mines = db.fetchone()[0]
    except:
        bauxite_mines = None
    try:
        db.execute("SELECT copper_mines FROM proInfra WHERE id=(%s)", (pId,))
        copper_mines = db.fetchone()[0]
    except:
        copper_mines = None
    try:
        db.execute("SELECT uranium_mines FROM proInfra WHERE id=(%s)", (pId,))
        uranium_mines = db.fetchone()[0]
    except:
        uranium_mines = None
    try:
        db.execute("SELECT lead_mines FROM proInfra WHERE id=(%s)", (pId,))
        lead_mines = db.fetchone()[0]
    except:
        lead_mines = None
    try:
        db.execute("SELECT iron_mines FROM proInfra WHERE id=(%s)", (pId,))
        iron_mines = db.fetchone()[0]
    except:
        iron_mines = None
    try:
        db.execute("SELECT lumber_mills FROM proInfra WHERE id=(%s)", (pId,))
        lumber_mills = db.fetchone()[0]
    except:
        lumber_mills = None
    #############

    ### Processing ###
    
    db.execute("SELECT component_factories FROM proInfra WHERE id=(%s)", (pId,))
    component_factories = db.fetchone()[0]
    db.execute("SELECT steel_mills FROM proInfra WHERE id=(%s)", (pId,))
    steel_mills  = db.fetchone()[0]
    db.execute("SELECT ammunition_factories FROM proInfra WHERE id=(%s)", (pId,))
    ammunition_factories = db.fetchone()[0]
    db.execute("SELECT aluminium_refineries FROM proInfra WHERE id=(%s)", (pId,))
    aluminium_refineries = db.fetchone()[0]
    db.execute("SELECT oil_refineries FROM proInfra WHERE id=(%s)", (pId,))
    oil_refineries = db.fetchone()[0]

    #################

    connection.close()

    return render_template("province.html", pId=pId, population=population, name=name, ownProvince=ownProvince,
                            cityCount=cityCount, land=land, pollution=pollution, consumer_spending=consumer_spending,
                            happiness=happiness, productivity=productivity, location=location,

                            coal_burners=coal_burners, oil_burners=oil_burners, hydro_dams=hydro_dams, nuclear_reactors=nuclear_reactors, solar_fields=solar_fields,
                            gas_stations=gas_stations, general_stores=general_stores, farmers_markets=farmers_markets, malls=malls,
                            banks=banks, city_parks=city_parks, hospitals=hospitals, libraries=libraries, universities=universities,
                            monorails=monorails,
                            
                            army_bases=army_bases, harbours=harbours, aerodomes=aerodomes, admin_buildings=admin_buildings, silos=silos,
                            
                            farms=farms, pumpjacks=pumpjacks, coal_mines=coal_mines, bauxite_mines=bauxite_mines,
                            copper_mines=copper_mines, uranium_mines=uranium_mines, lead_mines=lead_mines, iron_mines=iron_mines,
                            lumber_mills=lumber_mills,

                            component_factories=component_factories, steel_mills=steel_mills, ammunition_factories=ammunition_factories,
                            aluminium_refineries=aluminium_refineries, oil_refineries=oil_refineries
                            )


@login_required
@app.route("/createprovince", methods=["GET", "POST"])
def createprovince():

    cId = session["user_id"]
    
    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    if request.method == "POST":

        pName = request.form.get("name")

        db.execute("SELECT gold FROM stats WHERE id=(%s)", (cId,))
        current_user_money = int(db.fetchone()[0])
        province_price = 50000

        if province_price > current_user_money:
            return error(400, "You don't have enough money")

        db.execute("INSERT INTO provinces (userId, provinceName) VALUES (%s, %s)", (cId, pName))

        db.execute("SELECT id FROM provinces WHERE userId=(%s) AND provinceName=(%s)", (cId, pName))
        province_id = db.fetchone()[0]

        db.execute("INSERT INTO proInfra (id) VALUES (%s)", (province_id,))
        
         # Provinces cost 50k
        new_user_money = current_user_money - province_price
        db.execute("UPDATE stats SET gold=(%s) WHERE id=(%s)", (new_user_money, cId))

        connection.commit()
        connection.close()

        return redirect("/provinces")
    else:

        db.execute("SELECT COUNT(id) FROM provinces WHERE userId=(%s)", (cId,))
        current_province_amount = db.fetchone()[0]

        multiplier = 1 + (0.25 * current_province_amount)
        price = int(50000 * multiplier)
        return render_template("createprovince.html", price=price)

def get_used_slots(pId): # pId = province id

    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    total_slots = 0

    allUnits = [
        "coal_burners", "oil_burners", "hydro_dams", "nuclear_reactors", "solar_fields",
        "gas_stations", "general_stores", "farmers_markets", "malls", "banks",
        "city_parks", "hospitals", "libraries", "universities", "monorails",

        "army_bases", "harbours", "aerodomes", "admin_buildings", "silos",

        "farms", "pumpjacks", "coal_mines", "bauxite_mines", 
        "copper_mines", "uranium_mines", "lead_mines", "iron_mines",
        "lumber_mills",

        "component_factories", "steel_mills", "ammunition_factories",
        "aluminium_refineries", "oil_refineries"
    ]
    
    for unit in allUnits:
        try:
            select_statement = f"SELECT {unit} FROM proInfra " + "WHERE id=%s"
            db.execute(select_statement, (pId))

            amount = int(db.fetchone()[0])
            total_slots += amount

        except:
            total_slots += 0

    return total_slots

@login_required
@app.route("/<way>/<units>/<province_id>", methods=["POST"])
def province_sell_buy(way, units, province_id):

    if request.method == "POST":

        cId = session["user_id"]

        connection = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"))

        db = connection.cursor()

        try:
            db.execute("SELECT id FROM provinces WHERE id=%s AND userId=%s", (province_id, cId,))
            ownProvince = db.fetchone()[0]
            ownProvince = True
        except TypeError:
            ownProvince = False

        if ownProvince == False:
            return error(400, "You don't own this province")

        allUnits = [
            "land", "cityCount",
            
            "coal_burners", "oil_burners", "hydro_dams", "nuclear_reactors", "solar_fields",
            "gas_stations", "general_stores", "farmers_markets", "malls", "banks",
            "city_parks", "hospitals", "libraries", "universities", "monorails",

            "army_bases", "harbours", "aerodomes", "admin_buildings", "silos",

            "farms", "pumpjacks", "coal_mines", "bauxite_mines", 
            "copper_mines", "uranium_mines", "lead_mines", "iron_mines",
            "lumber_mills",

            "component_factories", "steel_mills", "ammunition_factories",
            "aluminium_refineries", "oil_refineries"
        ]

        max_4 = [
            "gas_stations", "general_stores", "farmers_markets", "malls",
            "banks", "city_parks", "hospitals"
        ]    

        db.execute("SELECT gold FROM stats WHERE id=(%s)", (cId,))
        gold = int(db.fetchone()[0])

        wantedUnits = int(request.form.get(units))

        if units == "cityCount":

            db.execute("SELECT cityCount FROM provinces WHERE id=(%s)", (province_id,))
            current_cityCount = db.fetchone()[0]

            multiplier = 1 + ((0.10 * wantedUnits) * current_cityCount) # 10% Increase in cost for each city.
            cityCount_price = int(1000 * multiplier) # Each city costs 1000 without the multiplier
        else:
            cityCount_price = 0

        unit_prices = {
            "land": 100,
            "cityCount": cityCount_price,

            "coal_burners": 500,
            "oil_burners": 500,
            "hydro_dams": 500,
            "nuclear_reactors": 500,
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
            "silos": 500,

            "farms": 500,
            "pumpjacks": 500,
            "coal_mines": 500,
            "bauxite_mines": 500,
            "copper_mines": 500,
            "uranium_mines": 500,
            "lead_mines": 500,
            "iron_mines": 500,
            "lumber_mills": 500,

            "component_factories": 500,
            "steel_mills": 500, 
            "ammunition_factories": 500,
            "aluminium_refineries": 500,
            "oil_refineries": 500
        }

        if units not in allUnits:
            return error("No such unit exists.", 400)

        if units == "land" or units == "cityCount":
            table = "provinces"
        else:
            table = "proInfra"

        price = unit_prices[f"{units}"]
        totalPrice = int(wantedUnits * price)

        curUnStat = f"SELECT {units} FROM {table} " +  "WHERE id=%s"
        db.execute(curUnStat, (province_id,))
        currentUnits = int(db.fetchone()[0])

        db.execute("SELECT cityCount FROM provinces WHERE id=(%s)", (province_id,))
        total_infra_slots = int(db.fetchone()[0])

        used_slots = int(get_used_slots(province_id))
        free_infra_slots = total_infra_slots - used_slots

        if way == "sell":

            if wantedUnits > currentUnits:  # checks if unit is legit
                return error("You don't have enough units", 400)

            unitUpd = f"UPDATE {table} SET {units}" + "=%s WHERE id=%s"
            db.execute(unitUpd, ((currentUnits - wantedUnits), province_id))

            db.execute("UPDATE stats SET gold=(%s) WHERE id=(%s)", ((gold + wantedUnits * price), cId))

        elif way == "buy":

            if int(totalPrice) > int(gold):  # checks if user wants to buy more units than he has gold
                return error("You don't have enough gold", 400)

            if units in max_4 and currentUnits + wantedUnits >= 4:
                return error(400, "You can't have more than 4 of this unit")

            if free_infra_slots < wantedUnits:
                return error(400, f"You don't have enough city slots to buy {wantedUnits} units. Buy more cities to fix this problem")

            db.execute("UPDATE stats SET gold=(%s) WHERE id=(%s)", (int(gold)-int(totalPrice), cId,))

            updStat = f"UPDATE {table} SET {units}" + "=%s WHERE id=%s"
            db.execute(updStat, ((currentUnits + wantedUnits), province_id))

        else:
            error(404, "Page not found")

        connection.commit()
        connection.close()

        return redirect(f"/province/{province_id}")

