from flask import Flask, request, render_template, session, redirect
from flask_session import Session
from tempfile import mkdtemp
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from helpers import login_required, error
import NationsScript as Game
import datetime
import _pickle as pickle
import random
from celery import Celery
# from celery.schedules import crontab # arent currently using but will be later on
from helpers import get_influence, get_coalition_influence

# Game.ping() # temporarily removed this line because it might make celery not work

app = Flask(__name__)

#basic cache configuration
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config["CELERY_BROKER_URL"] = 'amqp://ano:ano@localhost:5672/ano'
app.config["CELERY_RESULT_BACKEND"] = 'amqp://ano:ano@localhost:5672/ano'

celery_beat_schedule = {
    "time_scheduler": {
        "task": "app.populationGrowth",
        # Run every second
        "schedule": 1.0,
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
    def get_col_name():
        conn = sqlite3.connect('affo/aao.db') # connects to db
        db = conn.cursor()
        try:
            inColit = db.execute("SELECT colId FROM coalitions WHERE userId=(?)", (session["user_id"], )).fetchone()[0]
            inCol = f"/coalition/{inColit}"
            return inCol
        except:
            inCol = error(404, "Page Not Found")
            return inCol
    def get_resource_amount():
        conn = sqlite3.connect('affo/aao.db') # connects to db
        db = conn.cursor()
        session_id = session["user_id"]

        money = db.execute("SELECT gold FROM stats WHERE id=(?)", (session_id,)).fetchone()[0] # DONE

        rations = 0 # db.execute("SELECT rations FROM resources WHERE userId=(?)", (session_id,)).fetchone()[0]
        oil = db.execute("SELECT oil FROM resources WHERE id=(?)", (session_id,)).fetchone()[0] # DONE
        coal = db.execute("SELECT coal FROM resources WHERE id=(?)", (session_id,)).fetchone()[0] # DONE
        uranium = db.execute("SELECT uranium FROM resources WHERE id=(?)", (session_id,)).fetchone()[0] # DONE
        bauxite = db.execute("SELECT bauxite FROM resources WHERE id=(?)", (session_id,)).fetchone()[0] # DONE
        iron = db.execute("SELECT iron FROM resources WHERE id=(?)", (session_id,)).fetchone()[0] # DONE
        lead = db.execute("SELECT lead FROM resources WHERE id=(?)", (session_id,)).fetchone()[0] # DONE
        copper = db.execute("SELECT copper FROM resources WHERE id=(?)", (session_id,)).fetchone()[0] # DONE

        components = 0 # db.execute("SELECT rations FROM resources WHERE userId=(?)", (session_id,)).fetchone()[0]
        steel = 0 # db.execute("SELECT rations FROM resources WHERE userId=(?)", (session_id,)).fetchone()[0]
        consumer_goods = db.execute("SELECT consumer_goods FROM resources WHERE id=(?)", (session_id,)).fetchone()[0] # DONE

        copper_plates = 0 # db.execute("SELECT rations FROM resources WHERE id=(?)", (session_id,)).fetchone()[0]
        aluminum = 0 # db.execute("SELECT rations FROM resources WHERE id=(?)", (session_id,)).fetchone()[0]
        gasoline = 0 # db.execute("SELECT rations FROM resources WHERE id=(?)", (session_id,)).fetchone()[0]
        ammunition = 0 # db.execute("SELECT rations FROM resources WHERE id=(?)", (session_id,)).fetchone()[0]
        
        lst = [money, rations, oil, coal, uranium, bauxite, iron, lead, copper, components, steel, consumer_goods, copper_plates, aluminum, gasoline, ammunition]
        return lst
    return dict(get_col_name=get_col_name, get_resource_amount=get_resource_amount)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html") # renders index.html when "/" is accesed

@app.route("/error", methods=["GET"])
def errorito(): # fancy view for error, because error function is used
    error(400, "Unknown Error")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        connection = sqlite3.connect('affo/aao.db') # connects to db
        db = connection.cursor() # creates the cursor for db connection

        password = request.form.get("password") # gets the password input from the form
        username = request.form.get("username") # gets the username input from the forms

        if not username or not password: # checks if inputs are blank
            return error(400, "No Password or Username")

        user = db.execute("SELECT * FROM users WHERE username = (?)", (username,)).fetchone() # selects data about user, from users
        connection.commit()

        if user is not None and check_password_hash(user[4], password): # checks if user exists and if the password is correct
            session["user_id"] = user[0] # sets session's user_id to current user's id
            session["logged_in"] = True
            print('User has succesfully logged in.')
            connection.commit()
            connection.close()
            return redirect("/") # redirects user to homepage

        return error(403, "Wrong password")

    else:
        return render_template("login.html") # renders login.html when "/login" is acessed via get

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        
        # connects the db to the signup function
        connection = sqlite3.connect('affo/aao.db') # connects to db
        db = connection.cursor()

        username = request.form.get("username") # gets corresponding form inputs
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        key = request.form.get("key")

        allKeys = db.execute("SELECT key FROM keys").fetchall()
        
        if password != confirmation: # checks if password is = to confirmation password
            return error(400, "Passwords must match.")
        for keys in allKeys: # lmao shitty way to do idk why i did this
            if key == keys[0]:
                hashed = generate_password_hash(password, method='pbkdf2:sha256', salt_length=32) # hashes the inputted password
                db.execute("INSERT INTO users (username, email, hash, date) VALUES (?, ?, ?, ?)", (username, email, hashed, str(datetime.date.today()))) # creates a new user || added account creation date
                user = db.execute("SELECT id FROM users WHERE username = (?)", (username,)).fetchone()
                connection.commit()
                session["user_id"] = user[0] # set's the user's "id" column to the sessions variable "user_id"
                session["logged_in"] = True
                db.execute("INSERT INTO stats (id, location) VALUES (SELECT id FROM users WHERE id = (?)), (?)", (session["user_id"], "Bosfront")) # change the default location                                                                          # "Bosfront" to something else
                db.execute("INSERT INTO ground (id) SELECT id FROM users WHERE id = (?)", (session["user_id"],)) 
                db.execute("INSERT INTO air (id) SELECT id FROM users WHERE id = (?)", (session["user_id"],))
                db.execute("INSERT INTO water (id) SELECT id FROM users WHERE id = (?)", (session["user_id"],))
                db.execute("INSERT INTO special (id) SELECT id FROM users WHERE id = (?)", (session["user_id"],))
                db.execute("INSERT INTO resources (id) SELECT id FROM users WHERE id = (?)", (session["user_id"],))
                db.execute("DELETE FROM keys WHERE key=(?)", (key,)) # deletes the used key
                connection.commit()
                connection.close()
                return redirect("/")
    else:
        return render_template("signup.html")

@login_required
@app.route("/country/id=<cId>")
def country(cId):
    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()

    username = db.execute("SELECT username FROM users WHERE id=(?)", (cId,)).fetchone()[0] # gets country's name from db
    influence = get_influence(cId) # runs the get_influence function of the player's id, which calculates his influence score
    description = db.execute("SELECT description FROM users WHERE id=(?)", (cId,)).fetchone()[0]

    population = db.execute("SELECT population FROM stats WHERE id=(?)", (cId,)).fetchone()[0]
    happiness = db.execute("SELECT happiness FROM stats WHERE id=(?)", (cId,)).fetchone()[0]
    provinceCount = db.execute("SELECT COUNT(*) FROM provinces WHERE userId=(?)", (cId,)).fetchone()[0]

    location = db.execute("SELECT location FROM stats WHERE id=(?)", (cId,)).fetchone()[0]
    gold = db.execute("SELECT gold FROM stats WHERE id=(?)", (cId,)).fetchone()[0]
    dateCreated = db.execute("SELECT date FROM users WHERE id=(?)", (cId,)).fetchone()[0]

    provinceNames = db.execute("SELECT provinceName FROM provinces WHERE userId=(?) ORDER BY provinceId DESC", (cId,)).fetchall()
    provinceIds = db.execute("SELECT provinceId FROM provinces WHERE userId=(?) ORDER BY provinceId DESC", (cId,)).fetchall()

    provinces = zip(provinceNames, provinceIds)

    if str(cId) == str(session["user_id"]):
        status = True
    else:
        status = False

    try:
        colName = db.execute("SELECT name FROM colNames WHERE id = (SELECT colId FROM coalitions WHERE userId=(?))", (cId,)).fetchone()[0]
    except:
        colName = ""


    return render_template("country.html", username=username, cId=cId, description=description,
    happiness=happiness, population=population, location=location, gold=gold, status=status,
    provinceCount=provinceCount, colName=colName, dateCreated=dateCreated, influence=influence,
    provinces=provinces)

@login_required
@app.route("/military", methods=["GET", "POST"])
def military():
    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()
    cId = session["user_id"]
    if request.method == "GET": # maybe optimise this later with css anchors
        # ground
        tanks = db.execute("SELECT tanks FROM ground WHERE id=(?)", (cId,)).fetchone()[0]
        soldiers = db.execute("SELECT soldiers FROM ground WHERE id=(?)", (cId,)).fetchone()[0]
        artillery = db.execute("SELECT artillery FROM ground WHERE id=(?)", (cId,)).fetchone()[0]
        connection.commit()
        # air
        flying_fortresses = db.execute("SELECT flying_fortresses FROM air WHERE id=(?)", (cId,)).fetchone()[0]
        fighter_jets = db.execute("SELECT fighter_jets FROM air WHERE id=(?)", (cId,)).fetchone()[0]
        apaches = db.execute("SELECT apaches FROM air WHERE id=(?)", (cId,)).fetchone()[0]
        connection.commit()
        # water
        destroyers = db.execute("SELECT destroyers FROM water WHERE id=(?)", (cId,)).fetchone()[0]
        cruisers = db.execute("SELECT cruisers FROM water WHERE id=(?)", (cId,)).fetchone()[0]
        submarines = db.execute("SELECT submarines FROM water WHERE id=(?)", (cId,)).fetchone()[0]
        connection.commit()
        # special
        spies = db.execute("SELECT spies FROM special WHERE id=(?)", (cId,)).fetchone()[0]
        icbms = db.execute("SELECT ICBMs FROM special WHERE id=(?)", (cId,)).fetchone()[0]
        nukes = db.execute("SELECT nukes FROM special WHERE id=(?)", (cId,)).fetchone()[0]
        connection.commit()

        return render_template("military.html", tanks=tanks, soldiers=soldiers, artillery=artillery,
        flying_fortresses=flying_fortresses, apaches=apaches, fighter_jets=fighter_jets,
        destroyers=destroyers, cruisers=cruisers, submarines=submarines,
        spies=spies, icbms=icbms, nukes=nukes
        )

person = {"name": "galaxy"}
person["message"] = "Thanks guys :D, you are all so amazing." # easter egg probably or it has something to do with mail xD || aw thats nice

@login_required
@app.route("/market", methods=["GET", "POST"])
def market():
    if request.method == "GET":

        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()
        
        offer_ids = db.execute("SELECT offer_id FROM offers").fetchall()
        
        ids = []
        names = []
        resources = []
        amounts = []
        prices = []
        total_Prices = []
        offer_ids_list = []

        print(offer_ids)

        for i in offer_ids:

            offer_ids_list.append(i[0])
            
            user_id = db.execute("SELECT user_id FROM offers WHERE offer_id=(?)", (i[0],)).fetchone()[0]
            ids.append(user_id)

            name = db.execute("SELECT username FROM users WHERE id=(?)", (user_id,)).fetchone()[0]
            names.append(name)

            resource = db.execute("SELECT resource FROM offers WHERE offer_id=(?)", (i[0],)).fetchone()[0]
            resources.append(resource)

            amount = db.execute("SELECT amount FROM offers WHERE offer_id=(?)", (i[0],)).fetchone()[0]
            amounts.append(amount)

            price = db.execute("SELECT price FROM offers WHERE offer_id=(?)", (i[0],)).fetchone()[0]
            prices.append(price)

            total_Price = db.execute("SELECT price FROM offers WHERE offer_id=(?)", (i[0],)).fetchone()[0]
            total_Prices.append(total_Price)


        offers = zip(ids, names, resources, amounts, prices, total_Prices, offer_ids_list)

        return render_template("market.html", offers=offers)

@login_required
@app.route("/buy_offer/<offer_id>", methods=["POST"])
def buy_market_offer(offer_id):

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()
    
    cId = session["user_id"]

    amount_wanted = request.form.get(f"amount_{offer_id}")

    if offer_id.isnumeric() is False or amount_wanted.isnumeric() is False:
        return error(400, "Values must be numeric")

    offer = db.execute("SELECT resource, amount, price, total_Price, user_id FROM offers WHERE offer_id=(?)", (offer_id,)).fetchone()

    seller_id = int(offer[3])

    resource = offer[0]

    if int(amount_wanted) > int(offer[1]):
        return error(400, "Amount wanted cant be higher than total amount")

    user_gold = db.execute("SELECT gold FROM stats WHERE id=(?)", (cId,)).fetchone()[0]

    if int(amount_wanted) * int(offer[2]) > int(user_gold): # checks if buyer doesnt have enough gold for buyin 

        return error(400, "You don't have enough gold") # returns error if buyer doesnt have enough gold for buying

    gold_sold = user_gold - (int(amount_wanted) * int(offer[2]))

    sellResStat = f"SELECT {resource} FROM resources WHERE id=(?)"
    sellTotRes = db.execute(sellResStat, (seller_id,)).fetchone()[0]

    newSellerresource = (int(sellTotRes) - int(amount_wanted))
    
    db.execute("UPDATE stats SET gold=(?) WHERE id=(?)", (gold_sold, cId)) 

    resRemStat = f"UPDATE resources SET {resource}=(?) WHERE id=(?)" # statement for resource removal for seller
    db.execute(resRemStat, (newSellerresource, seller_id)) # removes the resources the seller sold

    currentBuyerResource = f"SELECT {resource} FROM resources WHERE id=(?)" # statement for getting the current resource from the buyer
    buyerResource = db.execute(currentBuyerResource, (cId,)).fetchone()[0] # executes the statement

    newBuyerResource = int(buyerResource) + int(amount_wanted) # generates the number of the resource the buyer should have

    buyUpdStat = f"UPDATE resources SET {resource}=(?) WHERE id=(?)" # statement for giving the user the resource bought
    db.execute(buyUpdStat, (newBuyerResource, cId)) # executes the statement

    db.execute("UPDATE offers SET amount=(?) WHERE offer_id=(?)", ((int(offer[1]) - int(amount_wanted)), offer_id))

    connection.commit() # commits the connection

    # lol this whole function is a fucking shitstorm ill comment it later hopefully

    return redirect("/market")

@login_required
@app.route("/provinces", methods=["GET", "POST"])
def provinces():
    if request.method == "GET":

        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        cId = session["user_id"]

        cityCount = db.execute("SELECT cityCount FROM provinces WHERE userId=(?)", (cId,)).fetchall()
        population = db.execute("SELECT population FROM provinces WHERE userId=(?)", (cId,)).fetchall()
        name = db.execute("SELECT provinceName FROM provinces WHERE userId=(?)", (cId,)).fetchall()
        pId = db.execute("SELECT provinceId FROM provinces WHERE userId=(?)", (cId,)).fetchall()

        pAll = zip(cityCount, population, name, pId)

        bAll = zip(cityCount, population, name, pId)

        return render_template("provinces.html", pAll=pAll, bAll=bAll)

@login_required
@app.route("/province/<pId>", methods=["GET", "POST"])
def province(pId):
    if request.method == "GET":
        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        name = db.execute("SELECT provinceName FROM provinces WHERE provinceId=(?)", (pId,)).fetchone()[0]
        population = db.execute("SELECT population FROM provinces WHERE provinceId = (?)", (pId, )).fetchone()[0]
        cityCount = db.execute("SELECT cityCount FROM provinces WHERE provinceId=(?)", (pId,)).fetchone()[0]
        land = (db.execute("SELECT land FROM provinces WHERE provinceId=(?)", (pId,)).fetchone()[0])

        connection.commit()

        return render_template("province.html", pId=pId, population=population, name=name, cityCount=cityCount, land=land)

# rawCol (for easy finding using CTRL + F)
@login_required
@app.route("/coalition/<colId>", methods=["GET"])
def coalition(colId):
    if request.method == "GET":

        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()
        
        cId = session["user_id"]

        name = db.execute("SELECT name FROM colNames WHERE id=(?)", (colId,)).fetchone()[0]
        colType = db.execute("SELECT type FROM colNames WHERE id=(?)", (colId,)).fetchone()[0]
        members = db.execute("SELECT COUNT(userId) FROM coalitions WHERE colId=(?)", (colId,)).fetchone()[0]
        total_influence = get_coalition_influence(colId)
        average_influence = total_influence / members

        # names = db.execute("SELECT username FROM users WHERE id = (SELECT userId FROM coalitions WHERE colId=(?))", (session["user_id"], )).fetchall()

        leader = db.execute("SELECT leader FROM colNames WHERE id=(?)", (colId,)).fetchone()[0]

        treaties = db.execute("SELECT name FROM treaty_ids").fetchall()


        if leader == cId:
            userLeader = True
        else:
            userLeader = False

        requestMessages = db.execute("SELECT message FROM requests WHERE colId=(?)", (colId,)).fetchall()
        requestIds = db.execute("SELECT reqId FROM requests WHERE colId=(?)", (colId,)).fetchall()
        requestNames = db.execute("SELECT username FROM users WHERE id=(SELECT reqId FROM requests WHERE colId=(?))", (colId,)).fetchall()

        requests = zip(requestIds, requestNames, requestMessages)

        """def avgStat(unit):
            peopleUnit = db.execute("SELECT (?) FROM stats WHERE id = (SELECT userId FROM coalitions WHERE colId=(?))", (unit, colId,)).fetchall()
            totalUnit = []
            for i in peopleUnit:
                totalUnit.append(i[0])
            peopleUnit = sum(totalUnit)
            return peopleUnit

        gold = avgStat("gold")
        happiness = avgStat("happiness")
        population = avgStat("population")"""

        description = db.execute("SELECT description FROM colNames WHERE id=(?)", (colId,)).fetchone()[0]

        colType = db.execute("SELECT type FROM colNames WHERE id=(?)", (colId,)).fetchone()[0]

        try:
            userInCol= db.execute("SELECT userId FROM coalitions WHERE userId=(?)", (cId,)).fetchone()[0]
            userInCol = True
        except:
            userInCol = False

        try:
            userInCurCol= db.execute("SELECT userId FROM coalitions WHERE userId=(?) AND colId=(?)", (cId, colId)).fetchone()[0]
            userInCurCol = True
        except:
            userInCurCol = False

        return render_template("coalition.html", name=name, colId=colId, members=members,
        description=description, colType=colType, userInCol=userInCol, userLeader=userLeader,
        requests=requests, userInCurCol=userInCurCol, treaties=treaties, total_influence=total_influence,
        average_influence=average_influence)

@login_required
# estCol (this is so the function would be easier to find in code)
@app.route("/establish_coalition", methods=["GET", "POST"])
def establish_coalition():
    if request.method == "POST":
        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        try: 
            db.execute("SELECT userId FROM coalitions WHERE userId=(?)", (session["user_id"],)).fetchone()[0]
            return error(403, "You are already in a coalition")
        except:

            cType = request.form.get("type")
            name = request.form.get("name")
            desc = request.form.get("description")

            if len(str(name)) > 15:
                return error(500, "name too long! the coalition name needs to be under 15 characters")
                # TODO add a better error message that renders inside the establish_coalition page
            else:
                # TODO gives a key error, look into this
                db.execute("INSERT INTO colNames (name, leader, type, description) VALUES (?, ?, ?, ?)", (name, session["user_id"], cType, desc))
                colId = db.execute("SELECT id FROM colNames WHERE name = (?)", (name,)).fetchone()[0]
                db.execute("INSERT INTO coalitions (colId, userId) VALUES (?, ?)", (colId, session["user_id"],))

                connection.commit()
                return redirect(f"/coalition/{colId}")
    else:
        return render_template("establish_coalition.html")

"""@app.context_processor
def get_status(unit, table, userId):

    cId = session["user_id"]

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()

    try:
        statStat = f"SELECT {unit} FROM {table} WHERE {userId} = (?)"
        db.execute(statStat, (cId,))
        return True
    except:
        return False

    updStat = f"UPDATE {table} SET {units}=(?) WHERE id=(?)"
        db.execute(updStat,((int(currentUnits) + int(wantedUnits)), cId)) # fix weird table"""

@login_required
@app.route("/<way>/<typee>/<units>", methods=["POST"])
def sell_buy(way, typee, units):

    if request.method == "POST":
    
        cId = session["user_id"]

        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        allUnits = ["soldiers", "tanks", "artillery",
        "flying_fortresses", "fighter_jets", "apaches"
        "destroyers", "cruisers", "submarines",
        "spies", "icbms", "nukes",
        
        "cityCount", "land",
        "oil_burners", "hydro_dams", "nuclear_reactors", "solar_fields",
        ""] # all allowed units

        if units not in allUnits:
            return redirect("/no_such_unit")

        # update this so it works using the nations script
        if units == "soldiers": # maybe change this to a dictionary later on
            table = "ground"
            price = 50
        elif units == "tanks":
            table = "ground"
            price = 150
        elif units == "artillery":
            table = "ground"
            price = 300

        elif units == "flying_fortresses":
            table = "air"
            price = 500
        elif units == "fighter_jets":
            table = "air"
            price = 450
        elif units == "apaches":
            table = "air"
            price = 350

        elif units == "destroyers":
            table = "water"
            price = 500
        elif units == "cruisers":
            table = "water"
            price = 650
        elif units == "submarines":
            table = "water"
            price = 450
            
        elif units == "spies":
            table = "special"
            price = 500
        elif units == "icbms":
            table = "special"
            price = 750
        elif units == "nukes":
            table = "special"
            price = 1000

        elif units == "cityCount":
            table = "provinces"
            price = 500
        elif units == "land":
            table = "provinces"
            price = 250

        elif units == "oil_burners":
            table = "proInfra"
            price = 500
        elif units == "hydro_dams":
            table = "proInfra"
            price = 500
        elif units == "nuclear_reactors":
            table = "proInfra"
            price = 500
        elif units == "solar_fields":
            table = "proInfra"
            price = 500

        if typee == "normal": # if buying or selling from military

            gold = db.execute("SELECT gold FROM stats WHERE id=(?)", (cId,)).fetchone()[0]
            wantedUnits = request.form.get(units)
            curUnStat = f'SELECT {units} FROM {table} WHERE id=?'
            totalPrice = int(wantedUnits) * price
            currentUnits = db.execute(curUnStat,(cId,)).fetchone()[0]

            if way == "sell":

                if int(wantedUnits) > int(currentUnits): # checks if unit is legits
                    return redirect("/too_much_to_sell") # seems to work

                unitUpd = f"UPDATE {table} SET {units}=(?) WHERE id=(?)"
                db.execute(unitUpd,(int(currentUnits) - int(wantedUnits), cId))
                db.execute("UPDATE stats SET gold=(?) WHERE id=(?)", ((int(gold) + int(wantedUnits) * int(price)), cId,)) # clean

            elif way == "buy":

                if int(totalPrice) > int(gold): # checks if user wants to buy more units than he has gold
                    return redirect("/too_many_units")

                db.execute("UPDATE stats SET gold=(?) WHERE id=(?)", (int(gold)-int(totalPrice), cId,))

                updStat = f"UPDATE {table} SET {units}=(?) WHERE id=(?)"
                db.execute(updStat,((int(currentUnits) + int(wantedUnits)), cId)) # fix weird table

            else: 
                error(404, "Page not found")

            connection.commit()

            return redirect("/military")

        elif typee == "province": # if buying from province

            gold = db.execute("SELECT gold FROM stats WHERE id=(?)", (cId,)).fetchone()[0]
            wantedUnits = request.form.get(units)
            curUnStat = f'SELECT {units} FROM {table} WHERE userId=?'
            totalPrice = int(wantedUnits) * price
            currentUnits = db.execute(curUnStat,(cId,)).fetchone()[0]

            if int(totalPrice) > int(gold): # checks if user wants to buy more units than he has gold
                return redirect("/too_many_units")

            db.execute("UPDATE stats SET gold=(?) WHERE id=(?)", (int(gold)-int(totalPrice), cId,))

            updStat = f"UPDATE {table} SET {units}=(?) WHERE userId=(?)"
            db.execute(updStat,((int(currentUnits) + int(wantedUnits)), cId)) # fix weird table

            connection.commit()

        return redirect("/provinces")



@login_required
@app.route("/createprovince", methods=["GET", "POST"])
def createprovince():
    if request.method == "POST":
        
        cId = session["user_id"]

        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        pName = request.form.get("name")

        db.execute("INSERT INTO provinces (userId, provinceName) VALUES (?, ?)", (cId, pName))

        connection.commit()

        return redirect("/provinces")
    else:
        return render_template("createprovince.html")

@login_required
@app.route("/marketoffer", methods=["GET", "POST"])
def marketoffer():
    if request.method == "POST":

        cId = session["user_id"]

        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        resource = request.form.get("resource")
        amount = request.form.get("amount")
        price = request.form.get("price")
        price = request.form.get("total_Price")

        if amount.isnumeric() is False or price.isnumeric() is False:
            return error(400, "You can only type numeric values into /marketoffer ")

        if int(amount) < 1:
            return error(400, "Amount must be greater than 0")

        rStatement = f"SELECT {resource} FROM resources WHERE id=(?)" # possible sql injection posibility TODO: look into thi
        realAmount = db.execute(rStatement, (cId,)).fetchone()[0]  #TODO: fix this not working
        if int(amount) > int(realAmount):
            return error("400", "Selling amount is higher than actual amount You have.")

        db.execute("INSERT INTO offers (user_id, resource, amount, price, total_Price) VALUES (?, ?, ?, ?, ?)", (cId, resource, int(amount), int(price), """int(total_Price)"""))

        connection.commit()
        return redirect("/market")
    else:
        return render_template("marketoffer.html")

@login_required
@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "GET":
        
        cId = session["user_id"]

        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        name = db.execute("SELECT username FROM users WHERE id=(?)", (cId,)).fetchone()[0]

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
@app.route("/war", methods=["GET", "POST"])
def war():

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()
    cId = session["user_id"]

    if request.method == "GET": # maybe optimise this later with css anchors
        # ground
        tanks = db.execute("SELECT tanks FROM ground WHERE id=(?)", (cId,)).fetchone()[0]
        soldiers = db.execute("SELECT soldiers FROM ground WHERE id=(?)", (cId,)).fetchone()[0]
        artillery = db.execute("SELECT artillery FROM ground WHERE id=(?)", (cId,)).fetchone()[0]
        # air
        flying_fortresses = db.execute("SELECT flying_fortresses FROM air WHERE id=(?)", (cId,)).fetchone()[0]
        fighter_jets = db.execute("SELECT fighter_jets FROM air WHERE id=(?)", (cId,)).fetchone()[0]
        apaches = db.execute("SELECT apaches FROM air WHERE id=(?)", (cId,)).fetchone()[0]
        # water
        destroyers = db.execute("SELECT destroyers FROM water WHERE id=(?)", (cId,)).fetchone()[0]
        cruisers = db.execute("SELECT cruisers FROM water WHERE id=(?)", (cId,)).fetchone()[0]
        submarines = db.execute("SELECT submarines FROM water WHERE id=(?)", (cId,)).fetchone()[0]
        # special
        spies = db.execute("SELECT spies FROM special WHERE id=(?)", (cId,)).fetchone()[0]
        icbms = db.execute("SELECT ICBMs FROM special WHERE id=(?)", (cId,)).fetchone()[0]
        nukes = db.execute("SELECT nukes FROM special WHERE id=(?)", (cId,)).fetchone()[0]

        yourCountry = db.execute("SELECT username FROM users WHERE id=(?)", (cId,)).fetchone()[0]

        return render_template("war.html", tanks=tanks, soldiers=soldiers, artillery=artillery,
        flying_fortresses=flying_fortresses, fighter_jets=fighter_jets, apaches=apaches,
        destroyers=destroyers, cruisers=cruisers, submarines=submarines,
        spies=spies, icbms=icbms, nukes=nukes, cId=cId, yourCountry=yourCountry
        )

@login_required
@app.route("/countries", methods=["GET", "POST"])
def countries(): # TODO: fix shit ton of repeated code in function
    if request.method == "GET":

        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        users = db.execute("SELECT id FROM users ORDER BY id").fetchall()

        population = []
        ids = []
        names = []
        coalition_ids = []
        coalition_names = []
        dates = []
        influences = []

        for i in users:

            ids.append(i[0])

            indPop = db.execute("SELECT population FROM stats WHERE id=(?)", (str(i[0]),)).fetchone()[0]
            population.append(indPop)

            name = db.execute("SELECT username FROM users WHERE id=(?)", (str(i[0]),)).fetchone()[0]
            names.append(name)

            date = db.execute("SELECT date FROM users WHERE id=(?)", (str(i[0]),)).fetchone()[0]
            dates.append(date)

            influence = get_influence(str(i[0]))
            influences.append(influence)

            try:
                coalition_id = db.execute("SELECT colId FROM coalitions WHERE userId = (?)", (str(i[0]),)).fetchone()[0]
                coalition_ids.append(coalition_id)

                coalition_name = db.execute("SELECT name FROM colNames WHERE id = (?)", (coalition_id,)).fetchone()[0]
                coalition_names.append(coalition_name)
            except:
                coalition_ids.append("No Coalition")
                coalition_names.append("No Coalition")

        connection.commit()

        resultAll = zip(population, ids, names, coalition_ids, coalition_names, dates, influences)

        return render_template("countries.html", resultAll=resultAll)

    else: 

        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()
        
        search = request.form.get("search")

        users = db.execute("SELECT id FROM users WHERE username LIKE ? ORDER BY id", ('%'+search+'%',)).fetchall()

        population = []
        ids = []
        names = []
        coalition_ids = []
        coalition_names = []
        dates = []
        influences = []

        for i in users:

            ids.append(i[0])

            indPop = db.execute("SELECT population FROM stats WHERE id=(?)", (str(i[0]),)).fetchone()[0]
            population.append(indPop)

            name = db.execute("SELECT username FROM users WHERE id=(?)", (str(i[0]),)).fetchone()[0]
            names.append(name)

            date = db.execute("SELECT date FROM users WHERE id=(?)", (str(i[0]),)).fetchone()[0]
            dates.append(date)
                        
            influence = get_influence(str(i[0]))
            influences.append(influence)

            try:
                coalition_id = db.execute("SELECT colId FROM coalitions WHERE userId = (?)", (str(i[0]),)).fetchone()[0]
                coalition_ids.append(coalition_id)

                coalition_name = db.execute("SELECT name FROM colNames WHERE id = (?)", (coalition_id,)).fetchone()[0]
                coalition_names.append(coalition_name)
            except:
                coalition_ids.append("No Coalition")
                coalition_names.append("No Coalition")

        resultAll = zip(population, ids, names, coalition_ids, coalition_names, dates, influences)

        return render_template("countries.html", resultAll=resultAll)

@login_required
@app.route("/coalitions", methods=["GET", "POST"])
def coalitions():
    if request.method == "GET":
        
        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        coalitions = db.execute("SELECT id FROM colNames").fetchall()

        names = []
        ids = []
        members = []
        types = []
        influences = []

        for i in coalitions:

            ids.append(i[0])

            idd = str(i[0])

            colType = db.execute("SELECT type FROM colNames WHERE id=(?)", (idd,)).fetchone()[0]
            types.append(colType)

            colName = db.execute("SELECT name FROM colNames WHERE id=(?)", (idd,)).fetchone()[0]
            names.append(colName)

            colMembers = db.execute("SELECT count(userId) FROM coalitions WHERE colId=(?)", (idd,)).fetchone()[0]
            members.append(colMembers)

            influence = get_coalition_influence(idd)
            influences.append(influence)

        resultAll = zip(names, ids, members, types, influences)

        return render_template("coalitions.html", resultAll=resultAll)
    
    else:

        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()
        
        search = request.form.get("search")

        resultId = db.execute("SELECT id FROM colNames WHERE name LIKE (?)", ('%'+search+'%',)).fetchall()
        ids = []
        names = []
        members = []
        types = []
        influences = []

        for i in resultId:
            names.append(db.execute("SELECT name FROM colNames WHERE id=(?)", (i[0],)).fetchone()[0])
            ids.append(db.execute("SELECT id FROM colNames WHERE id=(?)", (i[0],)).fetchone()[0])
            members.append(db.execute("SELECT count(userId) FROM coalitions WHERE colId=(?)", (i[0],)).fetchone()[0])
            types.append(db.execute("SELECT type FROM colNames WHERE id=(?)", (i[0],)).fetchone()[0])
            influences.append(get_coalition_influence(i[0]))

        resultAll = zip(names, ids, members, types, influences)

        return render_template("coalitions.html", resultAll=resultAll)

@login_required
@app.route("/join/<colId>", methods=["POST"])
def join_col(colId):
    
    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()

    cId = session["user_id"]

    colType = db.execute("SELECT type FROM colNames WHERE id = (?)", (colId,)).fetchone()[0]

    if colType == "Open":

        db.execute("INSERT INTO coalitions (colId, userId) VALUES (?, ?)", (colId, cId))

        connection.commit()

    else:

        message = request.form.get("message")

        db.execute("INSERT INTO requests (colId, reqId, message ) VALUES (?, ?, ?)", (colId, cId, message))

        connection.commit()

    return redirect(f"/coalition/{colId}")

@login_required
@app.route("/leave/<colId>", methods=["POST"])
def leave_col(colId):
    
    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()

    cId = session["user_id"]

    leader = db.execute("SELECT leader FROM colNames WHERE id=(?)", (colId,)).fetchone()[0]

    if cId == leader:
        return error(400, "Can't leave coalition, you're the leader")

    db.execute("DELETE FROM coalitions WHERE userId=(?) AND colId=(?)", (cId, colId))

    connection.commit()

    return redirect("/coalitions")

@login_required
@app.route("/my_offers", methods=["GET"])
def my_offers():

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()

    cId = session["user_id"]

    offers = db.execute("SELECT resource, price, amount FROM offers WHERE user_id=(?)", (cId,)).fetchall()

    return render_template("my_offers.html", offers=offers)

@login_required
@app.route("/add/<uId>", methods=["POST"])
def adding(uId):

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()

    try:
        colId = db.execute("SELECT colId FROM requests WHERE reqId=(?)", (uId,)).fetchone()[0]
    except TypeError:
        return error(400, "User hasn't posted a request to join")

    cId = session["user_id"]

    leader = db.execute("SELECT leader FROM colNames WHERE id=(?)", (colId,)).fetchone()[0]

    if leader != cId:

        return error(400, "You are not the leader of the coalition")

    db.execute("DELETE FROM requests WHERE reqId=(?) AND colId=(?)", (uId, colId))
    db.execute("INSERT INTO coalitions (colId, userId) VALUES (?, ?)", (colId, uId))
    connection.commit()

    return redirect(f"/coalition/{ colId }")

@login_required
@app.route("/remove/<uId>", methods=["POST"])
def removing(uId):

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()

    try:
        colId = db.execute("SELECT colId FROM requests WHERE reqId=(?)", (uId,)).fetchone()[0]
    except TypeError:
        return error(400, "User hasn't posted a request to join this coalition.")

    cId = session["user_id"]

    leader = db.execute("SELECT leader FROM colNames WHERE id=(?)", (colId,)).fetchone()[0]

    if leader != cId:

        return error(400, "You are not the leader of the coalition")

    db.execute("DELETE FROM requests WHERE reqId=(?) AND colId=(?)", (uId, colId))
    connection.commit()

    return redirect(f"/coalition/{ colId }")

@app.route("/logout", methods=["GET"])
def logout():
    if request.method == "GET":
        if 'user_id' in session:
            session.pop('user_id', None)
        else:
            return error(400, "You are not logged in")
        return redirect("/login")

@app.route("/tutorial", methods=["GET"])
def tutorial():
    return render_template("tutorial.html")

@app.route("/statistics", methods=["GET"])
def statistics():
    return render_template("statistics.html")

@login_required
@app.route("/update_country_info", methods=["POST"])
def update_info():

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()
    cId = session["user_id"]

    description = request.form.get("description")
    name = request.form.get("countryName")

    if len(description) > 1: # currently checks if the description is more than 1 letter cuz i was too lazy to figure out the input, bad practice but it works for now
        db.execute("UPDATE users SET description=(?) WHERE id=(?)", (description, cId))
        connection.commit()

    if len(name) > 1: # bad practice, but works for now, for more details check comment above

        try:
            duplicate = db.execute("SELECT id FROM users WHERE username=?", (name,)).fetchone()[0]
            duplicate = True
        except TypeError:
            duplicate = False

        if duplicate == False: # Checks if username isn't a duplicate
            db.execute("UPDATE users SET username=? WHERE id=?", (name, cId))
        connection.commit() # Commits the data

    return redirect(f"/country/id={cId}") # Redirects the user to his country

@login_required
@app.route("/update_discord", methods=["POST"])
def update_discord():

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()
    cId = session["user_id"]

    discord_username = request.form.get("discordUsername")
    db.execute("UPDATE users SET discord=(?) WHERE id=(?)", (discord_username, cId))
    connection.commit()
    return redirect(f"/country/id={cId}") # Redirects the user to his country
    
# available to run if double click the file
if __name__ == "__main__":
    app.run(debug=True) # Runs the app with debug mode on

