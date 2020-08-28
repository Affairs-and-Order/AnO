from flask import Flask, request, render_template, session, redirect, flash
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import generate_password_hash, check_password_hash
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
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/flags'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@login_required
@app.route("/country/id=<cId>")
def country(cId):
    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()

    username = db.execute("SELECT username FROM users WHERE id=(?)", (cId,)).fetchone()[0]  # gets country's name from db
    # runs the get_influence function of the player's id, which calculates his influence score
    influence = get_influence(cId)
    description = db.execute(
        "SELECT description FROM users WHERE id=(?)", (cId,)).fetchone()[0]

    population = db.execute(
        "SELECT population FROM stats WHERE id=(?)", (cId,)).fetchone()[0]
    happiness = db.execute(
        "SELECT happiness FROM stats WHERE id=(?)", (cId,)).fetchone()[0]
    provinceCount = db.execute(
        "SELECT COUNT(*) FROM provinces WHERE userId=(?)", (cId,)).fetchone()[0]

    location = db.execute(
        "SELECT location FROM stats WHERE id=(?)", (cId,)).fetchone()[0]
    gold = db.execute("SELECT gold FROM stats WHERE id=(?)",
                      (cId,)).fetchone()[0]
    dateCreated = db.execute(
        "SELECT date FROM users WHERE id=(?)", (cId,)).fetchone()[0]

    provinceNames = db.execute(
        "SELECT provinceName FROM provinces WHERE userId=(?) ORDER BY id DESC", (cId,)).fetchall()
    provinceIds = db.execute(
        "SELECT id FROM provinces WHERE userId=(?) ORDER BY id DESC", (cId,)).fetchall()
    provincePops = db.execute(
        "SELECT population FROM provinces WHERE userId=(?) ORDER BY id DESC", (cId,)).fetchall()
    provinceCities = db.execute(
        "SELECT cityCount FROM provinces WHERE userId=(?) ORDER BY id DESC", (cId,)).fetchall()
    provinceLand = db.execute(
        "SELECT land FROM provinces WHERE userId=(?) ORDER BY id DESC", (cId,)).fetchall()

    provinces = zip(provinceNames, provinceIds, provincePops,
                    provinceCities, provinceLand)

    if str(cId) == str(session["user_id"]):
        status = True
    else:
        status = False

    try:
        colId = db.execute(
            "SELECT colId FROM coalitions WHERE userId=(?)", (cId,)).fetchone()[0]
        colName = db.execute(
            "SELECT name FROM colNames WHERE id =?", (colId,)).fetchone()[0]
    except TypeError:
        colId = ""
        colName = ""

    try:
        flag = db.execute("SELECT flag FROM users WHERE id=(?)", (cId,)).fetchone()[0]
    except TypeError:
        flag = None

    connection.close()

    return render_template("country.html", username=username, cId=cId, description=description,
                           happiness=happiness, population=population, location=location, gold=gold, status=status,
                           provinceCount=provinceCount, colName=colName, dateCreated=dateCreated, influence=influence,
                           provinces=provinces, colId=colId, flag=flag)


@login_required
@app.route("/countries", methods=["GET", "POST"])
def countries():  # TODO: fix shit ton of repeated code in function
    if request.method == "GET":

        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        users = db.execute("SELECT id FROM users ORDER BY id").fetchall()
        population = db.execute(
            "SELECT population FROM stats ORDER BY id").fetchall()
        names = db.execute("SELECT username FROM users ORDER BY id").fetchall()

        coalition_ids = []
        coalition_names = []
        dates = []
        influences = []

        for i in users:

            date = db.execute(
                "SELECT date FROM users WHERE id=(?)", (str(i[0]),)).fetchone()[0]
            dates.append(date)

            influence = get_influence(str(i[0]))
            influences.append(influence)

            try:
                coalition_id = db.execute(
                    "SELECT colId FROM coalitions WHERE userId = (?)", (str(i[0]),)).fetchone()[0]
                coalition_ids.append(coalition_id)

                coalition_name = db.execute(
                    "SELECT name FROM colNames WHERE id = (?)", (coalition_id,)).fetchone()[0]
                coalition_names.append(coalition_name)
            except:
                coalition_ids.append("No Coalition")
                coalition_names.append("No Coalition")

        connection.commit()
        connection.close()

        resultAll = zip(population, users, names, coalition_ids,
                        coalition_names, dates, influences)

        return render_template("countries.html", resultAll=resultAll)

    else:

        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        search = request.form.get("search")

        users = db.execute(
            "SELECT id FROM users WHERE username LIKE ? ORDER BY id", ('%'+search+'%',)).fetchall()

        population = []
        ids = []
        names = []
        coalition_ids = []
        coalition_names = []
        dates = []
        influences = []

        for i in users:

            ids.append(i[0])

            indPop = db.execute(
                "SELECT population FROM stats WHERE id=(?)", (str(i[0]),)).fetchone()[0]
            population.append(indPop)

            name = db.execute(
                "SELECT username FROM users WHERE id=(?)", (str(i[0]),)).fetchone()[0]
            names.append(name)

            date = db.execute(
                "SELECT date FROM users WHERE id=(?)", (str(i[0]),)).fetchone()[0]
            dates.append(date)

            influence = get_influence(str(i[0]))
            influences.append(influence)

            try:
                coalition_id = db.execute(
                    "SELECT colId FROM coalitions WHERE userId = (?)", (str(i[0]),)).fetchone()[0]
                coalition_ids.append(coalition_id)

                coalition_name = db.execute(
                    "SELECT name FROM colNames WHERE id = (?)", (coalition_id,)).fetchone()[0]
                coalition_names.append(coalition_name)
            except:
                coalition_ids.append("No Coalition")
                coalition_names.append("No Coalition")

        connection.close()

        resultAll = zip(population, ids, names, coalition_ids,
                        coalition_names, dates, influences)

        return render_template("countries.html", resultAll=resultAll)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@login_required
@app.route("/update_country_info", methods=["POST"])
def update_info():

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()
    cId = session["user_id"]

    description = request.form.get("description")
    name = request.form.get("countryName")

    if len(description) > 1:  # currently checks if the description is more than 1 letter cuz i was too lazy to figure out the input, bad practice but it works for now
        db.execute("UPDATE users SET description=(?) WHERE id=(?)",
                   (description, cId))
        connection.commit()

    if len(name) > 1:  # bad practice, but works for now, for more details check comment above

        try:
            duplicate = db.execute(
                "SELECT id FROM users WHERE username=?", (name,)).fetchone()[0]
            duplicate = True
        except TypeError:
            duplicate = False

        if duplicate == False:  # Checks if username isn't a duplicate
            # Updates the username to the new one
            db.execute("UPDATE users SET username=? WHERE id=?", (name, cId))

    #TODO: add some checking for malicious extensions n shit
    file = request.files["flag_input"]
    if file and allowed_file(file.filename):
        current_filename = file.filename
        extension = current_filename.rsplit('.', 1)[1].lower()
        filename = f"flag_{cId}" + '.' + extension
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        db.execute("UPDATE users SET flag=(?) WHERE id=(?)", (filename, cId))
        
    connection.commit()  # Commits the data
    connection.close()  # Closes the connection

    return redirect(f"/country/id={cId}")  # Redirects the user to his country
