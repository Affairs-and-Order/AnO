from app import app
from flask import Flask, request, render_template, session, redirect, abort
from flask_session import Session
import sqlite3
from helpers import login_required, error
from attack_scripts import Nation, Military

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
            attackingNames = db.execute("SELECT username FROM users WHERE id=(SELECT defender FROM wars WHERE attacker=(?) ORDER BY defender)", (cId,)).fetchall()
            # generates list of tuples. The first element of each tuple is the country being attacked, the second element is the username of the countries being attacked.
            attackingIds = db.execute("SELECT id FROM wars WHERE attacker=(?)", (cId,)).fetchall()
            attacking = zip(attackingWars, attackingNames, attackingIds)
        except TypeError:
            attacking = 0

        # gets a defending tuple
        try:
            defendingWars = db.execute(
                "SELECT attacker FROM wars WHERE defender=(?) ORDER BY defender", (cId,)).fetchall()
            defendingNames = db.execute(
                "SELECT username FROM users WHERE id=(SELECT attacker FROM wars WHERE defender=(?) ORDER BY defender)", (cId,)).fetchall()
            defendingIds = db.execute("SELECT id FROM wars WHERE defender=(?)", (cId,)).fetchall()
            defending = zip(defendingWars, defendingNames, defendingIds)
        except TypeError:
            defending = 0

        # WHAT DOES THIS DO??? -- Steven
        # Selects how many users the user is in -- t0dd
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
@app.route("/warchoose", methods=["GET", "POST"])
def warChoose():

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()
    cId = session["user_id"]

    if request.method == "GET":
        # user shouldnt access page this way
        return render_template("wars.html")
    if request.method == "POST":
        # returns ALL the VALUES to warchoose.html
        return render_template("wars.html")
        """tanks=tanks, soldiers=soldiers, artillery=artillery,
                                bombers=bombers, fighters=fighters, apaches=apaches,
                                destroyers=destroyers, cruisers=cruisers, submarines=submarines,
                                spies=spies, icbms=icbms, nukes=nukes, cId=cId, yourCountry=yourCountry,
                                warsCount=warsCount, defending=defending, attacking=attacking"""


# page 3 where you choose what 3 units to attack
@login_required
@app.route("/waramount", methods=["POST"])
def warAmount():
    return render_template("waramount.html")




# page 4 results and tax set if a morale reaches 0
@login_required
@app.route("/warResult", methods=["POST"])
def warResult():
    return render_template("warResult.html")


# Endpoint for war declaration
@login_required
@app.route('/declare_war', methods=["POST"])
def declare_war():
    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()

    # Selects the country that the user is attacking
    defender = request.form.get("defender")
    war_message = request.form.get("description")
    war_type = request.form.get("warType")

    try:
        defender_id = db.execute("SELECT id FROM users WHERE username=(?)", (defender,)).fetchone()[0]

        attacker = Nation(session["user_id"])
        defender = Nation(defender_id)

        if attacker.id == defender.id:
            return "Can't declare war on yourself"

        already_war_with = db.execute("SELECT attacker, defender FROM wars WHERE attacker=(?) OR defender=(?)", (attacker.id, attacker.id,)).fetchall()

        if (attacker.id, defender_id,) in already_war_with or (defender_id, attacker.id) in already_war_with:
            return "You already fight against..."

        attacker_provinces = attacker.get_provinces()["provinces_number"]
        defender_provinces = defender.get_provinces()["provinces_number"]

        if (attacker_provinces-1 == defender_provinces) or (attacker_provinces+1 == defender_provinces) or (attacker_provinces == defender_provinces):
            pass
        else:
            return "Can't declare war because the province difference is too big"


    except TypeError:
        # Redirects the user to an error page
        return error(400, "No such country")

    db.execute("INSERT INTO wars (attacker, defender, war_type, agressor_message) VALUES (?, ?, ?, ?)",
    (attacker.id, defender_id, war_type, war_message))
    connection.commit()
    connection.close()

    return redirect("/wars")

@login_required
@app.route("/find_targets", methods=["GET", "POST"])
def find_targets():

    if request.method == "GET":
        return render_template("find_targets.html")
    else:
        # TODO: maybe delete the sql fetch and create a centralized way to fetch it
        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        defender = request.form.get("defender")
        defender_id = db.execute("SELECT id FROM users WHERE username=(?)", (defender,)).fetchone()[0]

        return redirect("/country/id={}".format(defender_id))

# if everything went through, remove the cost of supplies from the amount of supplies the country has.

@login_required
@app.route("/defense", methods=["GET", "POST"])
def defense():
    cId = session["user_id"]
    units = Military.get_military(cId)

    if request.method == "GET":
        return render_template("defense.html", units=units)

    elif request.method == "POST":
        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()
        nation = db.execute("SELECT * FROM nation WHERE nation_id=(?)", (cId,)).fetchone()

        # Defense units came from POST request (TODO: attach it to the frontend)
        defense_units = ["soldier", "tank", "apache"]

        # Default defense
        # nation_id = nation[1]
        # default_defense = nation[2]

        # TODO: check is selected unit names are valid
        if nation:
            if len(defense_units) == 3:
                
                # default_defense is stored in the db: 'unit1,unit2,unit3'
                defense_units = ",".join(defense_units)
                db.execute("UPDATE nation SET default_defense=(?) WHERE nation_id=(?)", (defense_units, nation[1]))
                connection.commit()
            else:
                return "Invalid number of units selected!"
        else:
            return "Nation is not created!"

        # should be a back button on this page to go back to wars so dw about some infinite loop
        # next we need to insert the 3 defending units set as a value to the nation's table property (one in each war): defense
        # db.execute("INSERT INTO wars (attacker, defender) VALUES (?, ?)", (cId, defender_id))
        connection.close()

        return render_template("defense.html", units=units)

@login_required
@app.route("/war/<war_id>", methods=["GET"])
def war_with_id(war_id):

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()

    cId = session["user_id"]

    if war_id.isdigit == False:
        return error(400, "War id must be an integer")

    defender = db.execute("SELECT defender FROM wars WHERE id=(?)", (war_id,)).fetchone()[0]
    defender_name = db.execute("SELECT username FROM users WHERE id=(?)", (defender,)).fetchone()[0]

    attacker = db.execute("SELECT attacker FROM wars WHERE id=(?)", (war_id,)).fetchone()[0]
    attacker_name = db.execute("SELECT username FROM users WHERE id=(?)", (attacker,)).fetchone()[0]

    war_type = db.execute("SELECT war_type FROM wars WHERE id=(?)", (war_id,)).fetchone()[0]
    agressor_message = db.execute("SELECT agressor_message FROM wars WHERE id=(?)", (war_id,)).fetchone()[0]

    if cId == defender:
        cId_type = "defender"
    elif cId == attacker:
        cId_type = "attacker"
    else:
        cId_type = "spectator"

    if cId_type == "spectator":
        return error(400, "You can't view this war")

    return render_template('war.html', defender=defender, attacker=attacker,
    attacker_name=attacker_name, defender_name=defender_name, war_type=war_type,
    agressor_message=agressor_message, cId_type=cId_type)
