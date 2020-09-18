from app import app
from flask import Flask, request, render_template, session, redirect, abort, flash, url_for
from flask_session import Session
import sqlite3
from helpers import login_required, error
from attack_scripts import Nation, Military
from units import Units
import time


@login_required
@app.route("/intelligence", methods=["GET"])
def intelligence():
    if request.method == "GET":
        connection = sqlite3.connect("affo/aao.db")
        db = connection.cursor()
        cId = session["user_id"]
        
        # db.execute("DELETE FROM spyentries WHERE date<(?)", (datenow-14days,))
        yourCountry = db.execute(
            "SELECT username FROM users WHERE id=(?)", (cId,)).fetchone()[0]

        emptyCountryDict = {'eName': 'placeholder'}
        for unittype in Military.allUnits:
            emptyCountryDict[unittype] = 'Unknown'

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
            except:
                spyEntries[i]['eName'] = 'Enemy Nation Name'
                # delete the spy entry if the spyee doesnt exist anymore
                # db.execute("DELETE FROM spyentries WHERE id=(?)", (eId,))
                # commented so we dont delete test spyentries
                # return "enemy nation doesn't exist"

        db.close()
        connection.close()
        return render_template("intelligence.html", yourCountry=yourCountry, spyEntries=spyEntries)
