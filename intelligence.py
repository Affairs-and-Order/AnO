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

    connection = sqlite3.connect("affo/aao.db")
    db = connection.cursor()
    cId = session["user_id"]

    if request.method == "GET":
        normal_units = Military.get_military(cId)
        special_units = Military.get_special(cId)
        units = normal_units.copy()
        units.update(special_units)

        # obtain the user's country from sql table
        yourCountry = db.execute(
            "SELECT username FROM users WHERE id=(?)", (cId,)).fetchone()[0]

        # this creates an array called attacking which stores tuples in the format [(defendingCountryName1, defendingCountryUsername1), (defendingCountryName2, defendingCountryUsername2), ...].
        try:
            # selecting all current defenders of cId
            attackingWars = db.execute(
                "SELECT defender FROM wars WHERE attacker=(?) ORDER BY defender", (cId,)).fetchall()
            # selecting all usernames of current defenders of cId
            attackingNames = db.execute(
                "SELECT username FROM users WHERE id=(SELECT defender FROM wars WHERE attacker=(?) ORDER BY defender)", (cId,)).fetchall()
            # generates list of tuples. The first element of each tuple is the country being attacked, the second element is the username of the countries being attacked.
            attackingIds = db.execute(
                "SELECT id FROM wars WHERE attacker=(?)", (cId,)).fetchall()
            attacking = zip(attackingWars, attackingNames, attackingIds)
        except TypeError:
            attacking = 0

        # gets a defending tuple
        try:
            defendingWars = db.execute(
                "SELECT attacker FROM wars WHERE defender=(?) ORDER BY defender", (cId,)).fetchall()
            defendingNames = db.execute(
                "SELECT username FROM users WHERE id=(SELECT attacker FROM wars WHERE defender=(?) ORDER BY defender)", (cId,)).fetchall()
            defendingIds = db.execute(
                "SELECT id FROM wars WHERE defender=(?)", (cId,)).fetchall()
            defending = zip(defendingWars, defendingNames, defendingIds)
        except TypeError:
            defending = 0

        # the next two for loops delete wars if the war involves a deleted nation.
        # if wars can be removed when someone deletes their nation or we ban a nation instead of every time anyone opens their war page, that would be faster
        listOfUserIdTuples = db.execute("SELECT id FROM users").fetchall()
        userIdsLst = []
        for tuple in listOfUserIdTuples:
            for item in tuple:
                userIdsLst.append(item)
        defendingIdsLst = []
        for tuple in defendingIds:
            for item in tuple:
                defendingIdsLst.append(item)
        attackingIdsLst = []
        for tuple in attackingIds:
            for item in tuple:
                attackingIdsLst.append(item)
        print(userIdsLst, 'user')
        print(defendingIdsLst, "def")
        print(attackingIdsLst, "att")
        # if an id inside the defender's list is not in the user list
        for id in defendingIdsLst:
            if id not in userIdsLst:
                # delete the war with the the nonexistent user inside
                db.execute(
                    "DELETE FROM wars WHERE defender=(?) OR attacker=(?)", (id, id))
        for id in attackingIdsLst:
            if id not in userIdsLst:
                db.execute(
                    "DELETE FROM wars WHERE defender=(?) OR attacker=(?)", (id, id))
        connection.commit()

        warsCount = db.execute(
            "SELECT COUNT(attacker) FROM wars WHERE defender=(?) OR attacker=(?)", (cId, cId)).fetchone()[0]
        db.close()
        connection.close()
        return render_template("intelligence.html", units=units, cId=cId, yourCountry=yourCountry, warsCount=warsCount, defending=defending, attacking=attacking)
