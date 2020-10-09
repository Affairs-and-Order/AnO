from flask import Flask, request, render_template, session, redirect, flash
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
import datetime
import _pickle as pickle
import random
from celery import Celery
from helpers import login_required, error
import sqlite3
# from celery.schedules import crontab # arent currently using but will be later on
from helpers import get_influence, get_coalition_influence
# Game.ping() # temporarily removed this line because it might make celery not work
from app import app
import os


# rawCol (for easy finding using CTRL + F)
@login_required
@app.route("/coalition/<colId>", methods=["GET"])
def coalition(colId):

    if request.method == "GET":

        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        cId = session["user_id"]

        name = db.execute("SELECT name FROM colNames WHERE id=(?)", (colId,)).fetchone()[0]
        colType = db.execute("SELECT type FROM colNames WHERE id=(?)", (colId,)).fetchone()[0]
        members = db.execute("SELECT COUNT(userId) FROM coalitions WHERE colId=(?)", (colId,)).fetchone()[0]
        total_influence = get_coalition_influence(colId)
        average_influence = total_influence // members

        # names = db.execute("SELECT username FROM users WHERE id = (SELECT userId FROM coalitions WHERE colId=(?))", (session["user_id"], )).fetchall()

        leader = db.execute("SELECT leader FROM colNames WHERE id=(?)", (colId,)).fetchone()[0]  # The id of the coalition leader
        leaderName = db.execute("SELECT username FROM users WHERE id=(?)", (leader,)).fetchone()[0]

        ############## TREATIES ##################

        #### INGOING ####
        ingoing_ids = db.execute("SELECT id FROM treaties WHERE col2_id=(?) AND status='Pending' ORDER BY treaty_id ASC", (colId,)).fetchall()
        col_ids = []
        col_names = []
        trt_names = []

        for treaty_idd in ingoing_ids:

            treaty_id = treaty_idd[0]

            col_id = db.execute("SELECT col1_id FROM treaties WHERE treaty_id=(?)", (treaty_id,)).fetchone()[0]
            col_ids.append(col_id)

            coalition_name = db.execute("SELECT name FROM colNames WHERE id=(?)", (col_id,)).fetchone()[0]
            col_names.append(coalition_name)

            treaty_name = db.execute("SELECT title FROM treaty_ids WHERE treaty_id=(SELECT treaty_id FROM treaties WHERE id=(?))", (treaty_id,)).fetchone()[0]
            trt_names.append(treaty_name)

        ingoing_treaties = zip(ingoing_ids, col_ids, col_names, trt_names)
        #################

        #### ACTIVE ####

        active_ids = db.execute(
        """SELECT id FROM treaties WHERE col2_id=(?) OR col1_id=(?) AND status='Active' ORDER BY treaty_id ASC""",
        (colId, colId)).fetchall()

        active_ids = []
        coalition_ids = []
        coalition_names = []
        treaty_names = []

        for treaty_idd in active_ids:
            offer_id = treaty_idd[0]

            active_ids.append(offer_id)

            coalition_id = db.execute("SELECT col1_id FROM treaties WHERE id=(?)", (offer_id,)).fetchone()[0]
            if coalition_id != colId:
                pass
            else: 
                coalition_id = db.execute("SELECT col2_id FROM treaties WHERE id=(?)", (offer_id,)).fetchone()[0]

            coalition_ids.append(coalition_id)
            
            coalition_name = db.execute("SELECT name FROM colNames WHERE id=(?)", (coalition_id,)).fetchone()[0]
            coalition_names.append(coalition_name)

            treaty_name = db.execute("SELECT title FROM treaty_ids WHERE treaty_id=(SELECT treaty_id FROM treaties WHERE id=(?))", (offer_id,)).fetchone()[0]
            treaty_names.append(treaty_name)

        active_treaties = zip(coalition_ids, coalition_names, treaty_names, active_ids)


        ################


        ############################################

        ### FLAG STUFF
        try:
            flag = db.execute("SELECT flag FROM colNames WHERE id=(?)", (colId,)).fetchone()[0]
        except TypeError:
            flag = None
        ### 


        requestMessages = db.execute("SELECT message FROM requests WHERE colId=(?)", (colId,)).fetchall()
        requestIds = db.execute("SELECT reqId FROM requests WHERE colId=(?)", (colId,)).fetchall()
        requestNames = db.execute("SELECT username FROM users WHERE id=(SELECT reqId FROM requests WHERE colId=(?))", (colId,)).fetchall()

        requests = zip(requestIds, requestNames, requestMessages)

        description = db.execute("SELECT description FROM colNames WHERE id=(?)", (colId,)).fetchone()[0]

        colType = db.execute("SELECT type FROM colNames WHERE id=(?)", (colId,)).fetchone()[0]

        ### STUFF FOR JINJA
        try:
            userInCol = db.execute("SELECT userId FROM coalitions WHERE userId=(?)", (cId,)).fetchone()[0]
            userInCol = True
        except:
            userInCol = False

        try:
            userInCurCol = db.execute("SELECT userId FROM coalitions WHERE userId=(?) AND colId=(?)", (cId, colId)).fetchone()[0]
            userInCurCol = True
        except:
            userInCurCol = False

        if leader == cId:
            userLeader = True
        else:
            userLeader = False
        ###

        ### BANK STUFF
        if userLeader == True:

            bankRequests = db.execute("SELECT reqId, amount, resource, id FROM colBanksRequests WHERE colId=(?)", (colId,)).fetchall()

            banks = []
            for reqId, amount, resource, bankId in bankRequests:
                username = db.execute("SELECT username FROM users WHERE id=(?)", (reqId,)).fetchone()[0]
                data_tuple = (reqId, amount, resource, bankId, username)
                banks.append(data_tuple)

            bankRequests = banks
        else:
            bankRequests = []
        ### 

        connection.close()

        return render_template("coalition.html", name=name, colId=colId, members=members,
                               description=description, colType=colType, userInCol=userInCol, userLeader=userLeader,
                               requests=requests, userInCurCol=userInCurCol, ingoing_treaties=ingoing_treaties, total_influence=total_influence,
                               average_influence=average_influence, leaderName=leaderName, leader=leader,
                               flag=flag, bankRequests=bankRequests, active_treaties=active_treaties)


@login_required
@app.route("/establish_coalition", methods=["GET", "POST"])
def establish_coalition():
    if request.method == "POST":
        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        try:
            db.execute("SELECT userId FROM coalitions WHERE userId=(?)",
                       (session["user_id"],)).fetchone()[0]
            return error(403, "You are already in a coalition")
        except:

            cType = request.form.get("type")
            name = request.form.get("name")
            desc = request.form.get("description")

            if len(str(name)) > 15:
                return error(500, "name too long! the coalition name needs to be under 15 characters")
                # TODO add a better error message that renders inside the establish_coalition page
            else:
                # TODO gives a key error, look into this
                db.execute("INSERT INTO colNames (name, leader, type, description) VALUES (?, ?, ?, ?)",
                           (name, session["user_id"], cType, desc))
                colId = db.execute("SELECT id FROM colNames WHERE name = (?)", (name,)).fetchone()[0]
                db.execute("INSERT INTO coalitions (colId, userId) VALUES (?, ?)", (colId, session["user_id"],))
                db.execute("INSERT INTO colBanks (colId) VALUES (?)", (colId,))

                connection.commit()
                connection.close()
                return redirect(f"/coalition/{colId}")
    else:
        return render_template("establish_coalition.html")

        
@login_required
@app.route("/coalitions", methods=["GET"])
def coalitions():

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()

    try:
        search = request.values.get("search")
    except TypeError:
        search = None

    if search == None or search == "":
        coalitions = db.execute("SELECT id FROM colNames").fetchall()
    else:
        coalitions = db.execute("SELECT id FROM colNames WHERE name=(?)", (search,)).fetchall()

    names = []
    ids = []
    members = []
    types = []
    influences = []

    for i in coalitions:

        ids.append(i[0])

        idd = str(i[0])

        colType = db.execute(
            "SELECT type FROM colNames WHERE id=(?)", (idd,)).fetchone()[0]
        types.append(colType)

        colName = db.execute(
            "SELECT name FROM colNames WHERE id=(?)", (idd,)).fetchone()[0]
        names.append(colName)

        colMembers = db.execute(
            "SELECT count(userId) FROM coalitions WHERE colId=(?)", (idd,)).fetchone()[0]
        members.append(colMembers)

        influence = get_coalition_influence(idd)
        influences.append(influence)

    connection.close()

    resultAll = zip(names, ids, members, types, influences)

    return render_template("coalitions.html", resultAll=resultAll)

@login_required
@app.route("/join/<colId>", methods=["POST"])
def join_col(colId):

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()

    cId = session["user_id"]

    colType = db.execute(
        "SELECT type FROM colNames WHERE id = (?)", (colId,)).fetchone()[0]

    if colType == "Open":

        db.execute(
            "INSERT INTO coalitions (colId, userId) VALUES (?, ?)", (colId, cId))

        connection.commit()

    else:

        message = request.form.get("message")

        db.execute(
            "INSERT INTO requests (colId, reqId, message ) VALUES (?, ?, ?)", (colId, cId, message))

        connection.commit()

    connection.close()

    return redirect(f"/coalition/{colId}")


@login_required
@app.route("/leave/<colId>", methods=["POST"])
def leave_col(colId):

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()

    cId = session["user_id"]

    leader = db.execute("SELECT leader FROM colNames WHERE id=(?)", (colId,)).fetchone()[0]

    if cId == leader:
        error(400, "Can't leave coalition, you're the leader")

    db.execute("DELETE FROM coalitions WHERE userId=(?) AND colId=(?)", (cId, colId))

    connection.commit()
    connection.close()

    return redirect("/coalitions")


@login_required
@app.route("/my_coalition", methods=["GET"])
def my_coalition():

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()
    cId = session["user_id"]

    try:
        coalition = db.execute(
            "SELECT colId FROM coalitions WHERE userId=(?)", (cId,)).fetchone()[0]
    except TypeError:
        coalition = None

    connection.close()

    if coalition == None:
        return redirect("/")  # Redirects to home page instead of an error
    else:
        return redirect(f"/coalition/{coalition}")


@login_required
@app.route("/add/<uId>", methods=["POST"])
def adding(uId):

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()

    try:
        colId = db.execute("SELECT colId FROM requests WHERE reqId=(?)", (uId,)).fetchone()[0]
    except TypeError:
        return error(400, "User hasn't posted a request to join")

    cId = session["user_id"]

    leader = db.execute("SELECT leader FROM colNames WHERE id=(?)", (colId,)).fetchone()[0]

    if leader != cId:
        return error(400, "You are not the leader of the coalition")

    db.execute("DELETE FROM requests WHERE reqId=(?) AND colId=(?)", (uId, colId))
    db.execute("INSERT INTO coalitions (colId, userId) VALUES (?, ?)", (colId, uId))

    connection.commit()
    connection.close()

    return redirect(f"/coalition/{colId}")


@login_required
# removes a request for coalition joining
@app.route("/remove/<uId>", methods=["POST"])
def removing_requests(uId):

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()

    try:
        colId = db.execute(
            "SELECT colId FROM requests WHERE reqId=(?)", (uId,)).fetchone()[0]
    except TypeError:
        return error(400, "User hasn't posted a request to join this coalition.")

    cId = session["user_id"]

    leader = db.execute(
        "SELECT leader FROM colNames WHERE id=(?)", (colId,)).fetchone()[0]

    if leader != cId:

        return error(400, "You are not the leader of the coalition")

    db.execute("DELETE FROM requests WHERE reqId=(?) AND colId=(?)", (uId, colId))
    connection.commit()

    return redirect(f"/coalition/{ colId }")

@login_required
@app.route("/delete_coalition/<colId>", methods=["POST"])
def delete_coalition(colId):

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()

    cId = session["user_id"]

    leader = db.execute("SELECT leader FROM colNames WHERE id=(?)", (colId,)).fetchone()[0]

    if leader != cId:
        return error(400, "You aren't the leader of this coalition")

    coalition_name = db.execute("SELECT name FROM colNames WHERE id=(?)", (colId,)).fetchone()[0]

    db.execute("DELETE FROM colNames WHERE id=(?)", (colId,))

    db.execute("DELETE FROM coalitions WHERE colId=(?)", (colId,))
    
    connection.commit()
    connection.close()

    flash(f"{coalition_name} coalition was deleted.")

    return redirect("/")



@login_required
@app.route("/update_col_info/<colId>", methods=["POST"])
def update_col_info(colId):

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()

    cId = session["user_id"]

    leader = db.execute("SELECT leader FROM colNames WHERE id=(?)", (colId,)).fetchone()[0]

    if leader != cId:
        return error(400, "You aren't the leader of this coalition")

    ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    file = request.files["flag_input"]
    if file and allowed_file(file.filename):

        # Check if the user already has a flag
        try:
            current_flag = db.execute("SELECT flag FROM colNames WHERE id=(?)", (colId,)).fetchone()[0]

            # If he does, delete the flag
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], current_flag))
            db.execute("UPDATE colNames SET flag=null WHERE id=(?)", (colId,))
        except TypeError:
            pass

        # Save the file
        current_filename = file.filename
        extension = current_filename.rsplit('.', 1)[1].lower()
        filename = f"col_flag_{colId}" + '.' + extension
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        db.execute("UPDATE colNames SET flag=(?) WHERE id=(?)", (filename, colId))

    connection.commit()
    connection.close()

    return redirect(f"/coalition/{colId}")

### COALITION BANK STUFF ###
@login_required
@app.route("/deposit_into_bank/<colId>", methods=["POST"])
def deposit_into_bank(colId):

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()

    cId = session["user_id"]

    try:
        db.execute("SELECT userId FROM coalitions WHERE userId=(?) and colId=(?)", (cId, colId)).fetchone()[0]
    except TypeError:
        return redirect(400, "You aren't in this coalition")

    resources = [
                "money", "rations", "oil", "coal", "uranium", "bauxite", "lead", "copper", "iron",
                "lumber", "components", "steel", "consumer_goods", "aluminium",
                "gasoline", "ammunition"]

    deposited_resources = []

    for res in resources:
        resource = request.form.get(res)
        if resource != "":
            res_tuple = (res, int(resource))
            deposited_resources.append(res_tuple)

    def deposit(resource, amount):

        # Removes the resource from the giver

        # If the resource is money, removes the money from the seller
        if resource == "money":

            current_money = int(db.execute("SELECT gold FROM stats WHERE id=(?)", (cId,)).fetchone()[0])

            if current_money < amount:
                return error(400, "You don't have enough money")

            new_money = current_money - amount

            db.execute("UPDATE stats SET gold=(?) WHERE id=(?)", (new_money, cId))

        # If it isn't, removes the resource from the giver
        else:

            current_resource_statement = f"SELECT {resource} FROM resources WHERE id=(?)"
            current_resource = int(db.execute(current_resource_statement, (cId,)).fetchone()[0])

            if current_resource < amount:
                return error(400, f"You don't have enough {resource}")

            new_resource = current_resource - amount

            update_statement = f"UPDATE resources SET {resource}=(?) WHERE id=(?)"
            db.execute(update_statement, (new_resource, cId))

        # Gives the coalition the resource
        current_resource_statement = f"SELECT {resource} FROM colBanks WHERE colId=(?)"
        current_resource = int(db.execute(current_resource_statement, (colId,)).fetchone()[0])

        new_resource = current_resource + amount

        update_statement = f"UPDATE colBanks SET {resource}=(?) WHERE colId=(?)"
        db.execute(update_statement, (new_resource, colId))

    for resource in deposited_resources:
        name = resource[0]
        amount = resource[1]
        deposit(name, amount)

    connection.commit()
    connection.close()

    return redirect(f"/coalition/{colId}")

def withdraw(resource, amount, user_id, colId):

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()

    # Removes the resource from the coalition bank

    current_resource_statement = f"SELECT {resource} FROM colBanks WHERE colId=(?)"
    current_resource = int(db.execute(current_resource_statement, (colId,)).fetchone()[0])

    if current_resource < amount:
        return error(400, f"Your coalition doesn't have enough {resource}")

    new_resource = current_resource - amount

    update_statement = f"UPDATE colBanks SET {resource}=(?) WHERE colId=(?)"
    db.execute(update_statement, (new_resource, colId))

    # Gives the leader his resource
    # If the resource is money, gives him money
    if resource == "money":

        current_money = int(db.execute("SELECT gold FROM stats WHERE id=(?)", (user_id,)).fetchone()[0])

        new_money = current_money + amount

        db.execute("UPDATE stats SET gold=(?) WHERE id=(?)", (new_money, user_id))

    # If the resource is not money, gives him that resource
    else:

        current_resource_statement = f"SELECT {resource} FROM resources WHERE id=(?)"
        current_resource = int(db.execute(current_resource_statement, (user_id,)).fetchone()[0])

        new_resource = current_resource + amount

        update_statement = f"UPDATE resources SET {resource}=(?) WHERE id=(?)"
        db.execute(update_statement, (new_resource, user_id))

    connection.commit()
    connection.close()

@login_required
@app.route("/withdraw_from_bank/<colId>", methods=["POST"])
def withdraw_from_bank(colId):

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()

    cId = session["user_id"]

    try:
        db.execute("SELECT leader FROM colNames WHERE leader=(?) and id=(?)", (cId, colId))
    except TypeError:
        return error(400, "You aren't the leader of this coalition")

    resources = [
        "money", "rations", "oil", "coal", "uranium", "bauxite", "lead", "copper", "iron",
        "lumber", "components", "steel", "consumer_goods", "aluminium",
        "gasoline", "ammunition"
    ]

    withdrew_resources = []

    for res in resources:
        resource = request.form.get(res)
        if resource != "":
            res_tuple = (res, int(resource))
            withdrew_resources.append(res_tuple)

    for resource in withdrew_resources:
        name = resource[0]
        amount = resource[1]
        withdraw(name, amount, cId, colId)

    connection.commit()
    connection.close()

    return redirect(f"/coalition/{colId}")

@login_required
@app.route("/request_from_bank/<colId>", methods=["POST"])
def request_from_bank(colId):

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()

    cId = session["user_id"]

    try:
        db.execute("SELECT userId FROM coalitions WHERE userId=(?) and colId=(?)", (cId, colId)).fetchone()[0]
    except TypeError:
        return redirect(400, "You aren't in this coalition")

    resources = [
                "money", "rations", "oil", "coal", "uranium", "bauxite", "lead", "copper", "iron",
                "lumber", "components", "steel", "consumer_goods", "aluminium",
                "gasoline", "ammunition"
    ]

    requested_resources = []

    for res in resources:
        resource = request.form.get(res)
        if resource != "":
            res_tuple = (res, int(resource))
            requested_resources.append(res_tuple)

    if len(requested_resources) > 1:
        return error(400, "You can only request one resource at a time")

    requested_resources = tuple(requested_resources[0])

    db.execute("INSERT INTO colBanksRequests (reqId, colId, amount, resource) VALUES (?, ?, ?, ?)", 
    (cId, colId, requested_resources[1], requested_resources[0]))

    connection.commit()
    connection.close()

    return redirect(f"/coalition/{colId}")

@login_required
@app.route("/remove_bank_request/<bankId>", methods=["POST"])
def remove_bank_request(bankId):

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()

    cId = session["user_id"]

    colId = db.execute("SELECT colId FROM colBanksRequests WHERE id=(?)", (bankId,)).fetchone()[0]

    try:
        db.execute("SELECT leader FROM colNames WHERE leader=(?) and id=(?)", (cId, colId))
    except TypeError:
        return error(400, "You aren't the leader of this coalition")

    db.execute("DELETE FROM colBanksRequests WHERE id=(?)", (bankId,))

    connection.commit()
    connection.close()
    return redirect("/my_coalition")

@login_required
@app.route("/accept_bank_request/<bankId>", methods=["POST"])
def accept_bank_request(bankId):

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()

    cId = session["user_id"]

    colId = db.execute("SELECT colId FROM colBanksRequests WHERE id=(?)", (bankId,)).fetchone()[0]

    try:
        db.execute("SELECT leader FROM colNames WHERE leader=(?) and id=(?)", (cId, colId))
    except TypeError:
        return error(400, "You aren't the leader of this coalition")

    resource = db.execute("SELECT resource FROM colBanksRequests WHERE id=(?)", (bankId,)).fetchone()[0]
    amount = db.execute("SELECT amount FROM colBanksRequests WHERE id=(?)", (bankId,)).fetchone()[0]
    user_id = db.execute("SELECT reqId FROM colBanksRequests WHERE id=(?)", (bankId,)).fetchone()[0]

    withdraw(resource, amount, user_id, colId)

    db.execute("DELETE FROM colBanksRequests WHERE id=(?)", (bankId,))
    
    connection.commit()
    connection.close()

    return redirect("/my_coalition")

@login_required
@app.route("/offer_treaty", methods=["POST"])
def offer_treaty():

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()

    cId = session["user_id"]

    col2_name = request.form.get("coalition_name")
    col2_id = db.execute("SELECT id FROM colNames WHERE name=(?)", (col2_name,)).fetchone()[0]

    user_coalition = db.execute("SELECT colId FROM coalitions WHERE userId=(?)", (cId,)).fetchone()[0]

    coalition_leader = db.execute("SELECT leader FROM colNames WHERE id=(?)", (user_coalition,)).fetchone()[0]

    if str(cId) != coalition_leader:
        error(400, "You aren't the leader of your coalition.")

    treaty_name = request.form.get("treaty_name")
    treaty_id = db.execute("SELECT treaty_id FROM treaty_ids WHERE title=(?)", (treaty_name,)).fetchone()[0]

    db.execute("INSERT INTO treaties (col1_id, col2_id, treaty_id) VALUES (?, ?, ?)", (user_coalition, col2_id, treaty_id))

    connection.commit()
    connection.close()

    return redirect("/my_coalition")

@login_required
@app.route("/accept_treaty/<offer_id>", methods=["POST"])
def accept_treaty(offer_id):

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()

    cId = session["user_id"]

    user_coalition = db.execute("SELECT colId FROM coalitions WHERE userId=(?)", (cId,)).fetchone()[0]

    coalition_leader = db.execute("SELECT leader FROM colNames WHERE id=(?)", (user_coalition,)).fetchone()[0]

    if str(cId) != coalition_leader:
        error(400, "You aren't the leader of your coalition.")

    db.execute("UPDATE treaties SET status='Active' WHERE id=(?)", (offer_id,))

    connection.commit()
    connection.close()

    return redirect("/my_coalition")