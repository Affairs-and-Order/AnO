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
import sqlite3
# from celery.schedules import crontab # arent currently using but will be later on
from helpers import get_influence, get_coalition_influence
# Game.ping() # temporarily removed this line because it might make celery not work
from app import app
import bcrypt
from requests_oauthlib import OAuth2Session
import os

OAUTH2_CLIENT_ID = '712251542425567309'
OAUTH2_CLIENT_SECRET = 'tbnBXz3CNZ3WsrA14xrBEJIs3eQUc75q'
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

@app.route('/discord')
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

    connection = sqlite3.connect('database.db')
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
        duplicate = db.execute("SELECT * FROM users WHERE hash=(?)", (discord_auth,)).fetchone()[0]
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

        connection = sqlite3.connect('database.db')
        db = connection.cursor()

        discord = make_session(token=session.get('oauth2_token'))
        
        username = request.form.get("username")


        discord_user = discord.get(API_BASE_URL + '/users/@me').json()
        discord_user_id = discord_user['id']
        email = discord_user['email']

        discord_auth = f"discord:{discord_user_id}"

        try:
            duplicate = db.execute("SELECT * FROM users WHERE hash=(?)", (discord_auth,)).fetchone()[0]
            duplicate = True
        except TypeError:
            duplicate = False

        if duplicate == True:
            return redirect("/error")
        
        db.execute("INSERT INTO users (username, email, hash) VALUES (?, ?, ?)", (username, email, discord_auth))
        db.execute("INSERT INTO stats (id, location) VALUES (?, ?)", (user, continent))  # TODO  change the default location

        db.execute("INSERT INTO military (id) VALUES (?)",
                    (user,))
        db.execute("INSERT INTO resources (id) VALUES (?)",
                    (user,))

        db.execute("INSERT INTO upgrades (user_id) VALUES (?)", (user,))

        db.execute("DELETE FROM keys WHERE key=(?)", (key,))  # deletes the used key
        user_id = db.execute("SELECT id FROM users WHERE hash=(?)", (discord_auth,)).fetchone()[0]

        session["user_id"] = user_id

        # clears session variables from oauth
        
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
        connection = sqlite3.connect('affo/aao.db')  # connects to db
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
            correct_key = db.execute("SELECT key FROM keys WHERE key=(?)", (key)).fetchone()[0]
        except TypeError:
            correct_key = None
            return error(400, "Key not found")

        if password != confirmation:  # checks if password is = to confirmation password
            return error(400, "Passwords must match.")

        if correct_key != None:
            # Hashes the inputted password
            hashed = bcrypt.hashpw(password, bcrypt.gensalt(14))

            db.execute("INSERT INTO users (username, email, hash, date) VALUES (?, ?, ?, ?)", (username, email, hashed, str(
                datetime.date.today())))  # creates a new user || added account creation date

            user = db.execute("SELECT id FROM users WHERE username = (?)", (username,)).fetchone()[0]

            # set's the user's "id" column to the sessions variable "user_id"
            session["user_id"] = user

            db.execute("INSERT INTO stats (id, location) VALUES (?, ?)", (user, continent)) 
            db.execute("INSERT INTO military (id) VALUES (?)", (user,))
            db.execute("INSERT INTO resources (id) VALUES (?)", (user,))

            db.execute("INSERT INTO upgrades (user_id) VALUES (?)", (user,))

            db.execute("DELETE FROM keys WHERE key=(?)", (key,))  # deletes the used key
            connection.commit()
            connection.close()
            return redirect("/")
    else:
        return render_template("signup.html")
