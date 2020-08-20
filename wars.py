from app import app
from flask import Flask, request, render_template, session, redirect, abort
from flask_session import Session
import sqlite3
from helpers import login_required, error


@login_required
@app.route("/wars", methods=["GET", "POST"])
def wars():

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()
    cId = session["user_id"]

    if request.method == "GET":  # maybe optimise this later with css anchors
        # obtain all ground unit numbers from sql table
        tanks = db.execute(
            "SELECT tanks FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        soldiers = db.execute(
            "SELECT soldiers FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        artillery = db.execute(
            "SELECT artillery FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        # obtain all air unit numbers from sql table
        flying_fortresses = db.execute(
            "SELECT flying_fortresses FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        fighter_jets = db.execute(
            "SELECT fighter_jets FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        apaches = db.execute(
            "SELECT apaches FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        # obtain all navy unit numbers from sql table
        destroyers = db.execute(
            "SELECT destroyers FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        cruisers = db.execute(
            "SELECT cruisers FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        submarines = db.execute(
            "SELECT submarines FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        # obtain all special unit numbers from sql table
        spies = db.execute(
            "SELECT spies FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        icbms = db.execute(
            "SELECT ICBMs FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        nukes = db.execute(
            "SELECT nukes FROM military WHERE id=(?)", (cId,)).fetchone()[0]

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
            attacking = zip(attackingWars, attackingNames)
        except TypeError:
            attacking = 0

        # gets a defending tuple
        try:
            defendingWars = db.execute(
                "SELECT attacker FROM wars WHERE defender=(?) ORDER BY defender", (cId,)).fetchall()
            defendingNames = db.execute(
                "SELECT username FROM users WHERE id=(SELECT attacker FROM wars WHERE defender=(?) ORDER BY defender)", (cId,)).fetchall()
            defending = zip(defendingWars, defendingNames)
        except TypeError:
            defending = 0

        # gets a warsCount value
        warsCount = db.execute(
            "SELECT COUNT(attacker) FROM wars WHERE defender=(?) OR attacker=(?)", (cId, cId)).fetchone()[0]

        # returns ALL the VALUES to wars.html
        return render_template("wars.html", tanks=tanks, soldiers=soldiers, artillery=artillery,
                               flying_fortresses=flying_fortresses, fighter_jets=fighter_jets, apaches=apaches,
                               destroyers=destroyers, cruisers=cruisers, submarines=submarines,
                               spies=spies, icbms=icbms, nukes=nukes, cId=cId, yourCountry=yourCountry,
                               warsCount=warsCount, defending=defending, attacking=attacking)

# the flask route that activates when you click attack on a nation in your wars page.
# check if you have enough supplies.


@login_required
@app.route("/wars/<attackingNation>/defendingNation", methods=["GET", "POST"])
def wars_route(attackingNation, defendingNation):

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()
    cId = session["user_id"]

    if request.method == "GET":
        # if the method is get THE USER IS PROBABLY HACKING (or at least they typed in the URL directly which should never happen, maybe by a bookmark)
        return render_template("badresult.html")
    if request.method == "POST":
        # returns ALL the VALUES to warResult.html
        return render_template("wars.html")
        """tanks=tanks, soldiers=soldiers, artillery=artillery,
                                flying_fortresses=flying_fortresses, fighter_jets=fighter_jets, apaches=apaches,
                                destroyers=destroyers, cruisers=cruisers, submarines=submarines,
                                spies=spies, icbms=icbms, nukes=nukes, cId=cId, yourCountry=yourCountry,
                                warsCount=warsCount, defending=defending, attacking=attacking"""


@login_required
@app.route("/find_targets", methods=["GET", "POST"])
def find_targets():

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()
    cId = session["user_id"]

    if request.method == "GET":
        return render_template("find_targets.html")
    else:
        # Selects the country that the user is attacking
        defender = request.form.get("defender")

        try:
            defender_id = db.execute(
                "SELECT id FROM users WHERE username=(?)", (defender,)).fetchone()[0]

            if defender_id == cId:
                return "Can't declare war on yourself"

            already_war_with = db.execute("SELECT attacker, defender FROM wars WHERE attacker=(?) OR defender=(?)", (cId, cId,)).fetchall()
            if (cId, defender_id,) in already_war_with or (defender_id, cId) in already_war_with:
                return "You already fight against..."

        except TypeError:
            # Redirects the user to an error page
            return error(400, "No such country")

        db.execute(
            "INSERT INTO wars (attacker, defender) VALUES (?, ?)", (cId, defender_id))
        connection.commit()
        connection.close()
        return redirect("/wars")
# if everything went through, remove the cost of supplies from the amount of supplies the country has.
