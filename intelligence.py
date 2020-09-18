from app import app
from flask import Flask, request, render_template, session, redirect, abort, flash, url_for
from flask_session import Session
import sqlite3
from helpers import login_required, error
from attack_scripts import Nation, Military
from units import Units
import time


@login_required
@app.route("/intelligence", methods=["GET", "POST"])
def intelligence():

    if request.method == "GET":
        connection = sqlite3.connect("affo/aao.db")
        db = connection.cursor()
        cId = session["user_id"]
        print(cId)
        yourCountry = db.execute(
            "SELECT username FROM users WHERE id=(?)", (cId,)).fetchone()[0]

        units = 378985
        emptyCountryDict = {'eName': 'placeholder', 'soldiers': 'Unknown', 'tanks': 'Unknown', 'artillery': 'Unknown', 'bombers': 'Unknown', 'fighters': 'Unknown', 'apaches': 'Unknown',
                            'destroyers': 'Unknown', 'cruisers': 'Unknown', 'submarines': 'Unknown', 'spies': 'Unknown', 'icbms': 'Unknown', 'nukes': 'Unknown'}
        # retrieve all entries from the spy table where spyer = cId

        spyinfodb = db.execute(
            "SELECT * FROM spyinfo WHERE spyer=(?)", (cId,)).fetchall()
        print(spyinfodb)
        spyEntries = []
        for i, tupleEntry in enumerate(spyinfodb, start=0):

            spyEntries.append(emptyCountryDict)

            try:
                eId = tupleEntry[2]
                spyEntries[i]['eName'] = db.execute(
                    "SELECT username FROM users WHERE id=(?)", (eId,)).fetchone()[0]
            except:
                spyEntries[i]['eName'] = 'Enemy Nation Name'
                # return "enemy nation doesn't exist"

            for j, unittype in enumerate(Military.allUnits):

                if tupleEntry[j+2] == 'true':
                    spyEntries[i][unittype] = db.execute(
                        f"SELECT {unittype} FROM military WHERE id=(?)", (eId,)).fetchone()[0]

        db.close()
        connection.close()
        return render_template("intelligence.html", yourCountry=yourCountry, spyEntries=spyEntries)
    return 'hi'
