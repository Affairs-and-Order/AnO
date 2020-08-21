from app import app
from flask import Flask, request, render_template, session, redirect, abort
from flask_session import Session
import sqlite3
from helpers import login_required, error


'''
Page 1:
Goes to a page where each 3 units choose what type of unit to attack with (12 options, 9 war and 3 special). There's up to 8 of these boxes available, since you can attack 5 nations at once or defend from 3 nations at once (make this flexible tho).
War
9 check boxes

Special operations
3 check boxes

Continue button

Page 2:
Goes to a page where you choose how many to send of each of your 3 units, or 1 special

Page 3:
Goes to a page where you target what all your units attack (13 options: 9 war units, 3 specials, 1 morale) (targeting 3)

Page 4:
Whoever lost fewer value in units is the winner. Based on the degree, morale changes. Based on degree on winning, sets a tax on the losing nation.
'''

# so this is page 1 where you can select what units to attack with
@login_required
@app.route("/wars", methods=["GET"])
def wars():

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()
    cId = session["user_id"]

    if request.method == "GET":
        # obtain all ground unit numbers from sql table
        tanks = db.execute(
            "SELECT tanks FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        soldiers = db.execute(
            "SELECT soldiers FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        artillery = db.execute(
            "SELECT artillery FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        # obtain all air unit numbers from sql table
        bombers = db.execute(
            "SELECT bombers FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        fighters = db.execute(
            "SELECT fighters FROM military WHERE id=(?)", (cId,)).fetchone()[0]
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

        # WHAT DOES THIS DO??? -- Steven
        warsCount = db.execute(
            "SELECT COUNT(attacker) FROM wars WHERE defender=(?) OR attacker=(?)", (cId, cId)).fetchone()[0]

        # returns ALL the VALUES to wars.html
        return render_template("wars.html", tanks=tanks, soldiers=soldiers, artillery=artillery,
                               bombers=bombers, fighters=fighters, apaches=apaches,
                               destroyers=destroyers, cruisers=cruisers, submarines=submarines,
                               spies=spies, icbms=icbms, nukes=nukes, cId=cId, yourCountry=yourCountry,
                               warsCount=warsCount, defending=defending, attacking=attacking)

# the flask route that activates when you click attack on a nation in your wars page.
# check if you have enough supplies.

# page 2 choose how many of each of your units to send
# how to send only 3 three unit variables that were chosen in the last page??
@login_required
@app.route("/wars/<attackingNation>/defendingNation", methods=["GET", "POST"])
def wars_route(attackingNation, defendingNation):

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()
    cId = session["user_id"]

    if request.method == "GET":
        # if the method is get THE USER IS PROBABLY HACKING (or at least they typed in the URL directly which should never happen, maybe by a bookmark), btw I've abused some bugs with this in PnW
        return render_template("wars.html")
    if request.method == "POST":
        # returns ALL the VALUES to warResult.html
        return render_template("wars.html")
        """tanks=tanks, soldiers=soldiers, artillery=artillery,
                                bombers=bombers, fighters=fighters, apaches=apaches,
                                destroyers=destroyers, cruisers=cruisers, submarines=submarines,
                                spies=spies, icbms=icbms, nukes=nukes, cId=cId, yourCountry=yourCountry,
                                warsCount=warsCount, defending=defending, attacking=attacking"""

# page 3 where you choose what 3 units to attack


# page 4 results and tax set if a morale reaches 0

# Endpoint for war declaration
@login_required
@app.route('/declare_war', methods=["POST"])
def declare_war():
    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()
    cId = session["user_id"]

    # Selects the country that the user is attacking
    defender = request.form.get("defender")
    war_message = request.form.get("description")
    war_type = request.form.get("warType")

    try:
        defender_id = db.execute("SELECT id FROM users WHERE username=(?)", (defender,)).fetchone()[0]

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

@login_required
@app.route("/find_targets", methods=["GET", "POST"])
def find_targets():

    if request.method == "GET":
        return render_template("find_targets.html")
    else:
        #TODO: maybe delete the sql fetch and create a centralized way to fetch it
        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        defender = request.form.get("defender")
        defender_id = db.execute("SELECT id FROM users WHERE username=(?)", (defender,)).fetchone()[0]

        return redirect("/country/id={}".format(defender_id))

# if everything went through, remove the cost of supplies from the amount of supplies the country has.


@login_required
@app.route("/setdefaultdefense", methods=["GET", "POST"])
def setdefaultdefense():
    if request.method == "GET":
        # i think this is all that needs to be done for the GET request
        return render_template("setdefaultdefense.html")
    elif request.method == "POST":  # if the user selected 3 units for defense and submitted, it goes here
        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()
        cId = session["user_id"]
        # should be a back button on this page to go back to wars so dw about some infinite loop
        # next we need to insert the 3 defending units set as a value to the nation's table property (one in each war): defense
        #db.execute("INSERT INTO wars (attacker, defender) VALUES (?, ?)", (cId, defender_id))
        connection.commit()
        connection.close()
        return render_template("setdefaultdefense.html")
    else:
        return "REPORT DIRECTLY TO ADMIN WHAT JUST HAPPENED"
