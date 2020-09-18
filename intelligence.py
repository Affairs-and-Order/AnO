from app import app
from flask import Flask, request, render_template, session, redirect, abort, flash, url_for
from flask_session import Session
import sqlite3
from helpers import login_required, error
from attack_scripts import Nation, Military
from units import Units
import time
from math import floor
from random import random


@login_required
@app.route("/intelligence", methods=["GET"])
def intelligence():
    if request.method == "GET":
        connection = sqlite3.connect("affo/aao.db")
        db = connection.cursor()
        cId = session["user_id"]

        # delete entries older than 14 days
        # db.execute("DELETE FROM spyentries WHERE date<(?)",
        #            (floor(time.time())-86400*14,))

        yourCountry = db.execute(
            "SELECT username FROM users WHERE id=(?)", (cId,)).fetchone()[0]

        emptyCountryDict = {'eName': 'placeholder'}
        for unittype in Military.allUnits:
            emptyCountryDict[unittype] = 'Unknown'

        resources = ["rations", "oil", "coal", "uranium", "bauxite", "lead", "copper", "iron",
                     "lumber", "components", "steel", "consumer_goods", "aluminium", "gasoline", "ammunition"]
        for resource in resources:
            emptyCountryDict[resource] = "Unknown"

        spyinfodb = db.execute(
            "SELECT * FROM spyinfo WHERE spyer=(?)", (cId,)).fetchall()
        spyEntries = []
        for i, tupleEntry in enumerate(spyinfodb, start=0):

            spyEntries.append(emptyCountryDict)

            try:
                eId = tupleEntry[2]
                spyEntries[i]['eName'] = db.execute(
                    "SELECT username FROM users WHERE id=(?)", (eId,)).fetchone()[0]
                for j, unittype in enumerate(Military.allUnits):
                    if tupleEntry[j+2] == 'true':
                        spyEntries[i][unittype] = db.execute(
                            f"SELECT {unittype} FROM military WHERE id=(?)", (eId,)).fetchone()[0]
                for j, resource in enumerate(resources):
                    if tupleEntry[j+14] == 'true':
                        spyEntries[i][resource] = db.execute(
                            f"SELECT {resource} FROM resources WHERE id", (eId,)).fetchone()[0]
            except:
                spyEntries[i]['eName'] = 'Enemy Nation Name'
                # delete the spy entry if the spyee doesnt exist anymore
                # db.execute("DELETE FROM spyentries WHERE id=(?)", (eId,))
                # commented so we dont delete test spyentries
                # return "enemy nation doesn't exist"

        db.close()
        connection.close()
        return render_template("intelligence.html", yourCountry=yourCountry, spyEntries=spyEntries)


@login_required
@app.route("/spyAmount", methods=["GET", "POST"])
def spyAmount():
    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()
    cId = session["user_id"]
    if request.method == "GET":
        yourCountry = db.execute(
            "SELECT username FROM users WHERE id=(?)", (cId,)).fetchone()[0]
        return render_template("spyAmount.html", yourCountry=yourCountry, spies=spies)
    # make the spy entry here
    if request.method == "POST":
        prep = request.form.get("prep")
        spies = request.form.get("amount")
        eId = request.form.get("enemy")
        eDefcon = db.execute(
            "SELECT defcon FROM users WHERE id=(?)", (eId,)).fetchone()[0]
        eSpies = db.execute(
            "SELECT spies FROM military WHERE id=(?)", (eId,)).fetchone()[0]
        # calculate what values have been revealed based on prep, amount, edefcon, espies


        resources = ["rations", "oil", "coal", "uranium", "bauxite", "lead", "copper", "iron",
                     "lumber", "components", "steel", "consumer_goods", "aluminium", "gasoline", "ammunition"]
        revealChance = prep * spies / (eDefcon * eSpies)
        spyEntry = {}
        for unit in Military.allUnits:
            if random() * revealChance > 0.5:
                spyEntry[unit] = 'true'
            else:
                spyEntry[unit] = 'false'
        for resource in resources:
            if random() * revealChance > 0.5:
                spyEntry[resource] = 'true'
            else:
                spyEntry[resource] = 'false'
        if random() * revealChance > 0.5:
            spyEntry["defaultdefense"] = 'true'
        else:
            spyEntry["defaultdefense"] = 'false'

        # insert spyEntry into spytable with
        date = time.time()

        # sessionize spyResult jinja
        session['eId'] = eId
        session["spyEntry"] = spyEntry
        return redirect("/spyResult")


@login_required
@app.route("/spyResult", methods=["GET"])
def spyResult():
    spyEntry = session["spyEntry"]
    # You've conducted a spy operation on {{enemyNation}} and revealed the following information {{spyEntry}}.

    return render_template("spyResult.html", enemyNation=enemyNation, spyEntry=spyEntry)
