from flask import Flask, request, render_template, session, redirect, flash
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash
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

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        connection = sqlite3.connect('affo/aao.db')  # connects to db
        db = connection.cursor()  # creates the cursor for db connection

        # gets the password input from the form
        password = request.form.get("password").encode("utf-8")
        # gets the username input from the forms
        username = request.form.get("username")

        if not username or not password:  # checks if inputs are blank
            return error(400, "No Password or Username")

        # selects data about user, from users
        user = db.execute("SELECT * FROM users WHERE username = (?)", (username,)).fetchone()

        hashed_pw = user[4]

        # checks if user exists and if the password is correct
        if user is not None and bcrypt.checkpw(password, hashed_pw):
            # sets session's user_id to current user's id
            session["user_id"] = user[0]
            try:
                coalition = db.execute(
                    "SELECT colId FROM coalitions WHERE userId=(?)", (session["user_id"], )).fetchone()[0]
            except TypeError:
                coalition = error(404, "Page Not Found")

            # print(f"coalition = {coalition}")

            session["coalition"] = coalition
            print('User has succesfully logged in.')
            connection.commit()
            connection.close()
            return redirect("/")  # redirects user to homepage

        return error(403, "Wrong password")

    else:
        # renders login.html when "/login" is acessed via get
        return render_template("login.html")
