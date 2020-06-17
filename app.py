from flask import Flask, request, render_template, session, redirect
from flask_session import Session
from tempfile import mkdtemp
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from helpers import login_required, error
import NationsScript as Game
# from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import _pickle as pickle
import random

Game.ping()

# this is the war checker, it will update on going wars between nations
# runs once a day
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


def eventCheck():
    rng = random.randint(1, 100)
    events = {
    }
    if rng == 50:
        pass
    # will decide if natural disasters occure


# warChecker = BackgroundScheduler() # wont be using this <
# eventChecker = BackgroundScheduler()
# uncomment when war ping is finished
# warChecker.add_job()


# from celery import Celery
# from celery.schedules import crontab

app = Flask(__name__)

#basic cache configuration
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
# celery.conf.update(app.config)

"""@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Executes every minute
    sender.add_periodic_task(
        crontab(minute='*/1'),
        populationGrowth.s(),
    )"""

@app.route("/")
def index():
    try:
        connection = sqlite3.connect('affo/aao.db') # connects to db
        db = connection.cursor() # creates the cursor for db connection

        inColit = db.execute("SELECT colId FROM coalitions WHERE userId=(?)", (session["user_id"], )).fetchone()[0]
        # TODO: fix this because this might causes errors when user is not in a coalition
        inCol = f"/coalition/{inColit}"
        app.add_template_global(inCol, name='inCol')
    except:
        inCol = error(404, "Page Not Found")
        app.add_template_global(inCol, name='inCol')
    return render_template("index.html") # renders index.html when "/" is accesed

@app.route("/error")
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

        if user is not None and check_password_hash(user[3], password): # checks if user exists and if the password is correct
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
                db.execute("INSERT INTO users (username, email, hash, date) VALUES (?, ?, ?, ?)", (username, email, hashed, datetime.date.today())) # creates a new user || added account creation date
                user = db.execute("SELECT id FROM users WHERE username = (?)", (username,)).fetchone()
                connection.commit()
                session["user_id"] = user[0] # set's the user's "id" column to the sessions variable "user_id"
                session["logged_in"] = True
                db.execute("INSERT INTO stats (id) SELECT id FROM users WHERE id = (?)", (session["user_id"],)) # change the default location                                                                          # "Bosfront" to something else
                db.execute("INSERT INTO ground (id) SELECT id FROM users WHERE id = (?)", (session["user_id"],)) 
                db.execute("INSERT INTO air (id) SELECT id FROM users WHERE id = (?)", (session["user_id"],))
                db.execute("INSERT INTO water (id) SELECT id FROM users WHERE id = (?)", (session["user_id"],))
                db.execute("INSERT INTO special (id) SELECT id FROM users WHERE id = (?)", (session["user_id"],))
                db.execute("INSERT INTO resources (id) SELECT id FROM users WHERE id = (?)", (session["user_id"],))
                db.execute("DELETE FROM keys WHERE key=(?)", (key,))
                connection.commit()
                connection.close()
                return redirect("/")
    else:
        return render_template("signup.html")

# @celery.task()
# TODO: create a celery task so this task would do itself every midnight or so
def populationGrowth():
    conn = sqlite3.connect('affo/aao.db') # connects to db
    db = conn.cursor()
    pop = db.execute("SELECT population, id FROM stats").fetchall() # selects id, population from the stats table and gets all the results for it

    for row in pop: # iterates over every result in population
        user_id = row[1] # sets the user_id variable to the "id" result from the query
        curPop = row[0]  # sets the current population variable to the "population" result from the query
        newPop = curPop + (int(curPop/10)) # gets the current population value and adds the same value / 10 to it
        db.execute("UPDATE stats SET population=(?) WHERE id=(?)", (newPop, user_id,)) # updates the db with the new value for population
        conn.commit()

    pop = db.execute("SELECT population FROM stats").fetchall()[0] # selects the population
    return pop # returns population TODO: change it so it wouldn't return population, just update the stats

@login_required
@app.route("/country/id=<cId>")
def country(cId):
    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()
    username = db.execute("SELECT username FROM users WHERE id=(?)", (cId,)).fetchone()[0] # gets country's name from db
    connection.commit()

    population = db.execute("SELECT population FROM stats WHERE id=(?)", (cId,)).fetchone()[0]
    happiness = db.execute("SELECT happiness FROM stats WHERE id=(?)", (cId,)).fetchone()[0]
    provinces = db.execute("SELECT COUNT(*) FROM provinces WHERE userId=(?)", (cId,)).fetchone()[0]
    connection.commit()

    location = db.execute("SELECT location FROM stats WHERE id=(?)", (cId,)).fetchone()[0]
    gold = db.execute("SELECT gold FROM stats WHERE id=(?)", (cId,)).fetchone()[0]
    connection.commit()

    if cId == session["user_id"]:
        status = True
    else:
        status = False

    try:
        colName = db.execute("SELECT name FROM colNames WHERE id = (SELECT colId FROM coalitions WHERE userId=(?))", (cId,)).fetchone()[0]
    except:
        colName = ""

    return render_template("country.html", username=username, cId=cId, happiness=happiness, population=population,
    location=location, gold=gold, status=status, provinces=provinces, colName=colName)

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
        
        user_ids = db.execute("SELECT user_id FROM offers").fetchall()
        
        ids = []
        names = []
        resources = []
        amounts = []
        prices = []

        for i in user_ids:

            ids.append(i)
            
            name = db.execute("SELECT username FROM users WHERE id=(?)", (i[0],)).fetchone()[0]
            
            names.append(name)

            resource = db.execute("SELECT resource FROM offers WHERE user_id=(?)", (i[0],)).fetchone()[0]
            resources.append(resource)

            amount = db.execute("SELECT amount FROM offers WHERE user_id=(?)", (i[0],)).fetchone()[0]
            amounts.append(amount)

            price = db.execute("SELECT price FROM offers WHERE user_id=(?)", (i[0],)).fetchone()[0]
            prices.append(price)

        offers = zip(ids, names, resources, amounts, prices)



        

        return render_template("market.html", offers=offers)

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

        return render_template("provinces.html", pAll=pAll)

@login_required
@app.route("/province/<pId>", methods=["GET", "POST"])
def province(pId):
    if request.method == "GET":
        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        name = db.execute("SELECT provinceName FROM provinces WHERE provinceId=(?)", (pId,)).fetchone()[0]
        population = db.execute("SELECT population FROM provinces WHERE provinceId = (?)", (pId, )).fetchone()[0]
        cityCount = db.execute("SELECT cityCount FROM provinces WHERE provinceId=(?)", (pId,)).fetchone()[0]

        connection.commit()

        return render_template("province.html", pId=pId, population=population, name=name, cityCount=cityCount)

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

        # names = db.execute("SELECT username FROM users WHERE id = (SELECT userId FROM coalitions WHERE colId=(?))", (session["user_id"], )).fetchall()

        leader = db.execute("SELECT leader FROM colNames WHERE id=(?)", (colId,)).fetchone()[0]

        if leader == cId:
            userLeader = True
        else:
            userLeader = False

        members = db.execute("SELECT COUNT(userId) FROM coalitions WHERE colId=(?)", (colId,)).fetchone()[0]

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

        return render_template("coalition.html", name=name, colId=colId, members=members,
        description=description, colType=colType, userInCol=userInCol, userLeader=userLeader)

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
@app.route("/<way>/<units>", methods=["POST"])
def sell_buy(way, units):

    if request.method == "POST":
    
        cId = session["user_id"]

        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        allUnits = ["soldiers", "tanks", "artillery",
        "flying_fortresses", "fighter_jets", "apaches"
        "destroyers", "cruisers", "submarines",
        "spies", "icbms", "nukes"] # all allowed units

        if units not in allUnits:
            return redirect("/no_such_unit")

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

        if amount.isnumeric() is False or price.isnumeric() is False:
            return error(400, "You can only type numeric values into /marketoffer ")

        if int(amount) < 1:
            return error(400, "Amount must be greater than 0")

        rStatement = f"SELECT {resource} FROM resources WHERE id=(?)" # possible sql injection posibility TODO: look into thi
        realAmount = db.execute(rStatement, (cId,)).fetchone()[0]  #TODO: fix this not working
        if int(amount) > int(realAmount):
            return error("400", "Selling amount is higher than actual amount You have.")

        db.execute("INSERT INTO offers (user_id, resource, amount, price) VALUES (?, ?, ?, ?)", (cId, resource, int(amount), int(price)))

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

        return render_template("war.html", tanks=tanks, soldiers=soldiers, artillery=artillery,
        flying_fortresses=flying_fortresses, fighter_jets=fighter_jets, apaches=apaches,
        destroyers=destroyers, cruisers=cruisers, submarines=submarines,
        spies=spies, icbms=icbms, nukes=nukes
        )

@login_required
@app.route("/countries")
def countries():
    if request.method == "GET":

        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        users = db.execute("SELECT id FROM users ORDER BY id").fetchall()

        population = []
        ids = []
        names = []
        coalition_ids = []
        coalition_names = []

        for i in users:

            ids.append(i[0])

            indPop = db.execute("SELECT population FROM stats WHERE id=(?)", (str(i[0]),)).fetchone()[0]
            population.append(indPop)

            name = db.execute("SELECT username FROM users WHERE id=(?)", (str(i[0]),)).fetchone()[0]
            names.append(name)

            try:
                coalition_id = db.execute("SELECT colId FROM coalitions WHERE userId = (?)", (str(i[0]),)).fetchone()[0]
                coalition_ids.append(coalition_id)

                coalition_name = db.execute("SELECT name FROM colNames WHERE id = (?)", (coalition_id,)).fetchone()[0]
                coalition_names.append(coalition_name)
            except:
                coalition_ids.append("No Coalition")
                coalition_names.append("No Coalition")

        connection.commit()

        new_zipped = zip(population, ids, names, coalition_ids, coalition_names)

        return render_template("countries.html", new_zipped=new_zipped)

@login_required
@app.route("/coalitions", methods=["GET", "POST"])
def coalitions():
    if request.method == "GET":
        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        colIds = db.execute("SELECT id FROM colNames").fetchall()
        colNames = db.execute("SELECT name FROM colNames").fetchall()
        colTypes = db.execute("SELECT type FROM colNames").fetchall()

        colBoth = zip(colIds, colNames, colTypes)

        exRes = False

        return render_template("coalitions.html", colBoth=colBoth, exRes=exRes)
    
    else:

        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()
        
        search = request.form.get("search")

        resultName = db.execute("SELECT name FROM colNames WHERE name LIKE (?)", ('%'+search+'%',)).fetchall()
        resultId = db.execute("SELECT id FROM colNames WHERE name LIKE (?)", ('%'+search+'%',)).fetchall()

        resultAll = zip(resultName, resultId)
        exRes = True

        return render_template("coalitions.html", resultAll=resultAll, exRes=exRes)

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

# available to run if double click the file
if __name__ == "__main__":
    app.run(debug=True)

