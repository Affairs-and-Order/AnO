from flask import request, render_template, session, redirect
from helpers import login_required
import psycopg2
from helpers import get_influence, error
from app import app
import os
import variables
from dotenv import load_dotenv
from coalitions import get_user_role
from tasks import calc_pg, calc_ti, rations_needed
from collections import defaultdict
from policies import get_user_policies
from operator import itemgetter
from datetime import datetime
from wars import target_data
load_dotenv()

app.config['UPLOAD_FOLDER'] = 'static/flags'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2 Mb limit


def get_econ_statistics(cId):

    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = conn.cursor()

    db.execute("SELECT id FROM provinces WHERE userId=%s", (cId,))
    provinces_list = db.fetchall()
    provinces = []

    for pId in provinces_list:
        provinces.append(pId[0])

    provinces = tuple(provinces)

    total = {}
    total = defaultdict(lambda: 0, total)

    # This is a pretty bad way of doing this, but the best
    # I thought of in the time given
    # TODO: find way to do this that would take less LOC
    try:
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
        aluminium_refineries, oil_refineries
        FROM proInfra WHERE id IN %s
        """, (provinces,))
        province_units = db.fetchall()
    except:
        province_units = []

    for units in province_units:

        units = list(units)

        coal_burners, oil_burners, hydro_dams, nuclear_reactors, solar_fields, \
            gas_stations, general_stores, farmers_markets, malls, banks, \
            city_parks, hospitals, libraries, universities, monorails, \
            army_bases, harbours, aerodomes, admin_buildings, silos, \
            farms, pumpjacks, coal_mines, bauxite_mines, \
            copper_mines, uranium_mines, lead_mines, iron_mines, \
            lumber_mills, component_factories, steel_mills, ammunition_factories, \
            aluminium_refineries, oil_refineries = units

        total["coal_burners"] += coal_burners
        total["oil_burners"] += oil_burners
        total["hydro_dams"] += hydro_dams
        total["nuclear_reactors"] += nuclear_reactors
        total["solar_fields"] += solar_fields

        total["gas_stations"] += gas_stations
        total["general_stores"] += general_stores
        total["farmers_markets"] += farmers_markets
        total["malls"] += malls
        total["banks"] += banks

        total["city_parks"] += city_parks
        total["hospitals"] += hospitals
        total["libraries"] += libraries
        total["universities"] += universities
        total["monorails"] += monorails

        total["army_bases"] += army_bases
        total["harbours"] += harbours
        total["aerodomes"] += aerodomes
        total["admin_buildings"] += admin_buildings
        total["silos"] += silos

        total["farms"] += farms
        total["pumpjacks"] + pumpjacks
        total["coal_mines"] += coal_mines
        total["bauxite_mines"] += bauxite_mines

        total["copper_mines"] += copper_mines
        total["uranium_mines"] += uranium_mines
        total["lead_mines"] += lead_mines
        total["iron_mines"] += iron_mines

        total["lumber_mills"] += lumber_mills
        total["component_factories"] += component_factories
        total["steel_mills"] += steel_mills
        total["ammunition_factories"] += ammunition_factories

        total["aluminium_refineries"] += aluminium_refineries
        total["oil_refineries"] += oil_refineries

    expenses = {}
    expenses = defaultdict(lambda: defaultdict(lambda: 0), expenses)

    def get_unit_type(unit):
        for type_name, buildings in variables.INFRA_TYPE_BUILDINGS.items():
            if unit in buildings:
                return type_name

    def check_for_resource_upkeep(unit, amount):
        try:
            convert_minus = list(
                variables.INFRA[f'{unit}_convert_minus'][0].items())[0]
            minus = convert_minus[0]
            minus_amount = convert_minus[1] * amount
        except KeyError:
            minus, minus_amount = [None, None]
            convert_minus = []
            return False

        if minus != None:
            unit_type = get_unit_type(unit)
            expenses[unit_type][minus] += minus_amount
        return True

    def check_for_monetary_upkeep(unit, amount):
        operating_costs = int(variables.INFRA[f'{unit}_money']) * amount
        unit_type = get_unit_type(unit)
        expenses[unit_type]["money"] += operating_costs

    for unit, amount in total.items():
        if amount != 0:
            check_for_resource_upkeep(unit, amount)
            check_for_monetary_upkeep(unit, amount)

    return expenses


def format_econ_statistics(statistics):

    formatted = {}
    formatted = defaultdict(lambda: "", formatted)

    for unit_type, unit_type_data in statistics.items():
        unit_type_data = list(unit_type_data.items())
        idx = 0
        for resource, amount in unit_type_data:

            amount = "{:,}".format(amount)

            if idx != len(unit_type_data)-1:
                expense_string = f"{amount} {resource}, "
            else:
                expense_string = f"{amount} {resource}"

            if resource == "money":  # Bit of a hack but the simplest and cleanest approach
                expense_string = expense_string.replace(" money", "")

            formatted[unit_type] += expense_string
            idx += 1

    return formatted


def get_revenue(cId):

    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = conn.cursor()

    cg_needed = cg_need(cId)

    db.execute("SELECT id FROM provinces WHERE userId=%s", (cId,))
    provinces_list = db.fetchall()

    revenue = {
        "gross": {},
        "net": {}
    }

    infra = variables.INFRA
    resources = variables.RESOURCES
    resources.append("money")
    for resource in resources:
        revenue["gross"][resource] = 0
        revenue["net"][resource] = 0

    for province_id in provinces_list:
        province_id = province_id[0]

        buildings = variables.BUILDINGS

        for building in buildings:
            building_query = f"SELECT {building}" + \
                " FROM proInfra WHERE id=%s"
            db.execute(building_query, (province_id,))
            building_count = db.fetchone()[0]

            # Gross and initial net calculations
            try:
                plus_data = list(infra[f'{building}_plus'].items())[0]

                plus_resource = plus_data[0]
                plus_amount = plus_data[1]

                if building == "farms":
                    db.execute(
                        "SELECT land FROM provinces WHERE id=%s", (province_id,))
                    land = db.fetchone()[0]
                    plus_amount *= land

                total = building_count * plus_amount
                revenue["gross"][plus_resource] += total
                revenue["net"][plus_resource] += total
            except:
                pass

            operating_costs = infra[f'{building}_money'] * building_count
            revenue["net"]["money"] -= operating_costs

            # Net removal from initial net
            try:
                convert_minus = infra[f'{building}_convert_minus']
                for data in convert_minus:
                    minus_resource, minus_amount = list(data.items())[0]
                    total = building_count * minus_amount
                    revenue["net"][minus_resource] -= total
            except:
                pass

    db.execute("SELECT consumer_goods FROM resources WHERE id=%s", (cId,))
    current_cg = db.fetchone()[0]
    current_cg += revenue["gross"]["consumer_goods"]

    ti_money, ti_cg = calc_ti(cId, current_cg)

    # Updates money
    db.execute("SELECT gold FROM stats WHERE id=%s", (cId,))
    current_money = db.fetchone()[0]

    revenue["gross"]["money"] += ti_money - current_money
    revenue["net"]["money"] += ti_money - current_money

    if current_cg - ti_cg == cg_needed:
        revenue["net"]["consumer_goods"] = cg_needed * - \
            1 + revenue["gross"]["consumer_goods"]
    elif current_cg > ti_cg:
        revenue["net"]["consumer_goods"] = revenue["gross"]["consumer_goods"] * -1

    db.execute("SELECT rations FROM resources WHERE id=%s", (cId,))
    current_rations = db.fetchone()[0]

    prod_rations = revenue["gross"]["rations"]
    new_rations = next_turn_rations(cId, prod_rations)
    revenue["net"]["rations"] = new_rations - current_rations

    return revenue


def next_turn_rations(cId, prod_rations):

    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = conn.cursor()

    db.execute("SELECT id FROM provinces WHERE userId=%s", (cId,))
    provinces = db.fetchall()

    db.execute("SELECT rations FROM resources WHERE id=%s", (cId,))
    current_rations = db.fetchone()[0] + prod_rations

    for pId in provinces:

        rations, _ = calc_pg(pId, current_rations)
        current_rations = rations

    return current_rations


@app.route("/delete_news/<int:id>", methods=["POST"])
@login_required
def delete_news(id):
    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))
    db = conn.cursor()
    db.execute("SELECT destination_id FROM news WHERE id=(%s)", (id,))
    destination_id = db.fetchone()[0]
    if destination_id == session["user_id"]:
        db.execute("DELETE FROM news WHERE id=(%s)", (id,))
        conn.commit()
        return "200"
    else:
        return "403"

# The amount of consumer goods a player needs to fill up fully


def cg_need(user_id):

    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = conn.cursor()

    db.execute("SELECT SUM(population) FROM provinces WHERE userId=%s", (user_id,))
    population = db.fetchone()[0]
    if population is None:
        population = 0

    # How many consumer goods are needed to feed a nation
    cg_needed = population // variables.CG_PER

    return cg_needed


@app.route("/my_country")
@login_required
def my_country():
    user_id = session["user_id"]
    return redirect(f"/country/id={user_id}")


@app.route("/country/id=<cId>")
@login_required
def country(cId):

    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    try:
        db.execute(
            "SELECT username, description, date FROM users WHERE id=%s", (cId,))
        username, description, dateCreated = db.fetchall()[0]
    except:
        return error(404, "Country doesn't exit")

    policies = get_user_policies(cId)
    print(policies)
    influence = get_influence(cId)

    db.execute(
        "SELECT SUM(population), AVG(happiness), AVG(productivity), COUNT(id) FROM provinces WHERE userId=%s", (cId,))
    population, happiness, productivity, provinceCount = db.fetchall()[0]

    db.execute("SELECT location FROM stats WHERE id=%s", (cId,))
    location = db.fetchone()[0]

    db.execute("SELECT provinceName, id, population, cityCount, land, happiness, productivity FROM provinces WHERE userId=(%s) ORDER BY id ASC", (cId,))
    provinces = db.fetchall()

    cg_needed = cg_need(cId)

    try:
        status = cId == str(session["user_id"])
    except:
        status = False

    try:
        db.execute("SELECT colId, role FROM coalitions WHERE userId=(%s)", (cId,))
        coalition_data = db.fetchall()[0]

        colId = coalition_data[0]
        colRole = coalition_data[1]

        db.execute("SELECT name FROM colNames WHERE id =%s", (colId,))
        colName = db.fetchone()[0]

    except:
        colId = 0
        colRole = None
        colName = ""

    try:
        db.execute("SELECT flag FROM colNames WHERE id=%s", (colId,))
        colFlag = db.fetchone()[0]
    except:
        colFlag = None

    try:
        db.execute("SELECT flag FROM users WHERE id=(%s)", (cId,))
        flag = db.fetchone()[0]
    except:
        flag = None

    spyCount = 0
    successChance = 0

    """
    uId == str(session["user_id"])
    db.execute("SELECT spies FROM military WHERE id=(%s)", (uId,))
    spyCount = db.fetchone()[0]
    spyPrep = 1 # this is an integer from 1 to 5, alter the stats table to include this data

    eSpyCount = db.execute("SELECT spies FROM military WHERE id=(%s)", (cId,))
    eDefcon = 1 # this is an integer from 1 to 5, alter the stats table to include this data

    if eSpyCount == 0:
        successChance = 100
    else:
        successChance = spyCount * spyPrep / eSpyCount / eDefcon
    """

    # News page
    idd = int(cId)
    news = []
    news_amount = 0
    if idd == session["user_id"]:
        # TODO: handle this as country/id=<int:cId>
        db.execute(
            "SELECT message,date,id FROM news WHERE destination_id=(%s)", (cId,))

        # data order in the tuple appears as in the news schema (notice this when work with this data using jija)
        news = db.fetchall()
        news_amount = len(news)

    # Revenue stuff
    if status:
        revenue = get_revenue(cId)

        db.execute(
            "SELECT name, type, resource, amount, date FROM revenue WHERE user_id=%s", (cId,))
        expenses = db.fetchall()

        statistics = get_econ_statistics(cId)
        statistics = format_econ_statistics(statistics)
    else:
        revenue = {}
        expenses = []
        statistics = {}

    rations_need = rations_needed(cId)

    connection.close()
    return render_template("country.html", username=username, cId=cId, description=description,
                           happiness=happiness, population=population, location=location, status=status,
                           provinceCount=provinceCount, colName=colName, dateCreated=dateCreated, influence=influence,
                           provinces=provinces, colId=colId, flag=flag, spyCount=spyCount, successChance=successChance,
                           colFlag=colFlag, colRole=colRole, productivity=productivity, revenue=revenue, news=news, news_amount=news_amount,
                           cg_needed=cg_needed, rations_need=rations_need, expenses=expenses, statistics=statistics, policies=policies)


@app.route("/countries", methods=["GET"])
@login_required
def countries():

    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    cId = session["user_id"]

    search = request.values.get("search")
    lowerinf = request.values.get("lowerinf")
    upperinf = request.values.get("upperinf")
    province_range = request.values.get("province_range")
    sort = request.values.get("sort")
    sortway = request.values.get("sortway")

    if sort == "war_range":
        target = target_data(cId)
        lowerinf = target["lower"]
        upperinf = target["upper"]
        province_range = target["province_range"]

    print(province_range)

    db.execute("""SELECT users.id, users.username, users.date, users.flag, COALESCE(SUM(provinces.population), 0) AS province_population,
coalitions.colId, colNames.name, COUNT(provinces.id) as provinces_count
FROM USERS
LEFT JOIN provinces ON users.id = provinces.userId
LEFT JOIN coalitions ON users.id = coalitions.userId
LEFT JOIN colNames ON colNames.id = coalitions.colId
WHERE users.id != %s
GROUP BY users.id, coalitions.colId, colNames.name
HAVING COUNT(provinces.id) >= %s;""", (cId, province_range,))
    dbResults = db.fetchall()

    connection.close()

    # Hack to add influence into the query, filter influence, province range, etc.
    results = []
    for user in dbResults:
        addUser = True
        user_id = user[0]
        user = list(user)
        influence = get_influence(user_id)

        user_date = user[2]
        date = datetime.fromisoformat(user_date)
        unix = int((date - datetime(1970, 1, 1)).total_seconds())

        user.append(influence)
        user.append(unix)
        if search:
            username = user[1]
            if search not in username:
                addUser = False
        if lowerinf:
            if influence < float(lowerinf):
                addUser = False
        if upperinf:
            if influence > float(upperinf):
                addUser = False
        if province_range:
            province_count = user[7]
            if province_count > int(province_range):
                addUser = False
        if addUser:
            results.append(user)

    if not sort:
        sortway = "desc"
        sort = "influence"

    reverse = False
    if sortway == "desc":
        reverse = True
    if sort == "influence":
        results = sorted(results, key=itemgetter(8), reverse=reverse)
    if sort == "age":
        results = sorted(results, key=itemgetter(9), reverse=reverse)
    if sort == "population":
        results = sorted(results, key=itemgetter(4), reverse=reverse)
    if sort == "provinces":
        results = sorted(results, key=itemgetter(7), reverse=reverse)

    return render_template("countries.html", countries=results)


@ app.route("/update_country_info", methods=["POST"])
@ login_required
def update_info():

    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()
    cId = session["user_id"]

    # Description changing
    description = request.form["description"]

    if description not in ["None", ""]:
        db.execute("UPDATE users SET description=%s WHERE id=%s",
                   (description, cId))

    # Flag changing
    ALLOWED_EXTENSIONS = ['png', 'jpg']

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    flag = request.files["flag_input"]
    if flag:

        if not allowed_file(flag.filename):
            return error(400, "Bad flag file format")

        current_filename = flag.filename

        try:
            db.execute("SELECT flag FROM users WHERE id=(%s)", (cId,))
            current_flag = db.fetchone()[0]

            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], current_flag))
        except:
            pass

        # Save the file & shit
        if allowed_file(current_filename):
            extension = current_filename.rsplit('.', 1)[1].lower()
            filename = f"flag_{cId}" + '.' + extension
            new_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            flag.save(new_path)
            db.execute("UPDATE users SET flag=(%s) WHERE id=(%s)",
                       (filename, cId))

    """
    bg_flag = request.files["bg_flag_input"]
    if bg_flag and allowed_file(bg_flag.filename):

        print("bg flag")

        # Check if the user already has a flag
        try:
            db.execute("SELECT bg_flag FROM users WHERE id=(%s)", (cId,))
            current_bg_flag = db.fetchone()[0]

            os.remove(os.path.join(
                app.config['UPLOAD_FOLDER'], current_bg_flag))
        except FileNotFoundError:
            pass

        # Save the file & shit
        current_filename = bg_flag.filename
        if allowed_file(current_filename):
            extension = current_filename.rsplit('.', 1)[1].lower()
            filename = f"bg_flag_{cId}" + '.' + extension
            flag.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            db.execute("UPDATE users SET bg_flag=(%s) WHERE id=(%s)",
                       (filename, cId))
    """

    # Location changing
    new_location = request.form.get("countryLocation")

    continents = ["Tundra", "Savanna", "Desert", "Jungle",
                  "Boreal Forest", "Grassland", "Mountain Range"]

    if new_location not in continents and new_location not in ["", "none"]:
        return error(400, "No such continent")

    if new_location not in ["", "none"]:

        db.execute("SELECT id FROM provinces WHERE userId=%s", (cId,))
        provinces = db.fetchall()

        for province_id in provinces:

            province_id = province_id[0]

            db.execute(
                "UPDATE proInfra SET pumpjacks=0 WHERE id=%s", (province_id,))
            db.execute(
                "UPDATE proInfra SET coal_mines=0 WHERE id=%s", (province_id,))
            db.execute(
                "UPDATE proInfra SET bauxite_mines=0 WHERE id=%s", (province_id,))
            db.execute(
                "UPDATE proInfra SET copper_mines=0 WHERE id=%s", (province_id,))
            db.execute(
                "UPDATE proInfra SET uranium_mines=0 WHERE id=%s", (province_id,))
            db.execute(
                "UPDATE proInfra SET lead_mines=0 WHERE id=%s", (province_id,))
            db.execute(
                "UPDATE proInfra SET iron_mines=0 WHERE id=%s", (province_id,))
            db.execute(
                "UPDATE proInfra SET lumber_mills=0 WHERE id=%s", (province_id,))

        db.execute("UPDATE stats SET location=(%s) WHERE id=(%s)",
                   (new_location, cId))

    connection.commit()  # Commits the data
    connection.close()  # Closes the connection

    return redirect(f"/country/id={cId}")  # Redirects the user to his country


@ app.route("/delete_own_account", methods=["POST"])
@ login_required
def delete_own_account():

    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()
    cId = session["user_id"]

    # Deletes all the info from database created upon signup
    db.execute("DELETE FROM users WHERE id=(%s)", (cId,))
    db.execute("DELETE FROM stats WHERE id=(%s)", (cId,))
    db.execute("DELETE FROM military WHERE id=(%s)", (cId,))
    db.execute("DELETE FROM resources WHERE id=(%s)", (cId,))
    # Deletes all market things the user is associated with
    db.execute("DELETE FROM offers WHERE user_id=(%s)", (cId,))
    db.execute("DELETE FROM wars WHERE defender=%s OR attacker=%s", (cId, cId))

    # Deletes all the users provinces and their infrastructure
    db.execute("SELECT id FROM provinces WHERE userId=%s", (cId,))
    province_ids = db.fetchall()
    for province_id in province_ids:
        province_id = province_id[0]
        db.execute("DELETE FROM provinces WHERE id=(%s)", (province_id,))
        db.execute("DELETE FROM proInfra WHERE id=(%s)", (province_id,))

    db.execute("DELETE FROM upgrades WHERE user_id=%s", (cId,))
    db.execute("DELETE FROM trades WHERE offeree=%s OR offerer=%s", (cId, cId))
    db.execute("DELETE FROM spyinfo WHERE spyer=%s OR spyee=%s", (cId, cId))
    db.execute("DELETE FROM requests WHERE reqId=%s", (cId,))
    db.execute(
        "DELETE FROM reparation_tax WHERE loser=%s OR winner=%s", (cId, cId))
    db.execute("DELETE FROM peace WHERE author=%s", (cId,))

    try:
        coalition_role = get_user_role(cId)
    except:
        coalition_role = None
    if coalition_role != "leader":
        pass
    else:

        db.execute("SELECT colId FROM coalitions WHERE userId=%s", (cId,))
        user_coalition = db.fetchone()[0]

        db.execute(
            "SELECT COUNT(userId) FROM coalitions WHERE role='leader' AND colId=%s", (user_coalition,))
        leader_count = int(db.fetchone()[0])

        if leader_count != 1:
            pass
        else:
            db.execute("DELETE FROM coalitions WHERE colId=%s",
                       (user_coalition,))
            db.execute("DELETE FROM colNames WHERE id=%s", (user_coalition,))
            db.execute("DELETE FROM colBanks WHERE colid=%s",
                       (user_coalition,))
            db.execute("DELETE FROM requests WHERE colId=%s",
                       (user_coalition,))

    db.execute("DELETE FROM coalitions WHERE userId=%s", (cId,))
    db.execute("DELETE FROM colBanksRequests WHERE reqId=%s", (cId,))

    connection.commit()
    connection.close()

    session.clear()

    return redirect("/")
