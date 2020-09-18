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

        units = 37894562385
        emptyCountryDict = {'eName': 'placeholder', 'soldiers': 'Unknown', 'tanks': 'Unknown', 'artillery': 'Unknown', 'bombers': 'Unknown', 'fighters': 'Unknown', 'apaches': 'Unknown',
                            'destroyers': 'Unknown', 'cruisers': 'Unknown', 'submarines': 'Unknown', 'spies': 'Unknown', 'icbms': 'Unknown', 'nukes': 'Unknown'}
        # retrieve all entries from the spy table where spyer = cId

        spyinfodb = db.execute("SELECT * FROM spyinfo WHERE spyer=(?)", (cId,)).fetchall()
        print(spyinfodb)
        spyEntries = []
        for tuple in spyinfodb:
            spyEntries.append(emptyCountryDict)
            spyEntries['eName'] = db.execute("SELECT username FROM users WHERE id=(?)", (tuple[2],)).fetchone()[0]
        
        # for each entry make a 'enemyNation': emptyCountryDict and add to a list of spyEntries

        db.close()
        connection.close()
        return render_template("intelligence.html", units=units, yourCountry=yourCountry, enemyCountry="enemyCountry")
    return 'hi'
