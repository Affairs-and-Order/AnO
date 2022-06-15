# FULLY MIGRATED

from app import app
from flask import request, render_template, session, redirect
from helpers import login_required, error
from attack_scripts import Military
import time
from random import random
import psycopg2
import os
from dotenv import load_dotenv
import variables
import random as rand
import time
load_dotenv()

@app.route("/intelligence", methods=["GET"])
@login_required
def intelligence():
    if request.method == "GET":

        connection = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"))
        db = connection.cursor()
        cId = session["user_id"]

        # delete entries older than 14 days
        # db.execute("DELETE FROM spyentries WHERE date<%s",
        #            (floor(time.time())-86400*14,))

        db.execute("SELECT username FROM users WHERE id=%s", (cId,))
        yourCountry = db.fetchone()[0]

        emptyCountryDict = {'eName': 'placeholder'}
        for unittype in Military.allUnits:
            emptyCountryDict[unittype] = 'Unknown'

        resources = variables.RESOURCES

        for resource in resources:
            emptyCountryDict[resource] = "Unknown"

        db.execute("SELECT * FROM spyinfo WHERE spyer=%s", (cId,))
        spyinfodb = db.fetchall()

        spyEntries = []
        for i, tupleEntry in enumerate(spyinfodb, start=0):

            spyEntries.append(emptyCountryDict)

            try:
                eId = tupleEntry[2]

                db.execute("SELECT username FROM users WHERE id=%s", (eId,))
                spyEntries[i]['eName'] = db.fetchone()[0]

                for j, unittype in enumerate(Military.allUnits):
                    if tupleEntry[j+2] == 'true':

                        db.execute("SELECT %s FROM military WHERE id=%s", (unittype, eId,))
                        spyEntries[i][unittype] = db.fetchone()[0]
                        
                for j, resource in enumerate(resources):
                    if tupleEntry[j+14] == 'true':

                        db.execute("SELECT %s FROM resources WHERE id=%s", (resource, eId,))
                        spyEntries[i][resource] = db.fetchone()[0]
            except:
                spyEntries[i]['eName'] = 'Enemy Nation Name'
                # delete the spy entry if the spyee doesnt exist anymore
                # db.execute("DELETE FROM spyentries WHERE id=%s", (eId,))
                # commented so we dont delete test spyentries
                # return "enemy nation doesn't exist"

        connection.close()
        return render_template("intelligence.html", yourCountry=yourCountry, spyEntries=spyEntries)


@app.route("/spyAmount", methods=["GET", "POST"])
@login_required
def spyAmount():
    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()
    cId = session["user_id"]
    if request.method == "GET":
        db.execute("SELECT username FROM users WHERE id=%s", (cId,))
        yourCountry = db.fetchone()[0]
        return render_template("spyAmount.html", yourCountry=yourCountry, spies=spies)

    # make the spy entry here
    if request.method == "POST":
        prep = request.form.get("prep")
        spies = request.form.get("amount")
        eId = request.form.get("enemy")

        db.execute("SELECT defcon FROM users WHERE id=%s", (eId,))
        eDefcon = db.fetchone()[0]

        db.execute("SELECT spies FROM military WHERE id=%s", (eId,))
        eSpies = db.fetchone()[0]

        # calculate what values have been revealed based on prep, amount, edefcon, espies


        resources = variables.RESOURCES
                     
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


# TODO: add notifications
@app.route("/spyResult", methods=["GET", "POST"])
@login_required
def spyResult():
    if request.method == "GET":
        spyEntry = session["spyEntry"]
        # You've conducted a spy operation on {{enemyNation}} and revealed the following information {{spyEntry}}.
        return render_template("spyResult.html", enemyNation=enemyNation, spyEntry=spyEntry)
    if request.method == "POST":

        cId = session["user_id"]
        eId = request.form.get("country")
        spies = int(request.form.get("spies"))
        spy_type = request.form.get("spy_type")

        connection = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"))

        db = connection.cursor()

        db.execute("SELECT spies FROM military WHERE id=%s", (cId,))
        actual_spies = db.fetchone()[0]

        if spies > actual_spies:
            return error(400, f"You don't have enough spies ({spies}/{actual_spies}). Missing {actual_spies-spies} spies")


        db.execute("SELECT spies FROM military WHERE id=%s", (eId,))
        enemy_spies = db.fetchone()[0]

        print(eId, enemy_spies)

        executed_spies = 0 # ADD NOTIFICATION FOR THIS
        uncovered_spies = 0 # ADD NOTIFICATION FOR THIS
        uncovered = {}

        if spy_type == "resources":
            for resource in variables.RESOURCES:
                own_rand = round(rand.uniform(0, 1), 3)
                enemy_rand = round(rand.uniform(0, 1), 3)

                own_score = own_rand * spies
                enemy_score = enemy_rand * enemy_spies

                if own_score == 0: own_score = 0.0001
                if enemy_score == 0: enemy_score = 0.0001

                multiplier = enemy_score / own_score

                if multiplier > 10:
                    executed_spies += 1
                if multiplier > 2:
                    uncovered_spies += 1
                if multiplier > 1: # Enemy won
                    uncovered[resource] = False
                elif multiplier <= 1: # Own won
                    uncovered[resource] = True

            uncovered_resources = [k for k,v in uncovered.items() if v]
            uncover_statement = f"SELECT {', '.join(uncovered_resources)}" + " FROM resources WHERE id=%s"
            db.execute(uncover_statement, (eId,))
            resources = db.fetchall()[0]

            print(uncovered_resources)
            print(resources)

            # db.execute("INSERT INTO spyinfo (spyer, spyee, date) VALUES (%s, %s, %s)", (cId, eId, time.time()))

            update_resources = []
            for res, amo in zip(uncovered_resources, resources):
                update_resources.append(f"{res}={amo}")
            print(update_resources)
            update_resources_string = ", ".join(update_resources)
            print(update_resources_string)

            spyinfo_update = f"UPDATE spyinfo SET {update_resources_string}" + " WHERE id=%s"

            
        # db.execute("UPDATE military SET spies=spies-%s WHERE id=%s", (executed_spies, cId))

        connection.commit()
        connection.close()

        return redirect("/intelligence")