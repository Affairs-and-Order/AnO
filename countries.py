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

@app.route("/country/id=<cId>")
@login_required
def country(cId):
    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()

    username = db.execute("SELECT username FROM users WHERE id=(?)", (cId,)).fetchone()[0]  # gets country's name from db
    # runs the get_influence function of the player's id, which calculates his influence score
    influence = get_influence(cId)
    description = db.execute("SELECT description FROM users WHERE id=(?)", (cId,)).fetchone()[0]

    population = db.execute("SELECT population FROM stats WHERE id=(?)", (cId,)).fetchone()[0]
    happiness = db.execute("SELECT happiness FROM stats WHERE id=(?)", (cId,)).fetchone()[0]
    provinceCount = db.execute("SELECT COUNT(*) FROM provinces WHERE userId=(?)", (cId,)).fetchone()[0]

    location = db.execute("SELECT location FROM stats WHERE id=(?)", (cId,)).fetchone()[0]
    gold = db.execute("SELECT gold FROM stats WHERE id=(?)", (cId,)).fetchone()[0]
    dateCreated = db.execute("SELECT date FROM users WHERE id=(?)", (cId,)).fetchone()[0]

    provinceNames = db.execute("SELECT provinceName FROM provinces WHERE userId=(?) ORDER BY id DESC", (cId,)).fetchall()
    provinceIds = db.execute("SELECT id FROM provinces WHERE userId=(?) ORDER BY id DESC", (cId,)).fetchall()
    provincePops = db.execute("SELECT population FROM provinces WHERE userId=(?) ORDER BY id DESC", (cId,)).fetchall()
    provinceCities = db.execute("SELECT cityCount FROM provinces WHERE userId=(?) ORDER BY id DESC", (cId,)).fetchall()
    provinceLand = db.execute("SELECT land FROM provinces WHERE userId=(?) ORDER BY id DESC", (cId,)).fetchall()

    provinces = zip(provinceNames, provinceIds, provincePops,
                    provinceCities, provinceLand)

    if str(cId) == str(session["user_id"]):
        status = True
    else:
        status = False

    try:
        colId = db.execute("SELECT colId FROM coalitions WHERE userId=(?)", (cId,)).fetchone()[0]
        colName = db.execute("SELECT name FROM colNames WHERE id =?", (colId,)).fetchone()[0]
    except TypeError:
        colId = ""
        colName = ""

    try:
        colFlag = db.execute("SELECT flag FROM colNames WHERE id=(?)", (colId,)).fetchone()[0]
    except TypeError:
        colFlag = None

    try:
        flag = db.execute("SELECT flag FROM users WHERE id=(?)", (cId,)).fetchone()[0]
    except TypeError:
        flag = None

    spyCount = db.execute("SELECT spies FROM military WHERE id=(?)", (cId,)).fetchone()[0]
    spyPrep = 1 # this is an integer from 1 to 5
    eSpyCount = 0 # this is an integer from 0 to 100
    eDefcon = 1 # this is an integer from 1 to 5

    if eSpyCount == 0:
        successChance = 100
    else:
        successChance = spyCount * spyPrep / eSpyCount / eDefcon
    connection.close()

    return render_template("country.html", username=username, cId=cId, description=description,
                           happiness=happiness, population=population, location=location, gold=gold, status=status,
                           provinceCount=provinceCount, colName=colName, dateCreated=dateCreated, influence=influence,
                           provinces=provinces, colId=colId, flag=flag, spyCount=spyCount, successChance=successChance,
                           colFlag=colFlag)


@app.route("/countries", methods=["GET"])
@login_required
def countries():  # TODO: fix shit ton of repeated code in function

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()

    try:
        search = request.values.get("search")
    except TypeError:
        search = None

    try:
        lowerinf = float(request.values.get("lowerinf"))
    except TypeError:
        lowerinf = None

    try:
        upperinf = float(request.values.get("upperinf"))
    except TypeError:
        upperinf = None


    # Unoptimize
    if search == None or search == "" and upperinf == None and lowerinf == None:
        users = db.execute("SELECT id FROM users ORDER BY id").fetchall()
    elif search != None and upperinf == None and lowerinf == None:
        users = db.execute("SELECT id FROM users WHERE username=(?) ORDER BY id", (search,)).fetchall()

    if lowerinf != None and upperinf == None:
        for user in users:
            user_id = int(user[0])
            if get_influence(user_id) < lowerinf:
                users.remove(user)

    elif upperinf != None and lowerinf == None:
        for user in users:
            user_id = int(user[0])
            if get_influence(user_id) > upperinf:
                users.remove(user)

    elif upperinf != None and lowerinf != None:
        for user in users:
            user_influence = get_influence(int(user[0]))
            if user_influence > upperinf or user_influence < lowerinf:
                users.remove(user)


    population = db.execute("SELECT population FROM stats ORDER BY id").fetchall()
    names = db.execute("SELECT username FROM users ORDER BY id").fetchall()

    coalition_ids = []
    coalition_names = []
    dates = []
    influences = []
    flags = []

    for i in users:

        date = db.execute("SELECT date FROM users WHERE id=(?)", (str(i[0]),)).fetchone()[0]
        dates.append(date)

        influence = get_influence(str(i[0]))
        influences.append(influence)

        try:
            flag = db.execute("SELECT flag FROM users WHERE id=(?)", (str(i[0]),)).fetchone()[0]
        except TypeError:
            flag = None

        flags.append(flag)

        try:
            coalition_id = db.execute("SELECT colId FROM coalitions WHERE userId = (?)", (str(i[0]),)).fetchone()[0]
            coalition_ids.append(coalition_id)

            coalition_name = db.execute("SELECT name FROM colNames WHERE id = (?)", (coalition_id,)).fetchone()[0]
            coalition_names.append(coalition_name)
        except:
            coalition_ids.append("No Coalition")
            coalition_names.append("No Coalition")

    connection.commit()
    connection.close()

    resultAll = zip(population, users, names, coalition_ids,
                    coalition_names, dates, influences, flags)

    return render_template("countries.html", resultAll=resultAll)



@app.route("/update_country_info", methods=["POST"])
@login_required
def update_info():

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()
    cId = session["user_id"]

    # Description changing
    description = request.form.get("description")

    if not description == "None":
        db.execute("UPDATE users SET description=(?) WHERE id=(?)", (description, cId))

    # Flag changing
    ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    file = request.files["flag_input"]
    if file and allowed_file(file.filename):

        # Check if the user already has a flag
        try:
            current_flag = db.execute("SELECT flag FROM users WHERE id=(?)", (cId,)).fetchone()[0]

            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], current_flag))
        except TypeError:
            pass

        # Save the file & shit
        current_filename = file.filename
        if allowed_file(current_filename):
            extension = current_filename.rsplit('.', 1)[1].lower()
            filename = f"flag_{cId}" + '.' + extension
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            db.execute("UPDATE users SET flag=(?) WHERE id=(?)", (filename, cId))

    # Location changing
    new_location = request.form.get("countryLocation")

    if not new_location == "":
        db.execute("UPDATE stats SET location=(?) WHERE id=(?)", (new_location, cId))

    connection.commit()  # Commits the data
    connection.close()  # Closes the connection

    return redirect(f"/country/id={cId}")  # Redirects the user to his country

@app.route("/delete_own_account", methods=["POST"])
@login_required
def delete_own_account():

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()
    cId = session["user_id"]

    # Deletes all the info from database created upon signup
    db.execute("DELETE FROM users WHERE id=(?)", (cId,))
    db.execute("DELETE FROM stats WHERE id=(?)", (cId,))
    db.execute("DELETE FROM military WHERE id=(?)", (cId,))
    db.execute("DELETE FROM resources WHERE id=(?)", (cId,))

    # Deletes all market things the user is associateed with
    db.execute("DELETE FROM offers WHERE user_id=(?)", (cId,))
    # Deletes all the users provinces and their infrastructure
    try:
        province_ids = db.execute("SELECT id FROM provinces WHERE userId=(?)", (cId,)).fetchall()
        for i in province_ids:
            db.execute("DELETE FROM provinces WHERE id=(?)", (i[0],))
            db.execute("DELETE FROM proInfra WHERE id=(?)", (i[0],))
    except:
        pass

    connection.commit()
    connection.close()

    session.clear()

    return redirect("/")

@app.route("/username_available/<username>", methods=["GET"])
def username_avalaible(username):
    conn = sqlite3.connect('affo/aao.db') # connects to db
    db = conn.cursor()

    try:
        username_exists = db.execute("SELECT username FROM users WHERE username=(?)", (username,)).fetchone()[0]
        username_exists = True
    except TypeError:
        username_exists = False

    if username_exists == True:
        return "No"
    else:
        return "Yes"
