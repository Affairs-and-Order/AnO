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
        print(Military.allUnits)
        emptyCountryDict = {'eName': 'placeholder', 'soldiers': 'Unknown', 'tanks': 'Unknown', 'artillery': 'Unknown', 'bombers': 'Unknown', 'fighters': 'Unknown', 'apaches': 'Unknown',
                            'destroyers': 'Unknown', 'cruisers': 'Unknown', 'submarines': 'Unknown', 'spies': 'Unknown', 'icbms': 'Unknown', 'nukes': 'Unknown'}
        # retrieve all entries from the spy table where spyer = cId

        spyinfodb = db.execute(
            "SELECT * FROM spyinfo WHERE spyer=(?)", (cId,)).fetchall()
        print(spyinfodb)
        spyEntries = []
        for index, tupleEntry in enumerate(spyinfodb, start=0):
            print(index)
            print(tupleEntry)
            spyEntries.append(emptyCountryDict)

            try:
                eId = tupleEntry[2]
                spyEntries[index]['eName'] = db.execute(
                    "SELECT username FROM users WHERE id=(?)", (eId,)).fetchone()[0]
            except:
                spyEntries[index]['eName'] = 'Enemy Nation Name'
                # return "enemy nation doesn't exist"


            if tupleEntry[3] == 'true':
                spyEntries[index]['soldiers'] = db.execute(
                    "SELECT soldiers FROM military WHERE id=(?)", (eId,)).fetchone()[0]
            if tupleEntry[4] == 'true':
                spyEntries[index]['tanks'] = db.execute(
                    "SELECT tanks FROM military WHERE id=(?)", (eId,)).fetchone()[0]
            if tupleEntry[5] == 'true':
                spyEntries[index]['soldiers'] = db.execute(
                    "SELECT soldiers FROM military WHERE id=(?)", (eId,)).fetchone()[0]
            if tupleEntry[6] == 'true':
                spyEntries[index]['soldiers'] = db.execute(
                    "SELECT soldiers FROM military WHERE id=(?)", (eId,)).fetchone()[0]
            if tupleEntry[7] == 'true':
                spyEntries[index]['soldiers'] = db.execute(
                    "SELECT soldiers FROM military WHERE id=(?)", (eId,)).fetchone()[0]
            if tupleEntry[8] == 'true':
                spyEntries[index]['soldiers'] = db.execute(
                    "SELECT soldiers FROM military WHERE id=(?)", (eId,)).fetchone()[0]
            if tupleEntry[9] == 'true':
                spyEntries[index]['soldiers'] = db.execute(
                    "SELECT soldiers FROM military WHERE id=(?)", (eId,)).fetchone()[0]
            if tupleEntry[10] == 'true':
                spyEntries[index]['soldiers'] = db.execute(
                    "SELECT soldiers FROM military WHERE id=(?)", (eId,)).fetchone()[0]
            if tupleEntry[11] == 'true':
                spyEntries[index]['soldiers'] = db.execute(
                    "SELECT soldiers FROM military WHERE id=(?)", (eId,)).fetchone()[0]
            if tupleEntry[12] == 'true':
                spyEntries[index]['soldiers'] = db.execute(
                    "SELECT soldiers FROM military WHERE id=(?)", (eId,)).fetchone()[0]
            if tupleEntry[3] == 'true':
                spyEntries[index]['soldiers'] = db.execute(
                    "SELECT soldiers FROM military WHERE id=(?)", (eId,)).fetchone()[0]
            if tupleEntry[3] == 'true':
                spyEntries[index]['soldiers'] = db.execute(
                    "SELECT soldiers FROM military WHERE id=(?)", (eId,)).fetchone()[0]
            spyEntries[index]['soldiers'] = tupleEntry[3]
            print('hi')

        db.close()
        connection.close()
        return render_template("intelligence.html", yourCountry=yourCountry, spyEntries=spyEntries)
    return 'hi'
