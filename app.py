from flask import Flask, request, render_template, session, redirect
from flask_session import Session
from tempfile import mkdtemp
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from helpers import login_required
from flask_mail import Mail, Message
# from celery import Celery
# from celery.schedules import crontab

app = Flask(__name__)

app.config["MAIL_SERVER"] = None # replace this with the domain of the email
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True

# app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
# app.config['result_backend'] = 'redis://localhost:6379/0'

# celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
# celery.conf.update(app.config)

"""@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Executes every minute
    sender.add_periodic_task(
        crontab(minute='*/1'),
        populationGrowth.s(),
    )"""

mail = Mail(app)

# code for sending custom email messages to users
def sendEmail(title, content, user):

    conn = sqlite3.connect('affo/aao.db')

    msg = Message(title)
    msg.add_recipient("somebodyelse@example.com")
    msg.html = content
    mail.send(msg)


# basic cache configuration
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def index():
    return render_template("index.html") # renders index.html when "/" is accesed

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        connection = sqlite3.connect('affo/aao.db') # connects to db
        db = connection.cursor() # creates the cursor for db connection

        password = request.form.get("password") # gets the password input from the form
        username = request.form.get("username") # gets the username input from the forms

        if not username or not password: # checks if inputs are blank
            return redirect("/error_no_pw_or_un") #TODO change to actual error
        user = db.execute("SELECT * FROM users WHERE username = (?)", (username,)).fetchone() # selects data about user, from users
        connection.commit()

        if user is not None and check_password_hash(user[3], password): # checks if user exists and if the password is correct
            session["user_id"] = user[0] # sets session's user_id to current user's id
            session["logged_in"] = True
            print('User has succesfully logged in.')
            connection.commit()
            connection.close()
            return redirect("/") # redirects user to homepage
        return redirect("/error_wrong_pw")

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
        connection.commit()
        if not confirmation or not password or not email or not username: # checks for blank inputs
            return redirect("/error_blank") #TODO change to actual error
        elif password != confirmation: # checks if password is = to confirmation password
            return redirect("/error_wrong_cn") #TODO change to actual error
        else:
            hashed = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16) # hashes the inputted password
            db.execute("INSERT INTO users (username, email, hash) VALUES (?, ?, ?)", (username, email, hashed,)) # creates a new user
            user = db.execute("SELECT id FROM users WHERE username = (?)", (username,)).fetchone()
            connection.commit()
            session["user_id"] = user[0] # set's the user's "id" column to the sessions variable "user_id"
            session["logged_in"] = True
            db.execute("INSERT INTO stats (id) SELECT id FROM users WHERE id = (?)", (session["user_id"],)) # change the default location
            connection.commit()                                                                             # "Bosfront" to something else
            db.execute("INSERT INTO ground (id) SELECT id FROM users WHERE id = (?)", (session["user_id"],)) 
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
    connection.commit()
    location = db.execute("SELECT location FROM stats WHERE id=(?)", (cId,)).fetchone()[0]
    gold = db.execute("SELECT gold FROM stats WHERE id=(?)", (cId,)).fetchone()[0]
    try: # sees if user is logged in
        uId = True 
        return render_template("country.html", username=username, cId=cId, happiness=happiness, population=population,
        location=location, gold=gold, uId=uId)
    except KeyError: # if user isnt logged in
        uId = False
        return render_template("country.html", uId=uId)

@login_required
@app.route("/military", methods=["GET", "POST"])
def military():
    if request.method == "GET":
        return render_template("military.html")

@login_required
@app.route("/market", methods=["GET", "POST"])
def market():
    if request.method == "GET":
        return render_template("market.html")

@login_required
@app.route("/coalition", methods=["GET", "POST"])
def coalition():
    if request.method == "GET":
        return render_template("coalition.html")

@login_required
@app.route("/establishcoalition", methods=["GET", "POST"])
def establishcoalition():
    if request.method == "GET":
        return render_template("establishcoalition.html")

@login_required
@app.route("/countries", methods=["GET", "POST"])
def countries():
    if request.method == "GET":
        return render_template("countries.html")

@login_required
@app.route("/coalitions", methods=["GET", "POST"])
def coalitions():
    if request.method == "GET":
        return render_template("coalitions.html")

# available to run if double click the file
if __name__ == "__main__":
    app.run(debug=True)

