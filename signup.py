# FULLY MIGRATED

from flask import request, render_template, session, redirect
import datetime
from helpers import error
import psycopg2
# Game.ping() # temporarily removed this line because it might make celery not work
from app import app
import bcrypt
from requests_oauthlib import OAuth2Session
import os
from dotenv import load_dotenv
import requests
load_dotenv()

OAUTH2_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
OAUTH2_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")

try:
    environment = os.getenv("ENVIRONMENT")
except:
    environment = "DEV"

if environment == "PROD":
    OAUTH2_REDIRECT_URI = 'https://www.affairsandorder.com/callback'
else:
    OAUTH2_REDIRECT_URI = 'http://127.0.0.1:5000/callback'

API_BASE_URL = os.environ.get('API_BASE_URL', 'https://discordapp.com/api')
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'

app.config['SECRET_KEY'] = OAUTH2_CLIENT_SECRET

if 'http://' in OAUTH2_REDIRECT_URI:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'

def token_updater(token):
    session['oauth2_token'] = token

def make_session(token=None, state=None, scope=None):
    return OAuth2Session(
        client_id=OAUTH2_CLIENT_ID,
        token=token,
        state=state,
        scope=scope,
        redirect_uri=OAUTH2_REDIRECT_URI,
        auto_refresh_kwargs={
            'client_id': OAUTH2_CLIENT_ID,
            'client_secret': OAUTH2_CLIENT_SECRET,
        },
        auto_refresh_url=TOKEN_URL,
        token_updater=token_updater)

@app.route('/discord', methods=["GET", "POST"])
def discord():

    scope = request.args.get(
        'scope',
        'identify email')

    discord = make_session(scope=scope.split(' '))
    authorization_url, state = discord.authorization_url(AUTHORIZATION_BASE_URL)
    session['oauth2_state'] = state

    return redirect(authorization_url) # oauth2/authorize

@app.route('/callback')
def callback():

    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    if request.values.get('error'):
        return request.values['error']

    discord_state = make_session(state=session.get('oauth2_state'))
    token = discord_state.fetch_token(
        TOKEN_URL,
        client_secret=OAUTH2_CLIENT_SECRET,
        authorization_response=request.url)
    session['oauth2_token'] = token

    discord = make_session(token=token)
    discord_user_id = discord.get(API_BASE_URL + '/users/@me').json()['id']

    discord_auth = discord_user_id

    try:
        db.execute("SELECT * FROM users WHERE hash=(%s) AND auth_type='discord'", (discord_auth,))
        duplicate = db.fetchone()[0]
        duplicate = True
    except TypeError:
        duplicate = False

    if duplicate:
        return redirect("/discord_login")
    else:
        return redirect("/discord_signup")

@app.route('/discord_signup', methods=["GET", "POST"])
def discord_register():
    if request.method == "GET":

        return render_template('signup.html', way="discord")

    elif request.method == "POST":

        connection = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"))

        db = connection.cursor()

        discord = make_session(token=session.get('oauth2_token'))

        username = request.form.get("username")
        key = request.form.get("key")

        try:
            db.execute("SELECT key FROM keys WHERE key=(%s)", (key,))
            correct_key = db.fetchone()[0]
            correct_key = True
        except TypeError:
            correct_key = False
            return error(400, "Key not found")

        # Turns the continent number into 0-indexed
        continent_number = int(request.form.get("continent")) - 1
        # Ordered list, DO NOT EDIT
        continents = ["Tundra", "Savanna", "Desert", "Jungle", "Boreal Forest", "Grassland", "Mountain Range"]
        continent = continents[continent_number]

        if correct_key:

            discord_user = discord.get(API_BASE_URL + '/users/@me').json()

            discord_user_id = discord_user['id']
            email = discord_user['email']

            discord_auth = discord_user_id

            try:
                db.execute("SELECT username FROM users WHERE username=(%s)", (username,))
                duplicate_name = db.fetchone()[0]
                duplicate_name = True
            except TypeError:
                duplicate_name = False

            if duplicate_name:
                return error(400, "Duplicate name, choose another one")

            date = str(datetime.date.today())

            db.execute("INSERT INTO users (username, email, hash, date, auth_type) VALUES (%s, %s, %s, %s, %s)", (username, email, discord_auth, date, "discord"))

            db.execute("DELETE FROM keys WHERE key=(%s)", (key,))  # deletes the used key

            db.execute("SELECT id FROM users WHERE hash=(%s)", (discord_auth,))
            user_id = db.fetchone()[0]

            session["user_id"] = user_id

            db.execute("INSERT INTO stats (id, location) VALUES (%s, %s)", (user_id, continent))  # TODO Change the default location
            db.execute("INSERT INTO military (id) VALUES (%s)", (user_id,))
            db.execute("INSERT INTO resources (id) VALUES (%s)", (user_id,))
            db.execute("INSERT INTO upgrades (user_id) VALUES (%s)", (user_id,))

            # Clears session variables from oauth
            try:
                session.pop('oauth2_state')
            except KeyError:
                pass

            session.pop('oauth2_token')

            connection.commit()
            connection.close()
            return redirect("/")

# Function for verifying that the captcha token is correct
def verify_captcha(response):

    form_data = {
        "secret": os.getenv("RECAPTCHA_SECRET"),
        "response": response,
    }
    r = requests.post("https://www.google.com/recaptcha/api/siteverify", data=form_data)
    r = r.json()

    return r["success"]

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":

        connection = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"))

        # Creates a cursor to the database
        db = connection.cursor()

        # Gets user's form inputs
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password").encode('utf-8')
        confirmation = request.form.get("confirmation").encode('utf-8')

        # Turns the continent number into 0-indexed
        continent_number = int(request.form.get("continent")) - 1
        # Ordered list, DO NOT EDIT
        continents = ["Tundra", "Savanna", "Desert", "Jungle", "Boreal Forest", "Grassland", "Mountain Range"]
        continent = continents[continent_number]

        key = request.form.get("key")
        try:
            db.execute("SELECT key FROM keys WHERE key=%s", (key,))
            db.fetchone()[0]
        except:
            return error(400, "Key not found")

        try:
            db.execute("SELECT username FROM users WHERE username=%s", (username,))
            db.fetchone()[0]
            return error(400, "Duplicate name, choose another one")
        except:
            pass
        
        # Checks if password is equal to the confirmation password
        if password != confirmation:  
            return error(400, "Passwords must match.")

        # Hashes the inputted password
        hashed = bcrypt.hashpw(password, bcrypt.gensalt(14)).decode("utf-8")

        # Inserts the user and his data to the main table for users
        db.execute("INSERT INTO users (username, email, hash, date, auth_type) VALUES (%s, %s, %s, %s, %s)", (username, email, hashed, str(datetime.date.today()), "normal"))  # creates a new user || added account creation date

        # Selects the id of the user that was just registered. (Because id is AUTOINCREMENT'ed)
        db.execute("SELECT id FROM users WHERE username = (%s)", (username,))
        user_id = db.fetchone()[0]

        # Stores the user's 
        session["user_id"] = user_id

        # Inserts the user's id into the needed database tables
        db.execute("INSERT INTO stats (id, location) VALUES (%s, %s)", (user_id, continent))
        db.execute("INSERT INTO military (id) VALUES (%s)", (user_id,))
        db.execute("INSERT INTO resources (id) VALUES (%s)", (user_id,))
        db.execute("INSERT INTO upgrades (user_id) VALUES (%s)", (user_id,))

        db.execute("DELETE FROM keys WHERE key=(%s)", (key,)) # Deletes the key used for signup

        connection.commit()
        connection.close()
        return redirect("/")
    elif request.method == "GET":
        return render_template("signup.html", way="normal")
