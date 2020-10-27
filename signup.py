# ALL MIGRATED

from flask import Flask, request, render_template, session, redirect, flash
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import generate_password_hash
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
import bcrypt
from requests_oauthlib import OAuth2Session
import os
from dotenv import load_dotenv
load_dotenv()

OAUTH2_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
OAUTH2_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
OAUTH2_REDIRECT_URI = 'http://localhost:5000/callback'

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

    discord_auth = f"discord:{discord_user_id}"

    try:
        db.execute("SELECT * FROM users WHERE hash=(%s)", (discord_auth,))
        duplicate = db.fetchone()[0]
        duplicate = True
    except TypeError:
        duplicate = False

    if duplicate == True:
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
        continent = request.form.get("continent")
        key = request.form.get("key")

        try:
            db.execute("SELECT key FROM keys WHERE key=(%s)", (key,))
            correct_key = db.fetchone()[0]
            correct_key = True
        except TypeError:
            correct_key = False
            return error(400, "Key not found")

        if correct_key != False:

            discord_user = discord.get(API_BASE_URL + '/users/@me').json()

            discord_user_id = discord_user['id']
            email = discord_user['email']

            discord_auth = f"discord:{discord_user_id}"

            try:
                db.execute("SELECT username FROM users WHERE username=(%s)", (username,))
                duplicate_name = db.fetchone()[0]
                duplicate_name = True
            except TypeError:
                duplicate_name = False
            
            if duplicate_name == True:
                return error(400, "Duplicate name, choose another one")

            date = str(datetime.date.today())

            db.execute("INSERT INTO users (username, email, hash, date) VALUES (%s, %s, %s, %s)", (username, email, discord_auth, date))

            db.execute("DELETE FROM keys WHERE key=(%s)", (key,))  # deletes the used key

            db.execute("SELECT id FROM users WHERE hash=(%s)", (discord_auth,))
            user_id = db.fetchone()[0]

            session["user_id"] = user_id

            user = user_id
            
            db.execute("INSERT INTO stats (id, location) VALUES (%s, %s)", (user, continent))  # TODO  change the default location
            db.execute("INSERT INTO military (id) VALUES (%s)", (user,))
            db.execute("INSERT INTO resources (id) VALUES (%s)", (user,))
            db.execute("INSERT INTO upgrades (user_id) VALUES (%s)", (user,))

            # clears session variables from oauth
            try:
                session.pop('oauth2_state')
            except KeyError:
                pass
            
            session.pop('oauth2_token')

            connection.commit()
            connection.close()
            return redirect("/")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":

        # connects the db to the signup function
        
        connection = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"))
  # connects to db
        db = connection.cursor()

        # gets corresponding form inputs
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password").encode('utf-8')
        confirmation = request.form.get("confirmation").encode('utf-8')

        # Selected continent by user
        continent = request.form.get("continent")

        key = request.form.get("key")

        try:
            db.execute("SELECT key FROM keys WHERE key=(%s)", (key))
            correct_key = db.fetchone()[0]
        except TypeError:
            correct_key = None
            return error(400, "Key not found")

        try:
            db.execute("SELECT username FROM users WHERE username=(%s)", (username,))
            duplicate_name = db.fetchone()[0]
            duplicate_name = True
        except TypeError:
            duplicate_name = False

        if duplicate_name == True:
                return error(400, "Duplicate name, choose another one")

        if password != confirmation:  # checks if password is = to confirmation password
            return error(400, "Passwords must match.")

        if correct_key != None and duplicate_name != True:
            # Hashes the inputted password
            hashed = bcrypt.hashpw(password, bcrypt.gensalt(14))

            db.execute("INSERT INTO users (username, email, hash, date) VALUES (%s, %s, %s, %s)", (username, email, hashed, str(datetime.date.today())))  # creates a new user || added account creation date

            duplicate_name = db.fetchone()[0]

            db.execute("SELECT id FROM users WHERE username = (%s)", (username,))
            user = db.fetchone()[0]

            # set's the user's "id" column to the sessions variable "user_id"
            session["user_id"] = user

            db.execute("INSERT INTO stats (id, location) VALUES (%s, %s)", (user, continent)) 
            db.execute("INSERT INTO military (id) VALUES (%s)", (user,))
            db.execute("INSERT INTO resources (id) VALUES (%s)", (user,))
            db.execute("INSERT INTO upgrades (user_id) VALUES (%s)", (user,))

            db.execute("DELETE FROM keys WHERE key=(%s)", (key,))  # deletes the used key

            connection.commit()
            connection.close()
            return redirect("/")
    else:
        return render_template("signup.html")
