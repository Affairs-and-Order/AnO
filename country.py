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

@login_required
@app.route("/country/id=<cId>")
def country(cId):
    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()

    username = db.execute("SELECT username FROM users WHERE id=(?)", (cId,)).fetchone()[
        0]  # gets country's name from db
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
    except:
        colId = ""
        colName = ""

    connection.close()

    return render_template("country.html", username=username, cId=cId, description=description,
                           happiness=happiness, population=population, location=location, gold=gold, status=status,
                           provinceCount=provinceCount, colName=colName, dateCreated=dateCreated, influence=influence,
                           provinces=provinces, colId=colId)
