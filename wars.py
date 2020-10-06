from app import app
from flask import Flask, request, render_template, session, redirect, abort, flash, url_for
from flask_session import Session
import sqlite3
from helpers import login_required, error
from attack_scripts import Nation, Military, Economy
from units import Units
import time
from helpers import get_influence, check_required

"""
war page: choose a war

Page 1:
Goes to a page where each 3 units choose what type of unit to attack with (12 options, 9 war and 3 special). There"s up to 8 of these boxes available, since you can attack 5 nations at once or defend from 3 nations at once (make this flexible tho).
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
"""

# NOTICE put these "not routes" inside a different file like utils.py
# Update supplies amount only when user visit page where supplies interaction neccessary
# Call this from every function which displays or works with the supplies
def update_supply(war_id):
    connection = sqlite3.connect("affo/aao.db")
    db = connection.cursor()

    attacker_supplies, defender_supplies, supply_date = db.execute("SELECT attacker_supplies,defender_supplies,last_visited FROM wars WHERE id=?", (war_id,)).fetchall()[0]
    current_time = time.time()

    if current_time < int(supply_date):
        return "TIME STAMP IS CORRUPTED"

    time_difference = current_time - supply_date
    hours_count = time_difference//3600
    supply_by_hours = hours_count*50 # 50 supply in every hour

    # TODO: give bonus supplies if there is specific infrastructure for it
    # if supply_bonus: xy

    if supply_by_hours > 0:
        attacker_id, defender_id = db.execute("SELECT attacker,defender FROM wars where id=(?)", (war_id,)).fetchone()

        # TODO: this isn't tested yet until the END TODO, so test it
        attacker_upgrades = Nation.get_upgrades("supplies", attacker_id)
        defender_upgrades = Nation.get_upgrades("supplies", defender_id)

        for i in attacker_upgrades.values():
            attacker_supplies += i

        for i in defender_upgrades.values():
            defender_supplies += i
        # END TODO

        db.execute("UPDATE wars SET attacker_supplies=(?), defender_supplies=(?), last_visited=(?) WHERE id=(?)", (supply_by_hours+attacker_supplies, supply_by_hours+defender_supplies, time.time(), war_id))
        connection.commit()

# so this is page 0, war menu, choose a war
@app.route("/wars", methods=["GET", "POST"])
@login_required
def wars():

    connection = sqlite3.connect("affo/aao.db")
    db = connection.cursor()
    cId = session["user_id"]
    # cId = 10

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
                "SELECT defender FROM wars WHERE attacker=(?) AND peace_date IS NULL ORDER BY defender", (cId,)).fetchall()
            # selecting all usernames of current defenders of cId
            attackingNames = db.execute(
                "SELECT username FROM users WHERE id=(SELECT defender FROM wars WHERE attacker=(?) ORDER BY defender)", (cId,)).fetchall()
            # generates list of tuples. The first element of each tuple is the country being attacked, the second element is the username of the countries being attacked.
            attackingIds = db.execute(
                "SELECT id FROM wars WHERE attacker=(?) AND peace_date IS NULL", (cId,)).fetchall()
            # attacking = zip(attackingWars, attackingNames, attackingIds)
        except TypeError:
            attacking = 0

        # gets a defending tuple
        try:
            defendingWars = db.execute(
                "SELECT attacker FROM wars WHERE defender=(?) AND peace_date IS NULL ORDER BY defender ", (cId,)).fetchall()
            defendingNames = db.execute(
                "SELECT username FROM users WHERE id=(SELECT attacker FROM wars WHERE defender=(?) ORDER BY defender)", (cId,)).fetchall()
            defendingIds = db.execute(
                "SELECT id FROM wars WHERE defender=(?)", (cId,)).fetchall()
            # defending = zip(defendingWars, defendingNames, defendingIds)
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

        warsCount = db.execute("SELECT COUNT(attacker) FROM wars WHERE (defender=(?) OR attacker=(?)) AND peace_date IS NULL", (cId, cId)).fetchone()[0]

        # NOTE: at defender_stats and attacker_stats later maybe use the  Military.get_morale("defender_morale", attacker, defender) for morale check
        # because the code below is redundant but the get_morale function works only for Units instances currently

        # *_war_morales = [our_morale, enemy_morale]
        attacking_war_morales = []
        defending_war_morales = []

        for war_id in attackingIds:
            attacking_war_morales.append([
            db.execute("SELECT attacker_morale FROM wars WHERE id=(?)", (war_id[0],)).fetchone()[0],
            db.execute("SELECT defender_morale FROM wars WHERE id=(?)", (war_id[0],)).fetchone()[0]
            ])

        for war_id in defendingIds:
            defending_war_morales.append([
            db.execute("SELECT attacker_morale FROM wars WHERE id=(?)", (war_id[0],)).fetchone()[0],
            db.execute("SELECT defender_morale FROM wars WHERE id=(?)", (war_id[0],)).fetchone()[0]
            ])

        # complete_war_ids = attackingIdsLst+defendingIdsLst
        # attacking_morale = []
        # defending_morale = []
        #
        # for war_id in complete_war_ids:
        #     attacking_morale.append(db.execute("SELECT defender_morale FROM wars WHERE id=(?)", (war_id,)).fetchone()[0])
        #     defending_morale.append(db.execute("SELECT attacker_morale FROM wars WHERE id=(?)", (war_id,)).fetchone()[0])

        # defending_morale and attacking_morale include to wars.html
        defending = zip(defendingWars, defendingNames, defendingIds, defending_war_morales)

        attacking = zip(attackingWars, attackingNames, attackingIds, attacking_war_morales)
        db.close()
        connection.close()

        return render_template(
        "wars.html", units=units, cId=cId,
        yourCountry=yourCountry, warsCount=warsCount,
        defending=defending, attacking=attacking,
        defender_stats={"supply": 0, "morale": 0},
        attacker_stats={"supply": 0, "morale": 0})

# TODO: put the Peace offers lable under "Internal Affairs" or "Other"
# Peace offers show up here
@app.route("/peace_offers", methods=["POST", "GET"])
@login_required
def peace_offers():
    cId = session["user_id"]
    # cId = 11

    connection = sqlite3.connect("affo/aao.db")
    db = connection.cursor()

    # FETCH PEACE OFFER DATA AND PARSE IT
    peace_offers = db.execute("SELECT peace_offer_id FROM wars WHERE (attacker=(?) OR defender=(?)) AND peace_date IS NULL", (cId, cId)).fetchall()
    offers = {}

    # try:
    if peace_offers:

        for offer in peace_offers:
            offer_id = offer[0]
            if offer_id != None:

                # Every offer has a different subset
                offers[offer_id] = {}

                resources_fetch = db.execute("SELECT demanded_resources FROM peace WHERE id=(?)", (offer_id,)).fetchone()
                author_id = db.execute("SELECT author FROM peace WHERE id=(?)", (offer_id,)).fetchone()[0]

                if resources_fetch:
                    resources = resources_fetch[0]
                    if resources:
                        amounts = db.execute("SELECT demanded_amount FROM peace WHERE id=(?)", (offer_id,)).fetchone()[0].split(",")
                        resources = resources.split(",")

                        offers[offer_id]["resource_count"] = len(resources)
                        offers[offer_id]["resources"] = resources
                        offers[offer_id]["amounts"] = amounts

                        if cId == author_id:
                            offers[offer_id]["owned"] = 1

                    # TODO: make peace at post when clicked
                    # white peace
                    else:
                        offers[offer_id]["peace_type"] = "white"

                    # author_id = db.execute("SELECT author FROM peace WHERE id=(?)", (offer_id,)).fetchone()[0]
                    offers[offer_id]["author"] = [author_id, db.execute("SELECT username FROM users WHERE id=(?)", (author_id,)).fetchone()[0]]

    # except:
        # return "Something went wrong."

    if request.method == "POST":
        offer_id = request.form.get("peace_offer", None)

        # Validate inputs
        try:
            offer_id = int(offer_id)

            # Make sure that others can't accept,delete,etc. the peace offer other than the participants
            check_validity = db.execute("SELECT id FROM wars WHERE (attacker=(?) OR defender=(?)) AND peace_offer_id=(?) AND peace_date IS NULL",
            (cId, cId, offer_id)).fetchone()
            if len(check_validity) != 1:
                raise TypeError

        except:
            return "Peace offer is invalid!"

        decision = request.form.get("decision", None)

        # Offer rejected or revoked
        if decision == "0":
            db.execute("DELETE FROM peace WHERE id=(?)", (offer_id,))
            db.execute("UPDATE wars SET peace_offer_id=NULL WHERE peace_offer_id=(?)", (offer_id,))
            connection.commit()

        elif author_id != cId:

            # Offer accepted
            if decision == "1":
                # TODO: send a message about the decision to the participants
                # maybe do the above using a table created for metadata this way we can also send other message not just the peace offer

                eco = Economy(cId)
                resource_dict = eco.get_particular_resources(resources)

                # TODO: move the below check to the transfer_resources
                # check validity if amount is bigger than available resources
                count = 0
                for value in resource_dict.values():
                    if int(amounts[count]) > value:
                        return "Can't accept peace offer because you don't have the required resources!"

                    eco.transfer_resources(resources[count], int(amounts[count]), author_id)
                    count += 1

                Nation.set_peace(db, connection, None, {"option": "peace_offer_id", "value": offer_id})

            else:
                return "No decision was made."

        else:
            return "You can't accept your own offer."

        return redirect("/peace_offers")

    # TODO: put a button to revoke the peace offer made by the author
    return render_template("peace/peace_offers.html", cId=cId, peace_offers=offers)

@app.route("/send_peace_offer", methods=["GET", "POST"])
@login_required
def send_peace_offer():
    connection = sqlite3.connect("affo/aao.db")
    db = connection.cursor()

    cId = session["user_id"]
    # cId = 11

    if request.method == "GET":
        wars = Nation.get_current_wars(cId)
        enemy = []

        # determine wheter the user is the aggressor or the defender
        for war_id in wars:
            is_attacker = db.execute("SELECT 1 FROM wars WHERE id=(?) AND attacker=(?)", (war_id[0], cId)).fetchone()

            if is_attacker:
                enemy_ = db.execute("SELECT defender FROM wars WHERE id=(?)", (war_id[0],)).fetchone()[0]
            else:
                enemy_ = db.execute("SELECT attacker FROM wars WHERE id=(?)", (war_id[0],)).fetchone()[0]

            enemy.append(db.execute("SELECT username FROM users WHERE id=(?)", (enemy_,)).fetchone()[0])

        return render_template("peace/send_peace_offer.html", enemy=enemy)

    elif request.method == "POST":

        target = request.form.get("enemy")
        resources = request.form.get("resources_send", None)
        resources_amount = request.form.get("resources_amount_send", None)

        # Input validation
        try:
            if not target:
                raise Exception("Target is invalid")

            if resources and resources_amount:
                resources_amount = resources_amount[:-1]
                resources = resources[:-1]

                r = resources.split(",")
                a = resources_amount.split(",")

                for res, amo in zip(r, a):
                    if res not in Economy.resources:
                        raise Exception("Invalid resource")

                    int(amo)

                db.execute("INSERT INTO peace (author,demanded_resources,demanded_amount) VALUES ((?),(?),(?))", (cId, resources, resources_amount))

                enemy_id = db.execute("SELECT id FROM users WHERE username=(?)", (target,)).fetchone()[0]

                war_id = db.execute("SELECT id FROM wars WHERE (attacker=(?) OR defender=(?)) AND (attacker=(?) OR defender=(?)) AND peace_date IS NULL",
                (cId, cId, enemy_id, enemy_id)).fetchone()[0]

                db.execute("UPDATE wars SET peace_offer_id=(?) WHERE id=(?)", (db.lastrowid, war_id))
                connection.commit()

            else:
                raise TypeError
        except:
            return "ERROR"
        else:
            return redirect("/peace_offers")

# page 0, kind of a pseudo page where you can click attack vs special
@app.route("/war/<int:war_id>", methods=["GET"])
@login_required
def war_with_id(war_id):
    connection = sqlite3.connect("affo/aao.db")
    db = connection.cursor()

    # Check if war_exist
    valid_war = db.execute("SELECT * FROM wars WHERE id=(?)",(war_id,)).fetchone()
    if not valid_war:
        return "This war doesen't exist"

    # Check if peace already made
    peace_made = db.execute("SELECT peace_date FROM wars WHERE id=(?)", (war_id,)).fetchone()[0]
    print(peace_made, "THE PEACE MADE")
    if peace_made:
        return "This war already ended"

    update_supply(war_id)


    cId = session["user_id"]

    # defender meaning the one who got declared on
    defender = db.execute("SELECT defender FROM wars WHERE id=(?)", (war_id,)).fetchone()[0]  # this literally raises an error every single time it runs TypeError: 'NoneType' object is not subscriptable
    defender_name = db.execute("SELECT username FROM users WHERE id=(?)", (defender,)).fetchone()[0]

    # # attacker meaning the one who intially declared war, nothing to do with the current user (who is obviously currently attacking)
    attacker = db.execute("SELECT attacker FROM wars WHERE id=(?)", (war_id,)).fetchone()[0]
    attacker_name = db.execute(
        "SELECT username FROM users WHERE id=(?)", (attacker,)).fetchone()[0]

    war_type = db.execute(
        "SELECT war_type FROM wars WHERE id=(?)", (war_id,)).fetchone()[0]
    agressor_message = db.execute(
        "SELECT agressor_message FROM wars WHERE id=(?)", (war_id,)).fetchone()[0]
    if cId == attacker:
        session["enemy_id"] = defender
    else:
        session["enemy_id"] = attacker
    if cId == defender:
        cId_type = "defender"
    elif cId == attacker:
        cId_type = "attacker"
    else:
        cId_type = "spectator"

    if cId_type == "spectator":
        return error(400, "You can't view this war")

    return render_template("war.html", defender=defender, attacker=attacker,
                           attacker_name=attacker_name, defender_name=defender_name, war_type=war_type,
                           agressor_message=agressor_message, cId_type=cId_type)


# the flask route that activates when you click attack on a nation in your wars page.
# check if you have enough supplies.
# page 1: where you can select what units to attack with
@app.route("/warchoose", methods=["GET", "POST"])
@login_required
@check_required
def warChoose():
    cId = session["user_id"]
    # cId = 11

    if request.method == "GET":

        # this is upon first landing on this page after the user clicks attack in wars.html
        normal_units = Military.get_military(cId)
        special_units = Military.get_special(cId)
        units = normal_units.copy()
        units.update(special_units)

        return render_template("warchoose.html", units=units)

    elif request.method == "POST":
        # this post request happens when they click submit, upon which we would redirect to /waramount
        # typical post redirect get pattern means we should do with the request.form.get values here (the 3 units)
        # store the 3 values in session and retrieve it in waramount later

        selected_units = {}

        # If special unit sent
        special_unit = request.form.get("special_unit")
        if special_unit:
            selected_units[special_unit] = 0
            unit_amount = 1

         # If regular units sent
        else:
            selected_units[request.form.get("u1")] = 0
            selected_units[request.form.get("u2")] = 0
            selected_units[request.form.get("u3")] = 0
            unit_amount = 3

        attack_units = Units(cId)

        # Output error if any
        error = attack_units.attach_units(selected_units, unit_amount)
        if error:
            return error

        # cache Unit object reference in session
        session["attack_units"] = attack_units
        return redirect("/waramount")

# page 2 choose how many of each of your units to send
@app.route("/waramount", methods=["GET", "POST"])
@login_required
@check_required
def warAmount():
    cId = session["user_id"]
    # cId = 11

    if request.method == "GET":
        connection = sqlite3.connect("affo/aao.db")
        db = connection.cursor()
        attack_units = session["attack_units"]

        # grab supplies amount
        # if the user is the attacker in the war
        # if cId == db.execute("SELECT attacker FROM wars WHERE ")
        # supplies = db.execute("SELECT attacker_supplies FROM wars WHERE id=(?)", (cId,)).fetchone()[0]

        # find the max amount of units of each of those 3 the user can attack with to send to the waramount page on first load

        unitamounts = Military.get_particular_units_list(cId, attack_units.selected_units_list)
        # turn this dictionary into a list of its values
        connection.commit()
        db.close()
        connection.close()

        # if the user comes to this page by bookmark, it might crash because session["attack_units"] wouldn"t exist

        return render_template("waramount.html", selected_units=attack_units.selected_units_list, unitamounts=unitamounts)

    elif request.method == "POST":

        # Separate object's units list from new units list
        attack_units = session["attack_units"]
        selected_units = attack_units.selected_units_list

        # this is in the form of a dictionary
        selected_units = session["attack_units"].selected_units.copy()

        # 3 units list
        units_name = list(selected_units.keys())

        # check if its 3 regular units or 1 special unit (missile or nuke)
        if len(units_name) == 3:  # this should happen if 3 regular units
            for number in range(1, 4):
                unit_amount = request.form.get(f"u{number}_amount")
                print(unit_amount)
                if not unit_amount:
                    flash("Invalid name argument coming in")
                try:
                    selected_units[units_name[number-1]] = int(unit_amount)
                except:
                    return "Unit amount entered was not a number" # add javascript checks for this in the front end

            # Check every time when user input comes in lest user bypass input validation
            # Error code if any else return None
            error = session["attack_units"].attach_units(selected_units, 3)
            if error:
                return error

            # same note as before as to how to use this request.form.get to get the unit amounts.
            return redirect("/warResult")  # warTarget route is skipped

        elif len(units_name) == 1:  # this should happen if special
            selected_units[units_name[0]] = int(request.form.get("u1_amount"))
            error = session["attack_units"].attach_units(selected_units, 1)
            if error:
                return error

            return redirect("/wartarget")

        else:  # lets just leave this here if something dumb happens, then we can fix it!
            return ("everything just broke")


# This route is only for ICMB or nuke attacks
@app.route("/wartarget", methods=["GET", "POST"])
@login_required
def warTarget():
    cId = session["user_id"]
    eId = session["enemy_id"]

    # DEBUG DATA:
    # cId = 11
    # eId = 10
    # session["attack_units"] = Units(cId, {"nukes": 1}, selected_units_list=["nukes"])

    if request.method == "GET":

        connection = sqlite3.connect("affo/aao.db")
        db = connection.cursor()
        revealed_info = db.execute(
            "SELECT * FROM spyinfo WHERE spyer=(?) AND spyee=(?)", (cId, eId,)).fetchall()
        needed_types = ["soldiers", "tanks", "artillery", "fighters",
                        "bombers", "apaches", "destroyers", "cruisers", "submarines"]

        # cycle through revealed_info. if a value is true, and it"s a unit, add it to the units dictionary
        units = {}
        return render_template("wartarget.html", units=units)

    if request.method == "POST":

        # TODO: check if targeted_unit is send a valid unit type like soldiers and not like sdfsgsdw
        target = request.form.get("targeted_unit")
        target_amount = Military.get_particular_units_list(eId, [target])

        # The attack happens before warResult page rendered
        # Skip attach_units because no need for validation for target_amount since the data coming directly from the db without user affection
        # only validate is targeted_unit is valid
        defender = Units(eId, {target: target_amount[0]}, selected_units_list=[target])
        session["from_wartarget"] = Military.special_fight(session["attack_units"], defender, defender.selected_units_list[0])

        return redirect("warResult")

# page 4 results
# infra damage, building damage
# giant loot, coalition loot, reparation tax set if morale reaches 0
@app.route("/warResult", methods=["GET"])
# @login_required
def warResult():

    # DEBUG DATA:
    # session["attack_units"] = Units(11, {"soldiers": 10, "tanks": 20, "artillery": 20}, selected_units_list=["soldiers", "tanks", "artillery"])
    # eId = 10
    # session["enemy_id"] = eId
    # session["user_id"] = 11

    attacker = session["attack_units"]
    # grab defending enemy units from database
    eId = session["enemy_id"]

    # dev: making sure these values are correct
    # print(attacker.selected_units, "| attack units") # {'soldiers': 0, 'tanks': 0, 'artillery': 0} | attack units
    # print(eId, "| eId") # 10 | eId
    # print(defensestring, "| defense units")  # soldiers,tanks,artillery | defense units

    connection = sqlite3.connect("affo/aao.db")
    db = connection.cursor()

    attacker_name = db.execute("SELECT username FROM users WHERE id=(?)", (session["user_id"],)).fetchone()[0]
    defender_name = db.execute("SELECT username FROM users WHERE id=(?)", (session["enemy_id"],)).fetchone()[0]

    attacker_result = {"nation_name": attacker_name}
    defender_result = {"nation_name": defender_name}

    winner = None

    # If user came from /wartarget only then they have from_wartarget
    result = session.get("from_wartarget", None)
    if not result:
        defensestring = db.execute("SELECT default_defense FROM military WHERE id=(?)", (eId,)).fetchone()[0]  # this is in the form of a string soldiers,tanks,artillery

        defenselst = defensestring.split(",")  # [soldiers, tanks, artillery]
        defenseunits = {}

        for unit in defenselst:
            defenseunits[unit] = db.execute(f"SELECT {unit} FROM military WHERE id={eId}").fetchone()[0]

        defender = Units(eId, defenseunits, selected_units_list=defenselst)
        attacker = session["attack_units"]

        # Save the stats before the fight which used to calculate the lost amount from unit
        prev_defender = dict(defender.selected_units)
        prev_attacker = dict(attacker.selected_units)

        winner, win_condition, infra_damage_effects = Military.fight(attacker, defender)
        defender_result["infra_damage"] = infra_damage_effects

        if winner == defender.user_id:
            winner = defender_name
        else: winner = attacker_name

            # WAR TYPES
            # "raze" --> no loot, no reparation tax, destroy 10x more buildings, destroys money/res
            # "sustained" --> 1x loot, 1x infra destruction, 1x building destroy
            # "loot" --> 2x loot, 0.1x infra destruction, buildings cannot be destroyed
            # war_type = db.execute("SELECT war_type FROM wars WHERE (attacker=(?) OR attacker=(?)) AND (defender=(?) OR defender=(?))", (attacker.user_id, defender.user_id, attacker.user_id, defender.user_id)).fetchall()[-1]
            # if len(war_type) > 0:
            #     if war_type == "raze" : pass
            #     elif war_type == "sustained": pass
            #     elif war_type == "loot": pass
            #     else: print("INVALID WARTYPE")
            # else:
            #     print("INVALID USER IDs")

        defender_loss = {}
        attacker_loss = {}

        for unit in defender.selected_units_list:
            defender_loss[unit] = prev_defender[unit]-defender.selected_units[unit]

        for unit in attacker.selected_units_list:
            attacker_loss[unit] = prev_attacker[unit]-attacker.selected_units[unit]

        defender_result["unit_loss"] = defender_loss
        attacker_result["unit_loss"] = attacker_loss
    else:
        defender_result["unit_loss"] = result[0]
        defender_result["infra_damage"] = result[1]

        # unlink the session values so user can't just reattack when reload or revisit this page
        del session["from_wartarget"]

    # possible war policies:
    # "empire builder"--> winning gives no loot 2x reparation tax
    # "pirate" --> winning gives 2x more loot no reparation tax
    # "tactical" --> winning gives 1x loot 1x reparation tax
    # "pacifist" --> winning gives no loot no reparation tax, lowers project timer by 5 days, boosts your economy by 10%
    # "guerilla": --> winning gives 1x loot no reparation tax, losing makes you lose 40% less loot, and you resist 60% reparation tax.

    # save method only function for the attacker now, and maybe we won't change that
    # saves the decreased supply amount
    attacker.save()

    # unlink the session values so user can't just reattack when reload or revisit this page
    del session["attack_units"]
    del session["enemy_id"]

    return render_template(
        "warResult.html",
        winner=winner,
        defender_result=defender_result,
        attacker_result=attacker_result,
        attackResult="attackResult",
        resStolen="resStolen") # resStolen needs to be a dictionary

# Endpoint for war declaration
@app.route("/declare_war", methods=["POST"])
@login_required
def declare_war():
    connection = sqlite3.connect("affo/aao.db")
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
        # attacker = Nation(11)
        # defender = Nation(10)

        if attacker.id == defender.id:
            return "Can't declare war on yourself"

        already_war_with = db.execute("SELECT attacker, defender FROM wars WHERE (attacker=(?) OR defender=(?)) AND peace_date IS NULL", (attacker.id, attacker.id,)).fetchall()

        if (attacker.id, defender_id,) in already_war_with or (defender_id, attacker.id) in already_war_with:
            return "You already fight against..."

        # Check province difference
        attacker_provinces = attacker.get_provinces()["provinces_number"]
        defender_provinces = defender.get_provinces()["provinces_number"]

        if (attacker_provinces - defender_provinces > 1):
            return "That country has too few provinces for you! You can only declare war on countries within 3 provinces more or 1 less province than you."
        if (defender_provinces - attacker_provinces > 3):
            return "That country has too many provinces for you! You can only declare war on countries within 3 provinces more or 1 less province than you."

        # Check if nation currently at peace with another nation
        current_peace = db.execute("SELECT max(peace_date) FROM wars WHERE (attacker=(?) OR defender=(?)) AND (attacker=(?) OR defender=(?))", (attacker.id, attacker.id, defender_id, defender_id)).fetchone()

        # 259200 = 3 days
        if current_peace[0]:
            if (current_peace[0]+259200) > time.time():
                return "You can't declare war because truce has not expired!"

    except Exception as e:
        print("RUNN")
        print(e)

        # Redirects the user to an error page
        return error(400, "No such country")

    start_dates = time.time()
    db.execute("INSERT INTO wars (attacker, defender, war_type, agressor_message, start_date, last_visited) VALUES (?, ?, ?, ?, ?, ?)",
               (attacker.id, defender_id, war_type, war_message, start_dates, start_dates))
    connection.commit()
    connection.close()

    return redirect("/wars")

# this should go to countries with a specific URL influence arguments set up by taking the user's influence and putting in the lower and upper bounds.
@app.route("/find_targets", methods=["GET"])
@login_required
def find_targets():
    if request.method == "GET":
        connection = sqlite3.connect("affo/aao.db")
        db = connection.cursor()
        cId = session["user_id"]
        influence = get_influence(cId)
        upper = influence * 2
        lower = influence * 0.9
        return redirect(f"/countries?lowerinf={lower}&upperinf={upper}")
        # return redirect(f"/countries/search?=upperinf={upper}&lowerinf={lower}")

    # if request.method == "GET":
    #     return render_template("find_targets.html")
    # else:
    #     # TODO: maybe delete the sql fetch and create a centralized way to fetch it
    #     connection = sqlite3.connect("affo/aao.db")
    #     db = connection.cursor()

    #     defender = request.form.get("defender")
    #     defender_id = db.execute("SELECT id FROM users WHERE username=(?)", (defender,)).fetchone()
    #     if defender_id:
    #         return redirect(f"/country/id={defender_id[0]}")
    #     else:
    #         return error(400, "No such country")


# if everything went through, remove the cost of supplies from the amount of supplies the country has.


@app.route("/defense", methods=["GET", "POST"])
@login_required
def defense():
    cId = session["user_id"]
    units = Military.get_military(cId) # returns dictionary {'soldiers': 1000}

    if request.method == "GET":
        return render_template("defense.html", units=units)

    elif request.method == "POST":
        connection = sqlite3.connect("affo/aao.db")
        db = connection.cursor()
        nation = db.execute("SELECT * FROM nation WHERE nation_id=(?)", (cId,)).fetchone()

        # Defense units came from POST request (TODO: attach it to the frontend)
        defense_units = ["soldier", "tank", "apache"]
        # defense_units = [request.form.get(u1), request.form.get(u2), request.form.get(u3)]
        # Default defense
        # nation_id = nation[1]
        # default_defense = nation[2]

        if nation:
            for item in defense_units:
                if item not in Military.allUnits:
                    return "Invalid unit types!"
            if len(defense_units) == 3:
                # default_defense is stored in the db: "unit1,unit2,unit3"
                defense_units = ",".join(defense_units)
                db.execute(
                    "UPDATE nation SET default_defense=(?) WHERE nation_id=(?)", (defense_units, nation[1]))
                connection.commit()
            else:
                return "Invalid number of units selected!"
        else:
            return "Nation is not created!"

        # should be a back button on this page to go back to wars so dw about some infinite loop
        # next we need to insert the 3 defending units set as a value to the nation"s table property (one in each war): defense
        # db.execute("INSERT INTO wars (attacker, defender) VALUES (?, ?)", (cId, defender_id))
        connection.close()

        return render_template("defense.html", units=units)
