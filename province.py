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
@app.route("/provinces", methods=["GET", "POST"])
def provinces():
    if request.method == "GET":

        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        cId = session["user_id"]

        cityCount = db.execute(
            "SELECT cityCount FROM provinces WHERE userId=(?) ORDER BY id ASC", (cId,)).fetchall()
        population = db.execute(
            "SELECT population FROM provinces WHERE userId=(?) ORDER BY id ASC", (cId,)).fetchall()
        name = db.execute(
            "SELECT provinceName FROM provinces WHERE userId=(?) ORDER BY id ASC", (cId,)).fetchall()
        pId = db.execute(
            "SELECT id FROM provinces WHERE userId=(?) ORDER BY id ASC", (cId,)).fetchall()
        land = db.execute(
            "SELECT land FROM provinces WHERE userId=(?) ORDER BY id ASC", (cId,)).fetchall()

        connection.close()

        # zips the above SELECT statements into one list.
        pAll = zip(cityCount, population, name, pId, land)

        return render_template("provinces.html", pAll=pAll)


@login_required
@app.route("/province/<pId>", methods=["GET", "POST"])
def province(pId):
    if request.method == "GET":
        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        name = db.execute(
            "SELECT provinceName FROM provinces WHERE id=(?)", (pId,)).fetchone()[0]
        population = db.execute(
            "SELECT population FROM provinces WHERE id=(?)", (pId,)).fetchone()[0]
        pollution = db.execute(
            "SELECT pollution FROM provinces WHERE id=(?)", (pId,)).fetchone()[0]

        cityCount = db.execute(
            "SELECT cityCount FROM provinces WHERE id=(?)", (pId,)).fetchone()[0]
        land = db.execute(
            "SELECT land FROM provinces WHERE id=(?)", (pId,)).fetchone()[0]

        oil_burners = db.execute(
            "SELECT oil_burners FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]
        hydro_dams = db.execute(
            "SELECT hydro_dams FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]
        nuclear_reactors = db.execute(
            "SELECT nuclear_reactors FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]
        solar_fields = db.execute(
            "SELECT solar_fields FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]

        gas_stations = db.execute(
            "SELECT gas_stations FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]
        general_stores = db.execute(
            "SELECT general_stores FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]
        farmers_markets = db.execute(
            "SELECT farmers_markets FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]
        malls = db.execute(
            "SELECT malls FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]
        banks = db.execute(
            "SELECT banks FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]

        city_parks = db.execute(
            "SELECT city_parks FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]
        hospitals = db.execute(
            "SELECT hospitals FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]
        libraries = db.execute(
            "SELECT libraries FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]
        universities = db.execute(
            "SELECT universities FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]
        monorails = db.execute(
            "SELECT monorails FROM proInfra WHERE id=(?)", (pId,)).fetchone()[0]

        connection.close()

        return render_template("province.html", pId=pId, population=population, name=name,
                               cityCount=cityCount, land=land, pollution=pollution,
                               oil_burners=oil_burners, hydro_dams=hydro_dams, nuclear_reactors=nuclear_reactors, solar_fields=solar_fields,
                               gas_stations=gas_stations, general_stores=general_stores, farmers_markets=farmers_markets, malls=malls,
                               banks=banks, city_parks=city_parks, hospitals=hospitals, libraries=libraries, universities=universities,
                               monorails=monorails)


@login_required
@app.route("/createprovince", methods=["GET", "POST"])
def createprovince():
    if request.method == "POST":

        cId = session["user_id"]

        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        pName = request.form.get("name")

        db.execute(
            "INSERT INTO provinces (userId, provinceName) VALUES (?, ?)", (cId, pName))
        province_id = db.execute(
            "SELECT id FROM provinces WHERE userId=(?) AND provinceName=(?)", (cId, pName)).fetchone()[0]
        db.execute("INSERT INTO proInfra (id) VALUES (?)", (province_id,))

        connection.commit()
        connection.close()

        return redirect("/provinces")
    else:
        return render_template("createprovince.html")
