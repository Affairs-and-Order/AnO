from flask import request, render_template, session, redirect
from helpers import login_required
import psycopg2
from helpers import get_influence, error
from tasks import calc_pg, calc_ti, rations_needed
from app import app
import os
import variables
from dotenv import load_dotenv
from coalitions import get_user_role
from collections import defaultdict
from policies import get_user_policies
from operator import itemgetter
from datetime import datetime
from wars import target_data
import math
load_dotenv()

from psycopg2.extras import RealDictCursor

app.config['UPLOAD_FOLDER'] = 'static/flags'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2 Mb limit

# TODO: rewrite this function for fucks sake
def get_econ_statistics(cId):

    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    dbdict = conn.cursor(cursor_factory=RealDictCursor)

    # TODO: less loc
    try:
        dbdict.execute(
        """
        SELECT
        SUM(proInfra.coal_burners) AS coal_burners,
        SUM(proInfra.oil_burners) AS oil_burners,
        SUM(proInfra.hydro_dams) AS hydro_dams ,
        SUM(proInfra.nuclear_reactors) AS nuclear_reactors,
        SUM(proInfra.solar_fields) AS solar_fields,
        SUM(proInfra.gas_stations) AS gas_stations,
        SUM(proInfra.general_stores) AS general_stores,
        SUM(proInfra.farmers_markets) AS farmers_markets,
        SUM(proInfra.malls) AS malls,
        SUM(proInfra.banks) AS banks,
        SUM(proInfra.city_parks) AS city_parks,
        SUM(proInfra.hospitals) AS hospitals,
        SUM(proInfra.libraries) AS libraries,
        SUM(proInfra.universities) AS universities,
        SUM(proInfra.monorails) AS monorails,
        SUM(proInfra.army_bases) AS army_bases,
        SUM(proInfra.harbours) AS harbours,
        SUM(proInfra.aerodomes) AS aerodomes,
        SUM(proInfra.admin_buildings) AS admin_buildings,
        SUM(proInfra.silos) AS silos,
        SUM(proInfra.farms) AS farms,
        SUM(proInfra.pumpjacks) AS pumpjacks,
        SUM(proInfra.coal_mines) AS coal_mines,
        SUM(proInfra.bauxite_mines) AS bauxite_mines,
        SUM(proInfra.copper_mines) AS copper_mines,
        SUM(proInfra.uranium_mines) AS uranium_mines,
        SUM(proInfra.lead_mines) AS lead_mines,
        SUM(proInfra.iron_mines) AS iron_mines,
        SUM(proInfra.lumber_mills) AS lumber_mills,
        SUM(proInfra.component_factories) AS component_factories,
        SUM(proInfra.steel_mills) AS steel_mills,
        SUM(proInfra.ammunition_factories) AS ammunition_factories,
        SUM(proInfra.aluminium_refineries) AS aluminium_refineries,
        SUM(proInfra.oil_refineries) AS oil_refineries
        FROM proInfra LEFT JOIN provinces ON provinces.id=proInfra.id WHERE provinces.userId=%s;
        """, (cId,))
        total = dict(dbdict.fetchone())
    except:
        total = {}

    expenses = {}
    expenses = defaultdict(lambda: defaultdict(lambda: 0), expenses)

    def get_unit_type(unit):
        for type_name, buildings in variables.INFRA_TYPE_BUILDINGS.items():
            if unit in buildings:
                return type_name

    def check_for_resource_upkeep(unit, amount):
        try:
            convert_minus = list(variables.INFRA[f'{unit}_convert_minus'][0].items())[0]
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
        print(unit, amount)
        if amount != 0 and amount is not None:
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
    dbd = conn.cursor(cursor_factory=RealDictCursor)

    cg_needed = cg_need(cId)

    db.execute("SELECT id FROM provinces WHERE userId=%s", (cId,))
    provinces = db.fetchall()

    revenue = {
        "gross": {},
        "net": {}
    }

    """
    infra = variables.NEW_INFRA
    resources = variables.RESOURCES
    resources.append("money")
    for resource in resources:
        revenue["gross"][resource] = 0
        revenue["net"][resource] = 0

    for province_id in provinces_list:
        province_id = province_id[0]

        buildings = variables.BUILDINGS
        

        for building in buildings:
            building_query = f"SELECT {building}" + " FROM proInfra WHERE id=%s"
            db.execute(building_query, (province_id,))
            building_count = db.fetchone()[0]

            # Gross and initial net calculations
            plus = infra[building]["plus"]
            presource = list(plus.keys())[0]
            pamount = plus[resource]

            if building == "farms":
                db.execute("SELECT land FROM provinces WHERE id=%s", (province_id,))
                land = db.fetchone()[0]
                pamount *= land

            total = building_count * pamount
            revenue["gross"][presource] += total
            revenue["net"][presource] += total

            operating_costs = infra[building]["money"] * building_count
            revenue["net"]["money"] -= operating_costs

            # Net removal from initial net
            minus = infra[building]["minus"]
            mresource = list(minus.keys())[0]
            mamount = minus[mresource]

            total = building_count * mamount
            revenue["net"][presource] -= total
    """
    infra = variables.NEW_INFRA
    resources = variables.RESOURCES
    resources.extend(["money", "energy"])
    for resource in resources:
        revenue["gross"][resource] = 0
        revenue["net"][resource] = 0
    for province in provinces:
        province = province[0]

        dbd.execute("SELECT * FROM proInfra WHERE id=%s", (province,))
        buildings = dict(dbd.fetchone())

        for building, build_count in buildings.items():
            if building == "id": continue

            operating_costs = infra[building]["money"] * build_count
            revenue["net"]["money"] -= operating_costs

            try:
                plus = infra[building]["plus"]
            except KeyError:
                plus = {}
            for resource, amount in plus.items():
                if building == "farms":
                    db.execute("SELECT land FROM provinces WHERE id=%s", (province,))
                    land = db.fetchone()[0]
                    amount += (land * variables.LAND_FARM_MULTIPLIER)

                total = build_count * amount
                revenue["gross"][resource] += total
            try:
                minus = infra[building]["minus"]
            except KeyError:
                minus = {}
            for resource, amount in minus.items():
                total = build_count * amount
                revenue["net"][resource] = revenue["gross"][resource] - total
                
    db.execute("SELECT consumer_goods, rations FROM resources WHERE id=%s", (cId,))
    current_cg, current_rations = db.fetchone()
    current_cg += revenue["net"]["consumer_goods"]

    ti_money, ti_cg = calc_ti(cId)

    # Updates money
    revenue["gross"]["money"] += ti_money
    revenue["net"]["money"] += ti_money

    revenue["net"]["consumer_goods"] += ti_cg

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
    cg_needed = math.ceil(population / variables.CG_PER)

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
        db.execute("SELECT users.username, stats.location, users.description, users.date, users.flag FROM users INNER JOIN stats ON users.id=stats.id WHERE users.id=%s", (cId,))
        username, location, description, dateCreated, flag = db.fetchall()[0]
    except:
        return error(404, "Country doesn't exit")

    policies = get_user_policies(cId)
    influence = get_influence(cId)

    db.execute("SELECT SUM(population), AVG(happiness), AVG(productivity), COUNT(id) FROM provinces WHERE userId=%s", (cId,))
    population, happiness, productivity, provinceCount = db.fetchall()[0]

    db.execute("SELECT provinceName, id, population, cityCount, land, happiness, productivity FROM provinces WHERE userId=(%s) ORDER BY id ASC", (cId,))
    provinces = db.fetchall()

    cg_needed = cg_need(cId)

    try:
        status = cId == str(session["user_id"])
    except:
        status = False

    try:
        db.execute("SELECT coalitions.colId, coalitions.role, colNames.name, colNames.flag FROM coalitions INNER JOIN colNames ON coalitions.colId=colNames.id WHERE coalitions.userId=%s", (cId,))
        colId, colRole, colName, colFlag = db.fetchall()[0]
    except:
        colId = 0; colRole = None; colName = ""; colFlag = None

    spy = {}
    uId = session["user_id"]
    db.execute("SELECT spies FROM military WHERE military.id=(%s)", (uId,))
    spy["count"] = db.fetchone()[0]

    # News page
    idd = int(cId)
    news = []
    news_amount = 0
    if idd == session["user_id"]:
        # TODO: handle this as country/id=<int:cId>
        db.execute("SELECT message,date,id FROM news WHERE destination_id=(%s)", (cId,))
        # data order in the tuple appears as in the news schema (notice this when work with this data using jija)
        news = db.fetchall()
        news_amount = len(news)

    # Revenue stuff
    if status:
        revenue = get_revenue(cId)
        db.execute("SELECT name, type, resource, amount, date FROM revenue WHERE user_id=%s", (cId,))
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
                           provinces=provinces, colId=colId, flag=flag, spy=spy,
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

    if not province_range:
        province_range = 0

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
        if search and search not in user[1]: # user[1] - username
            addUser = False
        if lowerinf and influence < float(lowerinf):
            addUser = False
        if upperinf and influence > float(upperinf):
            addUser = False
        if province_range and user[7] > int(province_range): # user[7] - province count
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
        db.execute("UPDATE users SET description=%s WHERE id=%s", (description, cId))

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
            db.execute("UPDATE proInfra SET pumpjacks=0, coal_mines=0, bauxite_mines=0, copper_mines=0, uranium_mines=0, lead_mines=0, iron_mines=0, lumber_mills=0 WHERE id=%s", (province_id,))
        db.execute("UPDATE stats SET location=%s WHERE id=%s", (new_location, cId))

    connection.commit() 
    connection.close() 

    return redirect(f"/country/id={cId}")  # Redirects the user to his country

# TODO: check if you can DELETE with one statement
@app.route("/delete_own_account", methods=["POST"])
@login_required
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
    db.execute("DELETE FROM reparation_tax WHERE loser=%s OR winner=%s", (cId, cId))
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

        db.execute("SELECT COUNT(userId) FROM coalitions WHERE role='leader' AND colId=%s", (user_coalition,))
        leader_count = db.fetchone()[0]

        if leader_count != 1:
            pass
        else:
            db.execute("DELETE FROM coalitions WHERE colId=%s", (user_coalition,))
            db.execute("DELETE FROM colNames WHERE id=%s", (user_coalition,))
            db.execute("DELETE FROM colBanks WHERE colid=%s", (user_coalition,))
            db.execute("DELETE FROM requests WHERE colId=%s", (user_coalition,))

    db.execute("DELETE FROM coalitions WHERE userId=%s", (cId,))
    db.execute("DELETE FROM colBanksRequests WHERE reqId=%s", (cId,))

    connection.commit()
    connection.close()

    session.clear()

    return redirect("/")
