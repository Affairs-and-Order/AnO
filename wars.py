from app import app
from flask import Flask, request, render_template, session, redirect, abort
from flask_session import Session
import sqlite3
from helpers import login_required, error
from attack_scripts import Nation, Military
from implement_units_management import Units
import time

'''
war page: choose a war

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

# so this is page 0, war menu, choose a war
@login_required
@app.route("/wars", methods=["GET"])
def wars():

    connection = sqlite3.connect('affo/aao.db')
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

        # WHAT DOES THIS DO??? -- Steven
        # Selects how many wars the user is in -- t0dd
        # got it :D
        warsCount = db.execute(
            "SELECT COUNT(attacker) FROM wars WHERE defender=(?) OR attacker=(?)", (cId, cId)).fetchone()[0]

        # returns ALL the VALUES to wars.html
        return render_template("wars.html", units=units, cId=cId, yourCountry=yourCountry, warsCount=warsCount, defending=defending, attacking=attacking)

# the flask route that activates when you click attack on a nation in your wars page.
# check if you have enough supplies.
# page 1: where you can select what units to attack with
@login_required
@app.route("/warchoose", methods=["GET", "POST"])
def warChoose():
    cId = session["user_id"]

    if request.method == "GET":

        # this is upon first landing on this page after the user clicks attack in wars.html
        normal_units = Military.get_military(cId)
        # special_units = Military.get_special(cId)
        units = normal_units.copy()
        # units.update(special_units)
        return render_template("warchoose.html", units=units)

    elif request.method == "POST":
        # this post request happens when they click submit, upon which we would redirect to /waramount
        # typical post redirect get pattern means we should do with the request.form.get values here (the 3 units)
        # store the 3 values in session and retrieve it in waramount later

        selected_units = {}
        selected_units[request.form.get("u1")] = 0
        selected_units[request.form.get("u2")] = 0
        selected_units[request.form.get("u3")] = 0

        attack_units = Units(cId)

        # Output error if any
        error = attack_units.attach_units(selected_units)

        # cache Unit object reference in session
        session["attack_units"] = attack_units

        # could also just retrieve all 9 possibilities from warchoose and just remove the ones that are null if that's easier for you Carson -- Steven
        '''
        session["soldiers"] = request.form.get("attack_units")
        session["tanks"] = request.form.get("attack_units")
        session["artillery"] = request.form.get("attack_units")
        ET CETERA
        session["attack_units"] = request.form.get("attack_units")
        session["attack_units"] = request.form.get("attack_units")
        session["attack_units"] = request.form.get("attack_units")

        session["attack_units"] = request.form.get("attack_units")
        session["attack_units"] = request.form.get("attack_units")
        session["attack_units"] = request.form.get("attack_units")

        '''

        return redirect('/waramount')

# page 2 choose how many of each of your units to send
# how to send only 3 three unit variables that were chosen in the last page??
@login_required
@app.route("/waramount", methods=["GET", "POST"])
def warAmount():
    cId = session["user_id"]

    if request.method == "GET":
        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()
        # cId=2

        # after the user clicks choose amount, they come to this page.
        attack_units = session["attack_units"]
        selected_units = list(attack_units.selected_units.keys())

        # find the max amount of units of each of those 3 the user can attack with to send to the waramount page on first load
        # IMPORTANT: this version is vulnerable to SQL injection attacks, FIX BEFORE PRODUCTION
        unitamount1 = db.execute(f"SELECT {selected_units[0]} FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        unitamount2 = db.execute(f"SELECT {selected_units[1]} FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        unitamount3 = db.execute(f"SELECT {selected_units[2]} FROM military WHERE id=(?)", (cId,)).fetchone()[0]

        connection.commit()
        db.close()
        connection.close()

        # if the user comes to this page by bookmark, it might crash because session['attack_units'] wouldn't exist
        # attack_units = session['attack_units']

        unitamounts = [unitamount1, unitamount2, unitamount3]
        return render_template("waramount.html", attack_units=selected_units, unitamounts=unitamounts)

    elif request.method == "POST":
        # session["unit_amounts"] = request.form.get("attack_units")

        # Separate object's units list from now units list
        selected_units = session["attack_units"].selected_units.copy()

        units_name = list(selected_units.keys())

        for number in range(1, 4):
            unit_amount = request.form.get(f"u{number}_amount", None)
            if not unit_amount:
                return "Invalid name argument coming in"

            selected_units[units_name[number-1]] = int(unit_amount)

        # Check every time when user input comes in lest user bypass input validation
        # Error code if any
        error = session["attack_units"].attach_units(selected_units)
        print(error)

        # same note as before as to how to use this request.form.get to get the unit amounts.
        return redirect('/wartarget')
    else:
        return "what shenaniganry just happened here?! REPORT TO THE ADMINS!!"

# page 3 where you choose what 3 enemy units to attack
@login_required
@app.route("/wartarget", methods=["GET", "POST"])
def warTarget():
    if request.method == "GET":
        # all war targets never change regardless of type of war, no variables to send here!
        return render_template("wartarget.html")
    else:
        # get targeted units
        session['targeted_units'] = request.form.get('targeted_units')

        # Traget cID and targeted units
        target = Units(3)
        target.attach_units({"soldiers": 0, "tanks": 0, "bombers": 0})
        attacker = session["attack_units"]
        Military.fight(attacker, target)

        return redirect('warResult')

# page 4 results and tax set if a morale reaches 0
@login_required
@app.route("/warResult", methods=["POST"])
def warResult():
    # grab your units from session
    # grab enemy target units from session
    # grab defending enemy units from database

    # multiply all your unit powers together, with bonuses if a counter is found
    # multiply all enemy defending units together, with bonuses if a counter is found

    # if your score is higher by 3x, annihilation,
    # if your score is higher by 2x, definite victory
    # if your score is higher, close victory,
    # if your score is lower, close defeat, 0 damage,
    # if your score is lower by 2x, massive defeat, 0 damage

    # from annihilation (resource, field, city, depth, blockade, air):
    # soldiers: resource control
    # tanks: field control and city control
    # artillery: field control
    # destroyers: naval blockade
    # cruisers: naval blockade
    # submarines: depth control
    # bombers: field control
    # apaches: city control
    # fighter jets: air control

    # counters:
    # soldiers beat artillery, apaches
    # tanks beat soldiers
    # artillery beat tanks
    # destroyers beat submarines
    # cruisers beat destroyers
    # submarines beat cruisers
    # bombers beat soldiers, tanks, destroyers, cruisers, submarines
    # apaches beat soldiers, tanks, bombers, fighter jets
    # fighter jets beat bombers

    # resource control: soldiers can now loot enemy munitions (minimum between 1 per 100 soldiers and 50% of their total munitions)
    # field control: soldiers gain 2x power
    # city control: 2x morale damage
    # depth control: missile defenses go from 50% to 20% and nuke defenses go from  35% to 10%
    # blockade: enemy can no longer trade
    # air control: enemy bomber power reduced by 60%


    # A = defendingscore / attackingscore
    # B = attackingscore / defendingscore
    # lose A % of all your attacking units, times a random factor between 0.8 and 1, rolled once for each unit (so 3 times)
    # lose B % of all defending units, times a random factor between 0.75 and 1, rolled once for each unit (so 3 times)
    # defending country loses B * 10 morale. (so if your score was 10x higher than opponent, you win in average 1 attack other than the random factor)
    # if you were the defending (beginning of war) country you also lose B infra


    # if enemy morale reaches 0:
        # X = your remaining morale (so this is from 0 to 100)
        # take X / 2 % of their res and cash, tax them by X % for 2 days
        # minimum 20% loot
    # MODIFIERS to X (war policies, war type):

    # WAR POLICIES:
    # "empire builder"--> winning gives no loot 2x reparation tax
    # "pirate" --> winning gives 2x more loot no reparation tax
    # "tactical" --> winning gives 1x loot 1x reparation tax
    # "pacifist" --> winning gives no loot no reparation tax, lowers project timer by 5 days, boosts your economy by 10%
    # "guerilla": --> winning gives 1x loot no reparation tax, losing makes you lose 40% less loot, and you resist 60% reparation tax.

    # WAR TYPES
    # "raze" --> no loot, no reparation tax, destroy 10x more buildings, destroys money/res
    # "sustained" --> 1x loot, 1x infra destruction, 1x building destroy
    # "loot" --> 2x loot, 0.1x infra destruction, buildings cannot be destroyed
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
        defender_id = db.execute(
            "SELECT id FROM users WHERE username=(?)", (defender,)).fetchone()[0]

        attacker = Nation(session["user_id"])
        defender = Nation(defender_id)

        if attacker.id == defender.id:
            return "Can't declare war on yourself"

        already_war_with = db.execute(
            "SELECT attacker, defender FROM wars WHERE attacker=(?) OR defender=(?)", (attacker.id, attacker.id,)).fetchall()

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

    db.execute("INSERT INTO wars (attacker, defender, war_type, agressor_message, start_date) VALUES (?, ?, ?, ?, ?)",
               (attacker.id, defender_id, war_type, war_message, time.time()))
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
        defender_id = db.execute(
            "SELECT id FROM users WHERE username=(?)", (defender,)).fetchone()[0]

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
        nation = db.execute(
            "SELECT * FROM nation WHERE nation_id=(?)", (cId,)).fetchone()

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
                db.execute(
                    "UPDATE nation SET default_defense=(?) WHERE nation_id=(?)", (defense_units, nation[1]))
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

    defender = db.execute(
        "SELECT defender FROM wars WHERE id=(?)", (war_id,)).fetchone()[0]
    defender_name = db.execute(
        "SELECT username FROM users WHERE id=(?)", (defender,)).fetchone()[0]

    attacker = db.execute(
        "SELECT attacker FROM wars WHERE id=(?)", (war_id,)).fetchone()[0]
    attacker_name = db.execute(
        "SELECT username FROM users WHERE id=(?)", (attacker,)).fetchone()[0]

    war_type = db.execute(
        "SELECT war_type FROM wars WHERE id=(?)", (war_id,)).fetchone()[0]
    agressor_message = db.execute(
        "SELECT agressor_message FROM wars WHERE id=(?)", (war_id,)).fetchone()[0]

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
