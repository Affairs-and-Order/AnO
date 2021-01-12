# FULLY MIGRATED

from flask import request, render_template, session, redirect
from helpers import login_required, error
import psycopg2
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

        db.execute("""SELECT cityCount, population, provinceName, id, land, happiness, productivity
        FROM provinces WHERE userId=(%s) ORDER BY id ASC""", (cId,))
        provinces = db.fetchall()

        connection.close()

        return render_template("provinces.html", provinces=provinces)


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

    try:
        db.execute("""SELECT userId, provinceName, population, pollution, happiness, productivity,
        consumer_spending, cityCount, land, energy FROM provinces WHERE id=(%s)""", (pId,))
        province_data = db.fetchall()[0]
    except:
        return error(404, "Province doesn't exist")

    province = {}

    province["id"] = pId
    province["user"] = province_data[0]
    province["name"] = province_data[1]
    province["population"] = province_data[2]
    province["pollution"] = province_data[3]
    province["happiness"] = province_data[4]
    province["productivity"] = province_data[5]
    province["consumer_spending"] = province_data[6]
    province["cityCount"] = province_data[7]
    province["land"] = province_data[8]
    province["electricity"] = province_data[9]

    db.execute("SELECT location FROM stats WHERE id=(%s)", (province["user"],))
    province["location"] = db.fetchone()[0]

    ownProvince = province["user"] == cId

    db.execute(
    """
    SELECT
    coal_burners, oil_burners, hydro_dams, nuclear_reactors, solar_fields,
    gas_stations, general_stores, farmers_markets, malls, banks,
    city_parks, hospitals, libraries, universities, monorails,
    army_bases, harbours, aerodomes, admin_buildings, silos,
    farms, pumpjacks, coal_mines, bauxite_mines,
    copper_mines, uranium_mines, lead_mines, iron_mines,
    lumber_mills, component_factories, steel_mills, ammunition_factories,
    aluminium_refineries, oil_refineries FROM proInfra WHERE id=%s
    """, (pId,))
    province_units = db.fetchall()[0]

    coal_burners = province_units[0]
    oil_burners = province_units[1]
    hydro_dams = province_units[2]
    nuclear_reactors = province_units[3]
    solar_fields = province_units[4]

    gas_stations = province_units[5]
    general_stores = province_units[6]
    farmers_markets = province_units[7]
    malls = province_units[8]
    banks = province_units[9]

    city_parks = province_units[10]
    hospitals = province_units[11]
    libraries = province_units[12]
    universities = province_units[13]
    monorails = province_units[14]

    army_bases = province_units[15]
    harbours = province_units[16]
    aerodomes = province_units[17]
    admin_buildings = province_units[18]
    silos = province_units[19]

    farms = province_units[20]
    pumpjacks = province_units[21]
    coal_mines = province_units[22]
    bauxite_mines = province_units[23]
    copper_mines = province_units[24]
    uranium_mines = province_units[25]
    lead_mines = province_units[26]
    iron_mines = province_units[27]
    lumber_mills = province_units[28]

    component_factories = province_units[29]
    steel_mills = province_units[30]
    ammunition_factories = province_units[31]
    aluminium_refineries = province_units[32]
    oil_refineries = province_units[33]

    def enough_consumer_goods(user_id):

        try:
            db.execute("SELECT SUM(population) FROM provinces WHERE userId=%s", (user_id,))
            population = int(db.fetchone()[0])
        except:
            population = 0

        db.execute("SELECT consumer_goods FROM resources WHERE id=%s", (user_id,))
        consumer_goods = int(db.fetchone()[0])
        consumer_goods_needed = round(population * 0.00005)
        new_consumer_goods = consumer_goods - consumer_goods_needed

        if new_consumer_goods > 0:
            return True
        else:
            return False

    enough_consumer_goods = enough_consumer_goods(province["user"])

    def enough_rations(user_id):

        db.execute("SELECT rations FROM resources WHERE id=%s", (user_id,))
        rations = int(db.fetchone()[0])

        rations_per_100k = 4

        hundred_k = province["population"] // 100000
        new_rations = rations - (hundred_k * rations_per_100k)

        if new_rations < 1:
            return False
        else:
            return True

    enough_rations = enough_rations(province["user"])

    def has_power(province_id):

        db.execute("SELECT energy FROM provinces WHERE id=%s", (province_id,))
        energy = int(db.fetchone()[0])

        return energy > 0

    has_power = has_power(pId)

    connection.close()

    return render_template("province.html", province=province, ownProvince=ownProvince,

                            coal_burners=coal_burners, oil_burners=oil_burners, hydro_dams=hydro_dams, nuclear_reactors=nuclear_reactors, solar_fields=solar_fields,
                            gas_stations=gas_stations, general_stores=general_stores, farmers_markets=farmers_markets, malls=malls,
                            banks=banks, city_parks=city_parks, hospitals=hospitals, libraries=libraries, universities=universities,
                            monorails=monorails,

                            army_bases=army_bases, harbours=harbours, aerodomes=aerodomes, admin_buildings=admin_buildings, silos=silos,

                            farms=farms, pumpjacks=pumpjacks, coal_mines=coal_mines, bauxite_mines=bauxite_mines,
                            copper_mines=copper_mines, uranium_mines=uranium_mines, lead_mines=lead_mines, iron_mines=iron_mines,
                            lumber_mills=lumber_mills,

                            component_factories=component_factories, steel_mills=steel_mills, ammunition_factories=ammunition_factories,
                            aluminium_refineries=aluminium_refineries, oil_refineries=oil_refineries,

                            enough_consumer_goods=enough_consumer_goods, enough_rations=enough_rations, has_power=has_power
                            )

def get_province_price(user_id):

    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    db.execute("SELECT COUNT(id) FROM provinces WHERE userId=(%s)", (user_id,))
    current_province_amount = db.fetchone()[0]

    multiplier = 1 + (0.25 * current_province_amount)
    price = int(50000 * multiplier)

    return price

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

        province_price = get_province_price(cId)

        if province_price > current_user_money:
            return error(400, "You don't have enough money")

        db.execute("INSERT INTO provinces (userId, provinceName) VALUES (%s, %s) RETURNING id", (cId, pName))
        province_id = db.fetchone()[0]

        db.execute("INSERT INTO proInfra (id) VALUES (%s)", (province_id,))

        new_user_money = current_user_money - province_price
        db.execute("UPDATE stats SET gold=(%s) WHERE id=(%s)", (new_user_money, cId))

        connection.commit()
        connection.close()

        return redirect("/provinces")
    else:
        price = get_province_price(cId)
        return render_template("createprovince.html", price=price)

def get_free_slots(pId, slot_type): # pId = province id

    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    if slot_type == "city":

        db.execute(
        """
        SELECT
        coal_burners + oil_burners + hydro_dams + nuclear_reactors + solar_fields +
        gas_stations + general_stores + farmers_markets + malls + banks +
        city_parks + hospitals + libraries + universities + monorails
        FROM proInfra WHERE id=%s
        """, (pId,))
        used_slots = int(db.fetchone()[0])

        db.execute("SELECT cityCount FROM provinces WHERE id=%s", (pId,))
        all_slots = int(db.fetchone()[0])

        free_slots = all_slots - used_slots

    elif slot_type == "land":

        db.execute(
        """
        SELECT
        army_bases + harbours + aerodomes + admin_buildings + silos +
        farms + pumpjacks + coal_mines + bauxite_mines +
        copper_mines + uranium_mines + lead_mines + iron_mines +
        lumber_mills + component_factories + steel_mills + ammunition_factories +
        aluminium_refineries + oil_refineries FROM proInfra WHERE id=%s
        """, (pId,))
        used_slots = int(db.fetchone()[0])

        db.execute("SELECT land FROM provinces WHERE id=%s", (pId,))
        all_slots = int(db.fetchone()[0])

        free_slots = all_slots - used_slots

    return free_slots

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

        if not ownProvince:
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

        city_units = [
            "coal_burners", "oil_burners", "hydro_dams", "nuclear_reactors", "solar_fields",
            "gas_stations", "general_stores", "farmers_markets", "malls", "banks",
            "city_parks", "hospitals", "libraries", "universities", "monorails",
        ]

        land_units = [
            "army_bases", "harbours", "aerodomes", "admin_buildings", "silos",
            "farms", "pumpjacks", "coal_mines", "bauxite_mines",
            "copper_mines", "uranium_mines", "lead_mines", "iron_mines",
            "lumber_mills", "component_factories", "steel_mills",
            "ammunition_factories", "aluminium_refineries", "oil_refineries"
        ]

        db.execute("SELECT gold FROM stats WHERE id=(%s)", (cId,))
        gold = int(db.fetchone()[0])

        wantedUnits = int(request.form.get(units))

        if wantedUnits < 1:
            return error(400, "Units cannot be less than 1")

        if units == "cityCount":

            db.execute("SELECT cityCount FROM provinces WHERE id=(%s)", (province_id,))
            current_cityCount = db.fetchone()[0]

            multiplier = 1 + ((0.08 * wantedUnits) * current_cityCount) # 10% Increase in cost for each city.
            cityCount_price = int((250000 * multiplier) * wantedUnits) # Each city costs 250,000 without the multiplier

            print(f"total_price: {cityCount_price}")

        else:
            cityCount_price = 0

        if units == "land":

            db.execute("SELECT land FROM provinces WHERE id=(%s)", (province_id,))
            current_land = db.fetchone()[0]

            multiplier = 1 + ((0.06 * wantedUnits) * current_land) # 10% Increase in cost for each city.
            land_price = int((120000 * multiplier) * wantedUnits) # Each city costs 120,000 without the multiplier

        else:
            land_price = 0


        # All the unit prices in this format:
        """
        unit_price: <the of the unit>,
        unit_resource (optional): {resource_name: amount} (how many of what resources it takes to build)
        unit_resource2 (optional): same as one, just for second resource
        """
        # TODO: change the unit_resource and unit_resource2 into list based system
        unit_prices = {

            "land_price": land_price,
            "cityCount_price": cityCount_price,

            "coal_burners_price": 1300000,
            "coal_burners_resource": {"aluminium": 45},

            "oil_burners_price": 1600000,
            "oil_burners_resource": {"aluminium": 50},

            "hydro_dams_price": 5800000,
            "hydro_dams_resource": {"steel": 120},
            "hydro_dams_resource2": {"aluminium": 60},

            "nuclear_reactors_price": 9500000,
            "nuclear_reactors_resource": {"steel": 250},

            "solar_fields_price": 2300000,
            "solar_fields_resource": {"steel": 55},

            "gas_stations_price": 2900000,
            "gas_stations_resource": {"steel": 50},
            "gas_stations_resource2": {"aluminium": 35},

            "general_stores_price": 3500000,
            "general_stores_resource": {"steel": 60},
            "general_stores_resource2": {"aluminium": 70},

            "farmers_markets_price": 4200000,
            "farmers_markets_resource": {"steel": 75},
            "farmers_markets_resource2": {"aluminium": 80},

            "malls_price": 12500000, # Costs 12.5m
            "malls_resource": {"steel": 360},
            "malls_resource2": {"aluminium": 240},

            "banks_price": 7700000,
            "banks_resource": {"steel": 225},
            "banks_resource2": {"aluminium": 110},

            "city_parks_price": 4000000,
            "city_parks_resource": {"steel": 75},
            "city_parks_resource2": {"aluminium": 60},

            "hospitals_price": 8000000,
            "hospitals_resource": {"steel": 140},
            "hospitals_resource2": {"aluminium": 85},

            "libraries_price": 5200000,
            "libraries_resource": {"steel": 55},
            "libraries_resource2": {"aluminium": 40},

            "universities_price": 12500000, # Costs 12.5m
            "universities_resource": {"steel": 210},
            "universities_resource2": {"aluminium": 105},

            "monorails_price": 19800000,
            "monorails_resource": {"steel": 390},
            "monorails_resource2": {"aluminium": 195},

            "army_bases_price": 1800000,
            "army_bases_resource": {"lumber": 80},

            "harbours_price": 2100000,
            "harbours_resource": {"steel": 210},

            "aerodomes_price": 2600000,
            "aerodomes_resource": {"aluminium": 40},
            "aerodomes_resource2": {"steel": 165},

            "admin_buildings_price": 3200000,
            "admin_buildings_resource": {"steel": 90},
            "admin_buildings_resource2": {"aluminium": 75},

            "silos_price": 12800000,
            "silos_resource": {"steel": 540},
            "silos_resource2": {"aluminium": 240},

            "farms_price": 220000,
            "farms_resource": {"lumber": 10},

            "pumpjacks_price": 450000,
            "pumpjacks_resource": {"steel": 15},

            "coal_mines_price": 590000,
            "coal_mines_resource": {"lumber": 30},

            "bauxite_mines_price": 460000,
            "bauxite_mines_resource": {"lumber": 20},

            "copper_mines_price": 435000,
            "copper_mines_resource": {"lumber": 25},

            "uranium_mines_price": 690000,
            "uranium_mines_resource": {"steel": 35},

            "lead_mines_price": 420000,
            "lead_mines_resource": {"lumber": 25},

            "iron_mines_price": 640000,
            "iron_mines_resource": {"lumber": 20},

            "lumber_mills_price": 480000,

            "component_factories_price": 2200000,
            "component_factories_resource": {"steel": 20},
            "component_factories_resource2": {"aluminium": 20},

            "steel_mills_price": 1900000,
            "steel_mills_resource": {"aluminium": 60},

            "ammunition_factories_price": 1600000,
            "aluminium_refineries_price": 1750000,
            "oil_refineries_price": 1500000
        }

        if units not in allUnits:
            return error("No such unit exists.", 400)

        if units in ["land", "cityCount"]:
            table = "provinces"
        else:
            table = "proInfra"

        price = unit_prices[f"{units}_price"]
        totalPrice = int(wantedUnits * price)

        resources_used = []

        try:
            resource_data = next(iter(unit_prices[f'{units}_resource'].items()))

            resources_used.append(resource_data)
        except KeyError:
            pass

        try:
            resource2_data = next(iter(unit_prices[f'{units}_resource2'].items()))

            resources_used.append(resource2_data)
        except KeyError:
            pass

        curUnStat = f"SELECT {units} FROM {table} " +  "WHERE id=%s"
        db.execute(curUnStat, (province_id,))
        currentUnits = int(db.fetchone()[0])

        if units in city_units:
            slot_type = "city"
        elif units in land_units:
            slot_type = "land"
        else: # If unit is cityCount or land
            free_slots = 0
            slot_type = None

        if slot_type is not None:
            free_slots = get_free_slots(province_id, slot_type)

        def resource_stuff():

            for resource_data in resources_used:

                resource = resource_data[0]
                amount = resource_data[1]

                if way == "buy":

                    current_resource_stat = f"SELECT {resource} FROM resources" + " WHERE id=%s"
                    db.execute(current_resource_stat, (cId,))
                    current_resource = int(db.fetchone()[0])

                    new_resource = amount * wantedUnits - current_resource

                    if new_resource < 0:
                        return error(400, f"You don't have enough {resource}")

                    resource_update_stat = f"UPDATE resources SET {resource}=" + "%s WHERE id=%s"
                    db.execute(resource_update_stat, (new_resource, cId,))

                elif way == "sell":

                    current_resource_stat = f"SELECT {resource} FROM resources" + " WHERE id=%s"
                    db.execute(current_resource_stat, (cId,))
                    current_resource = int(db.fetchone()[0])

                    new_resource = current_resource + amount * wantedUnits

                    resource_update_stat = f"UPDATE resources SET {resource}=" + "%s WHERE id=%s"
                    db.execute(resource_update_stat, (new_resource, cId,))

        if way == "sell":

            if wantedUnits > currentUnits:  # Checks if user has enough units to sell
                return error("You don't have enough units", 400)

            unitUpd = f"UPDATE {table} SET {units}" + "=%s WHERE id=%s"
            db.execute(unitUpd, ((currentUnits - wantedUnits), province_id))

            new_money = gold + (wantedUnits * price)

            db.execute("UPDATE stats SET gold=(%s) WHERE id=(%s)", (new_money, cId))

            resource_stuff()

        elif way == "buy":

            if int(totalPrice) > int(gold): # Checks if user wants to buy more units than he has gold
                return error("you don't have enough money", 400)

            if free_slots < wantedUnits and units not in ["cityCount", "land"]:
                return error(400, f"You don't have enough city slots to buy {wantedUnits} units. Buy more cities to fix this problem")

            db.execute("UPDATE stats SET gold=(%s) WHERE id=(%s)", (int(gold)-int(totalPrice), cId,))

            updStat = f"UPDATE {table} SET {units}" + "=%s WHERE id=%s"
            db.execute(updStat, ((currentUnits + wantedUnits), province_id))

            resource_stuff()

        connection.commit()
        connection.close()

        return redirect(f"/province/{province_id}")
