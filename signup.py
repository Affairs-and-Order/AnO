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

            db.execute("INSERT INTO stats (id, location) VALUES (?, ?)", (user, continent))  # TODO  change the default location

            db.execute("INSERT INTO military (id) VALUES (?)",
                        (user,))
            db.execute("INSERT INTO resources (id) VALUES (?)",
                        (user,))

            db.execute("INSERT INTO upgrades (user_id) VALUES (?)", (user,))

            db.execute("DELETE FROM keys WHERE key=(?)", (key,))  # deletes the used key
            connection.commit()
            connection.close()
            return redirect("/")
    else:
        return render_template("signup.html")
