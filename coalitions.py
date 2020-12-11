# ALL CONVERTED

from flask import Flask, request, render_template, session, redirect, flash
from tempfile import mkdtemp
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
import datetime
import _pickle as pickle
import random
from celery import Celery
from helpers import login_required, error
import psycopg2
# from celery.schedules import crontab # arent currently using but will be later on
from helpers import get_influence, get_coalition_influence
# Game.ping() # temporarily removed this line because it might make celery not work
from app import app
import os
from dotenv import load_dotenv
load_dotenv()


# Function for getting the coalition role of a user
def get_user_role(user_id):

    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()
    
    db.execute("SELECT role FROM coalitions WHERE userId=%s", (user_id,))
    role = db.fetchone()[0]

    return role

# Route for viewing a coalition's page
@login_required
@app.route("/coalition/<colId>", methods=["GET"])
def coalition(colId):

    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    cId = session["user_id"]

    db.execute("SELECT name FROM colNames WHERE id=(%s)", (colId,))
    name = db.fetchone()[0]

    db.execute("SELECT type FROM colNames WHERE id=(%s)", (colId,))
    colType = db.fetchone()[0]

    db.execute("SELECT COUNT(userId) FROM coalitions WHERE colId=(%s)", (colId,))
    members = db.fetchone()[0]

    total_influence = get_coalition_influence(colId)

    average_influence = total_influence // members

    db.execute("SELECT description FROM colNames WHERE id=(%s)", (colId,))
    description = db.fetchone()[0]

    db.execute("SELECT type FROM colNames WHERE id=(%s)", (colId,))
    colType = db.fetchone()[0]

    db.execute("SELECT userId FROM coalitions WHERE role='leader' AND colId=(%s)", (colId,))
    leaders = db.fetchall() # All coalition leaders ids
    leaders = [item for t in leaders for item in t]

    leader_names = []

    for leader_id in leaders:
        db.execute("SELECT username FROM users WHERE id=%s", (leader_id,))
        leader_name = db.fetchone()[0]
        leader_names.append(leader_name)

    ### STUFF FOR JINJA
    try:
        db.execute("SELECT userId FROM coalitions WHERE userId=(%s)", (cId,))
        userInCol = db.fetchone()[0]
        userInCol = True
    except:
        userInCol = False

    try:
        db.execute("SELECT userId FROM coalitions WHERE userId=(%s) AND colId=(%s)", (cId, colId))
        userInCurCol = db.fetchone()[0]
        userInCurCol = True
    except:
        userInCurCol = False

    user_role = get_user_role(cId)

    if cId in leaders:
        userLeader = True
    else:
        userLeader = False
    ###

    ############## TREATIES ##################
    if userLeader:

        #### INGOING ####
        db.execute("SELECT id FROM treaties WHERE col2_id=(%s) AND status='Pending' ORDER BY treaty_id ASC", (colId,))
        ingoing_ids = db.fetchall()
        col_ids = []
        col_names = []
        trt_names = []

        for treaty_iddd in ingoing_ids:

            treaty_id = treaty_iddd[0]

            db.execute("SELECT col1_id FROM treaties WHERE id=(%s)", (treaty_id,))
            col_id = db.fetchone()[0]
            col_ids.append(col_id)

            db.execute("SELECT name FROM colNames WHERE id=(%s)", (col_id,))
            coalition_name = db.fetchone()[0]
            col_names.append(coalition_name)

            db.execute("SELECT title FROM treaty_ids WHERE treaty_id=(SELECT treaty_id FROM treaties WHERE id=(%s))", (treaty_id,))
            treaty_name = db.fetchone()[0]
            trt_names.append(treaty_name)

        ingoing_treaties = zip(ingoing_ids, col_ids, col_names, trt_names)
        ingoing_length = len(list(ingoing_treaties))
        #################

        #### ACTIVE ####

        
        db.execute("SELECT id FROM treaties WHERE col2_id=(%s) AND status='Active' OR col1_id=(%s) ORDER BY treaty_id ASC", (colId, colId))
        raw_active_ids = db.fetchall()

        active_ids = []
        coalition_ids = []
        coalition_names = []
        treaty_names = []


        for i in raw_active_ids:

            offer_id = i[0]

            active_ids.append(offer_id)

            db.execute("SELECT col1_id FROM treaties WHERE id=(%s)", (offer_id,))
            coalition_id = db.fetchone()[0]
            if coalition_id != colId:
                pass
            else: 
                db.execute("SELECT col2_id FROM treaties WHERE id=(%s)", (offer_id,))
                coalition_id = db.fetchone()[0]

            coalition_ids.append(coalition_id)
            
            db.execute("SELECT name FROM colNames WHERE id=(%s)", (coalition_id,))
            coalition_name = db.fetchone()[0]
            coalition_names.append(coalition_name)

            db.execute("SELECT title FROM treaty_ids WHERE treaty_id=(SELECT treaty_id FROM treaties WHERE id=(%s))", (offer_id,))
            treaty_name = db.fetchone()[0]
            treaty_names.append(treaty_name)

        active_treaties = zip(coalition_ids, coalition_names, treaty_names, active_ids)
        active_length = len(list(active_treaties))
    else:
        ingoing_treaties = []
        active_treaties = []
        ingoing_length = None
        active_length = None
        ################
    ############################################

    ### BANK STUFF ###
    if userInCurCol:

        db.execute("SELECT money FROM colBanks WHERE colId=(%s)", (colId,))
        money = db.fetchone()[0]

        db.execute("SELECT rations FROM colBanks WHERE colId=(%s)", (colId,))
        rations =  db.fetchone()[0]
        db.execute("SELECT oil FROM colBanks WHERE colId=(%s)", (colId,))
        oil =  db.fetchone()[0]
        db.execute("SELECT coal FROM colBanks WHERE colId=(%s)", (colId,))
        coal =  db.fetchone()[0]
        db.execute("SELECT uranium FROM colBanks WHERE colId=(%s)", (colId,))
        uranium =  db.fetchone()[0]
        db.execute("SELECT bauxite FROM colBanks WHERE colId=(%s)", (colId,))
        bauxite = db.fetchone()[0]
        db.execute("SELECT iron FROM colBanks WHERE colId=(%s)", (colId,))
        iron = db.fetchone()[0]
        db.execute("SELECT lead FROM colBanks WHERE colId=(%s)", (colId,))
        lead =  db.fetchone()[0]
        db.execute("SELECT copper FROM colBanks WHERE colId=(%s)", (colId,))
        copper = db.fetchone()[0]
        db.execute("SELECT lumber FROM colBanks WHERE colId=(%s)", (colId,))
        lumber = db.fetchone()[0]

        db.execute("SELECT components FROM colBanks WHERE colId=(%s)", (colId,))
        components =  db.fetchone()[0]
        db.execute("SELECT steel FROM colBanks WHERE colId=(%s)", (colId,))
        steel =  db.fetchone()[0]
        db.execute("SELECT consumer_goods FROM colBanks WHERE colId=(%s)", (colId,))
        consumer_goods = db.fetchone()[0]
        db.execute("SELECT aluminium FROM colBanks WHERE colId=(%s)", (colId,))
        aluminium = db.fetchone()[0]
        db.execute("SELECT gasoline FROM colBanks WHERE colId=(%s)", (colId,))
        gasoline = db.fetchone()[0]
        db.execute("SELECT ammunition FROM colBanks WHERE colId=(%s)", (colId,))
        ammunition = db.fetchone()[0]

        bankRaw = {
            'money': money,
            'rations': rations,
            'oil': oil,
            'coal': coal,
            'uranium': uranium,
            'bauxite': bauxite,
            'iron': iron,
            'copper': copper,
            'lead': lead,
            'lumber': lumber,
            'components': components,
            'steel': steel,
            'consumer_goods': consumer_goods,
            'aluminium': aluminium,
            'gasoline': gasoline,
            'ammunition': ammunition
        }

    else: 
        
        bankRaw = {}
    ###################

    ### FLAG STUFF
    try:
        db.execute("SELECT flag FROM colNames WHERE id=(%s)", (colId,))
        flag = db.fetchone()[0]
    except:
        flag = None
    ### 

    if userLeader and colType != "Open":

        db.execute("SELECT message FROM requests WHERE colId=(%s)", (colId,))
        requestMessages = db.fetchall()

        db.execute("SELECT reqId FROM requests WHERE colId=(%s)", (colId,))
        requestIds = db.fetchall()

        db.execute("SELECT username FROM users WHERE id=(SELECT reqId FROM requests WHERE colId=(%s))", (colId,))
        requestNames = db.fetchall()

        requests = zip(requestIds, requestNames, requestMessages)
    else:
        requests = None

    ### BANK STUFF
    if userLeader:

        db.execute("SELECT reqId, amount, resource, id FROM colBanksRequests WHERE colId=(%s)", (colId,))
        bankRequests = db.fetchall()

        banks = []
        for reqId, amount, resource, bankId in bankRequests:

            db.execute("SELECT username FROM users WHERE id=(%s)", (reqId,))
            username = db.fetchone()[0]

            data_tuple = (reqId, amount, resource, bankId, username)
            banks.append(data_tuple)

        bankRequests = banks
    else:
        bankRequests = []

    connection.close()

    return render_template("coalition.html", name=name, colId=colId, members=members, user_role=user_role,
                            description=description, colType=colType, userInCol=userInCol, userLeader=userLeader,
                            requests=requests, userInCurCol=userInCurCol, ingoing_treaties=ingoing_treaties, total_influence=total_influence,
                            average_influence=average_influence, leaderNames=leader_names, leaders=leaders,
                            flag=flag, bankRequests=bankRequests, active_treaties=active_treaties, bankRaw=bankRaw,
                            ingoing_length=ingoing_length, active_length=active_length)


# Route for establishing a coalition
@login_required
@app.route("/establish_coalition", methods=["GET", "POST"])
def establish_coalition():

    if request.method == "POST":
        
        connection = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"))

        db = connection.cursor()

        # Checks if a user is already in a coalition
        try:
            db.execute("SELECT userId FROM coalitions WHERE userId=(%s)", (session["user_id"],))
            db.fetchone()[0]

            return error(403, "You are already in a coalition")
        except:
            pass

        cType = request.form.get("type")
        name = request.form.get("name")
        desc = request.form.get("description")

        if len(str(name)) > 40:
            return error(400, "name too long! the coalition name needs to be under 40 characters")
        else:
            db.execute("INSERT INTO colNames (name, type, description) VALUES (%s, %s, %s)", (name, cType, desc))

            db.execute("SELECT id FROM colNames WHERE name = (%s)", (name,))
            colId = db.fetchone()[0] # Gets the coalition id of the just inserted coalition 

            # Inserts the user as the leader of the coalition
            db.execute("INSERT INTO coalitions (colId, userId, role) VALUES (%s, %s, %s)", (colId, session["user_id"], "leader"))

            # Inserts the coalition into the table for coalition banks
            db.execute("INSERT INTO colBanks (colId) VALUES (%s)", (colId,)) 

            connection.commit() # Commits the new data
            connection.close() # Closes the connection
            return redirect(f"/coalition/{colId}") # Redirects to the new coalition's page
    else:
        return render_template("establish_coalition.html")

# Route for viewing all existing coalitions
@login_required
@app.route("/coalitions", methods=["GET"])
def coalitions():
    
    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    try:
        search = request.values.get("search")
    except TypeError:
        search = None

    if search == None or search == "":
        try: 
            db.execute("SELECT id FROM colNames")
            coalitions = db.fetchall()
        except:
            coalitions = []
    else:
        db.execute("SELECT id FROM colNames WHERE name=(%s)", (search,))
        coalitions = db.fetchall()

    names = []
    ids = []
    members = []
    types = []
    influences = []

    for i in coalitions:

        ids.append(i[0])

        idd = str(i[0])

        db.execute("SELECT type FROM colNames WHERE id=%s", (idd,))
        colType = db.fetchone()[0]
        types.append(colType)

        db.execute("SELECT name FROM colNames WHERE id=%s", (idd,))
        colName = db.fetchone()[0]
        names.append(colName)

        db.execute("SELECT count(userId) FROM coalitions WHERE colId=%s", (idd,))
        colMembers = db.fetchone()[0]
        members.append(colMembers)

        influence = get_coalition_influence(idd)
        influences.append(influence)

    connection.close()

    resultAll = zip(names, ids, members, types, influences)

    return render_template("coalitions.html", resultAll=resultAll)

# Route for joining a coalition
@login_required
@app.route("/join/<colId>", methods=["POST"])
def join_col(colId):
    
    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    cId = session["user_id"]

    db.execute("SELECT type FROM colNames WHERE id=%s", (colId,))
    colType = db.fetchone()[0]

    if colType == "Open":

        db.execute("INSERT INTO coalitions (colId, userId) VALUES (%s, %s)", (colId, cId))

        connection.commit()

    else:

        message = request.form.get("message")

        db.execute("INSERT INTO requests (colId, reqId, message) VALUES (%s, %s, %s)", (colId, cId, message))

        connection.commit()

    connection.close()

    return redirect(f"/coalition/{colId}") # Redirects to the joined coalitions page

# Route for leaving a coalition
@login_required
@app.route("/leave/<colId>", methods=["POST"])
def leave_col(colId):

    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    cId = session["user_id"]

    role = get_user_role(cId)

    if role != "leader":
        return error(400, "Can't leave coalition, you're the leader")

    db.execute("DELETE FROM coalitions WHERE userId=(%s) AND colId=(%s)", (cId, colId))

    connection.commit()
    connection.close()

    return redirect("/coalitions")

# Route for redirecting to the user's coalition
@login_required
@app.route("/my_coalition", methods=["GET"])
def my_coalition():

    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()
    cId = session["user_id"]

    try:
        db.execute("SELECT colId FROM coalitions WHERE userId=%s", (cId,))
        coalition = db.fetchone()[0]

        connection.close()
    except TypeError:
        return redirect("/")  # Redirects to home page instead of an error

    return redirect(f"/coalition/{coalition}")

# Route for giving someone a role in your coalition
@login_required
@app.route("/give_position", methods=["POST"])
def give_position():
    
    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = conn.cursor()
    cId = session["user_id"]

    try:
        db.execute("SELECT colId FROM coalitions WHERE userId=%s", (cId,))
        colId = db.fetchone()[0]
    except:
        return error(400, "You are not a part of any coalition")

    user_role = get_user_role(cId)

    if user_role != "leader":
        return error(400, "You're not a leader")

    roles = ["leader", "deputy_leader", "banker", "tax_collector", "foreign_ambassador", "general", "domestic_minister"]

    role = request.form.get("role")

    if role not in roles:
        return error(400, "No such role exists")

    username = request.form.get("username")

    # The user id for the person being given the role
    db.execute("SELECT id FROM users WHERE username=%s", (username,))
    roleer = db.fetchone()[0]
    
    try:
        db.execute("SELECT colId FROM coalitions WHERE colId=%s AND userId=%s", (colId, roleer))
        db.fetchone()[0]
    except:
        return error(400, "There is no such user in the coalition")

    db.execute("UPDATE coalitions SET role=%s WHERE userId=%s", (role, roleer))

    conn.commit()
    conn.close()
    return redirect("/my_coalition")


@login_required
@app.route("/add/<uId>", methods=["POST"])
def adding(uId):
    
    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    try:
        db.execute("SELECT colId FROM requests WHERE reqId=(%s)", (uId,))
        colId = db.fetchone()[0]
    except TypeError:
        return error(400, "User hasn't posted a request to join")

    cId = session["user_id"]

    user_role = get_user_role(cId)

    if user_role != "leader":
        return error(400, "You are not a leader of the coalition")

    db.execute("DELETE FROM requests WHERE reqId=(%s) AND colId=(%s)", (uId, colId))

    db.execute("INSERT INTO coalitions (colId, userId) VALUES (%s, %s)", (colId, uId))

    connection.commit()
    connection.close()

    return redirect(f"/coalition/{colId}")


# Route for removing a join request
@login_required
@app.route("/remove/<uId>", methods=["POST"])
def removing_requests(uId):

    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    try:
        db.execute("SELECT colId FROM requests WHERE reqId=%s", (uId,))
        colId = db.fetchone()[0]
    except TypeError:
        return error(400, "User hasn't posted a request to join this coalition.")

    cId = session["user_id"]

    user_role = get_user_role(cId)
    
    if user_role != "leader":
        return error(400, "You are not the leader of the coalition")

    db.execute("DELETE FROM requests WHERE reqId=(%s) AND colId=(%s)", (uId, colId))

    connection.commit()

    return redirect(f"/coalition/{ colId }")

# Route for deleting a coalition
@login_required
@app.route("/delete_coalition/<colId>", methods=["POST"])
def delete_coalition(colId):

    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    cId = session["user_id"]

    user_role = get_user_role(cId)

    if user_role != "leader":
        return error(400, "You aren't the leader of this coalition")

    db.execute("SELECT name FROM colNames WHERE id=(%s)", (colId,))
    coalition_name = db.fetchone()[0]

    db.execute("DELETE FROM colNames WHERE id=(%s)", (colId,))
    db.execute("DELETE FROM coalitions WHERE colId=(%s)", (colId,))

    
    connection.commit()
    connection.close()

    flash(f"{coalition_name} coalition was deleted.")

    return redirect("/")

# Route for updating name, description, flag of coalition
@login_required
@app.route("/update_col_info/<colId>", methods=["POST"])
def update_col_info(colId):

    
    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    cId = session["user_id"]

    user_role = get_user_role(cId)

    if user_role != "leader":
        return error(400, "You aren't the leader of this coalition")

    ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    file = request.files["flag_input"]
    if file and allowed_file(file.filename):

        # Check if the user already has a flag
        try:
            db.execute("SELECT flag FROM colNames WHERE id=(%s)", (colId,))
            current_flag = db.fetchone()[0]

            # If he does, delete the flag
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], current_flag))
            db.execute("UPDATE colNames SET flag=null WHERE id=(%s)", (colId,))

        except TypeError:
            pass

        # Save the file
        current_filename = file.filename
        extension = current_filename.rsplit('.', 1)[1].lower()
        filename = f"col_flag_{colId}" + '.' + extension
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        db.execute("UPDATE colNames SET flag=(%s) WHERE id=(%s)", (filename, colId))

    connection.commit()
    connection.close()

    return redirect(f"/coalition/{colId}")

### COALITION BANK STUFF ###

# Route for depositing resources into the bank
@login_required
@app.route("/deposit_into_bank/<colId>", methods=["POST"])
def deposit_into_bank(colId):

    
    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    cId = session["user_id"]

    try:
        db.execute("SELECT userId FROM coalitions WHERE userId=(%s) and colId=(%s)", (cId, colId))
        db.fetchone()[0]
    except TypeError:
        return redirect(400, "You aren't in this coalition")

    resources = ["money", "rations", "oil", "coal", "uranium", "bauxite",
    "lead", "copper", "iron", "lumber", "components", "steel", "consumer_goods",
    "aluminium", "gasoline", "ammunition"]

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

            db.execute("SELECT gold FROM stats WHERE id=(%s)", (cId,))
            current_money = int(db.fetchone()[0])

            if current_money < amount:
                return error(400, "You don't have enough money")

            new_money = current_money - amount

            db.execute("UPDATE stats SET gold=(%s) WHERE id=(%s)", (new_money, cId))

        # If it isn't, removes the resource from the giver
        else:

            current_resource_statement = "SELECT %s FROM resources WHERE id=%s"

            db.execute(current_resource_statement, (resource, cId,))
            current_resource = int(db.fetchone()[0])

            if current_resource < amount:
                return error(400, f"You don't have enough {resource}")

            new_resource = current_resource - amount

            update_statement = "UPDATE resources SET %s=%s WHERE id=%s"
            db.execute(update_statement, (resource, new_resource, cId))

        # Gives the coalition the resource
        current_resource_statement = "SELECT %s FROM colBanks WHERE colId=%s"
        db.execute(current_resource_statement, (resource, colId,))
        current_resource = int(db.fetchone()[0])

        new_resource = current_resource + amount

        update_statement = "UPDATE colBanks SET %s=%s WHERE colId=%s"
        db.execute(update_statement, (resource, new_resource, colId))

    for resource in deposited_resources:
        name = resource[0]
        amount = resource[1]
        deposit(name, amount)

    connection.commit()
    connection.close()

    return redirect(f"/coalition/{colId}")

# Function for withdrawing a resource from the bank
def withdraw(resource, amount, user_id, colId):

    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    # Removes the resource from the coalition bank

    current_resource_statement = "SELECT %s FROM colBanks WHERE colId=%s"
    db.execute(current_resource_statement, (resource, colId,))
    current_resource = int(db.fetchone()[0])

    if current_resource < amount:
        return error(400, f"Your coalition doesn't have enough {resource}")

    new_resource = current_resource - amount

    update_statement = "UPDATE colBanks SET %s=%s WHERE colId=%s"
    db.execute(update_statement, (resource, new_resource, colId))

    # Gives the leader his resource
    # If the resource is money, gives him money
    if resource == "money":

        db.execute("SELECT gold FROM stats WHERE id=(%s)", (user_id,))
        current_money = int(db.fetchone()[0])

        new_money = current_money + amount

        db.execute("UPDATE stats SET gold=(%s) WHERE id=(%s)", (new_money, user_id))

    # If the resource is not money, gives him that resource
    else:

        current_resource_statement = "SELECT %s FROM resources WHERE id=%s"
        db.execute(current_resource_statement, (resource, user_id,))
        current_resource = int(db.fetchone()[0])

        new_resource = current_resource + amount

        update_statement = "UPDATE resources SET %s=%s WHERE id=%s"
        db.execute(update_statement, (resource, new_resource, user_id))

    connection.commit()
    connection.close()

# Route from withdrawing from the bank 
@login_required
@app.route("/withdraw_from_bank/<colId>", methods=["POST"])
def withdraw_from_bank(colId):

    cId = session["user_id"]

    user_role = get_user_role(cId)

    if user_role != "leader":
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

    return redirect(f"/coalition/{colId}")

# Route for requesting a resource from the coalition bank
@login_required
@app.route("/request_from_bank/<colId>", methods=["POST"])
def request_from_bank(colId):

    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    cId = session["user_id"]

    try:
        db.execute("SELECT userId FROM coalitions WHERE userId=(%s) and colId=(%s)", (cId, colId))
        db.fetchone()[0]
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

    db.execute("INSERT INTO colBanksRequests (reqId, colId, amount, resource) VALUES (%s, %s, %s, %s)", (cId, colId, requested_resources[1], requested_resources[0]))

    connection.commit()
    connection.close()

    return redirect(f"/coalition/{colId}")

# Route for removing a request for a resource from the coalition bank
@login_required
@app.route("/remove_bank_request/<bankId>", methods=["POST"])
def remove_bank_request(bankId):

    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    cId = session["user_id"]

    user_role = get_user_role(cId)

    if user_role != "leader":
        return error(400, "You aren't the leader of this coalition")

    db.execute("DELETE FROM colBanksRequests WHERE id=(%s)", (bankId,))

    connection.commit()
    connection.close()
    return redirect("/my_coalition")


# Route for accepting a bank request from the coalition bank
@login_required
@app.route("/accept_bank_request/<bankId>", methods=["POST"])
def accept_bank_request(bankId):

    
    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    cId = session["user_id"]

    db.execute("SELECT colId FROM colBanksRequests WHERE id=(%s)", (bankId,))
    colId = db.fetchone()[0]

    user_role = get_user_role(cId)

    if user_role != "leader":
        return error(400, "You aren't the leader of this coalition")

    db.execute("SELECT resource FROM colBanksRequests WHERE id=(%s)", (bankId,))
    resource = db.fetchone()[0]
    db.execute("SELECT amount FROM colBanksRequests WHERE id=(%s)", (bankId,))
    amount = db.fetchone()[0]
    db.execute("SELECT reqId FROM colBanksRequests WHERE id=(%s)", (bankId,))
    user_id = db.fetchone()[0]

    withdraw(resource, amount, user_id, colId)
    db.execute("DELETE FROM colBanksRequests WHERE id=(%s)", (bankId,))

    connection.commit()
    connection.close()

    return redirect("/my_coalition")

# Route for offering another coalition a treaty
@login_required
@app.route("/offer_treaty", methods=["POST"])
def offer_treaty():
    
    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    cId = session["user_id"]

    col2_name = request.form.get("coalition_name")
    db.execute("SELECT id FROM colNames WHERE name=(%s)", (col2_name,))
    col2_id = db.fetchone()[0]

    db.execute("SELECT colId FROM coalitions WHERE userId=(%s)", (cId,))
    user_coalition = db.fetchone()[0]

    user_role = get_user_role(cId)

    if user_role != "leader":
        return error(400, "You aren't the leader of this coalition")

    treaty_name = request.form.get("treaty_name")
    db.execute("SELECT treaty_id FROM treaty_ids WHERE title=(%s)", (treaty_name,))
    treaty_id = db.fetchone()[0]

    db.execute("INSERT INTO treaties (col1_id, col2_id, treaty_id) VALUES (%s, %s, %s)", (user_coalition, col2_id, treaty_id))

    treaty_id = db.fetchone()[0]

    connection.commit()
    connection.close()

    return redirect("/my_coalition")

# Route for accepting a treaty offer from another coalition
@login_required
@app.route("/accept_treaty/<offer_id>", methods=["POST"])
def accept_treaty(offer_id):

    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    cId = session["user_id"]

    db.execute("SELECT colId FROM coalitions WHERE userId=(%s)", (cId,))
    user_coalition = db.fetchone()[0]

    user_role = get_user_role(cId)

    if user_role != "leader":
        return error(400, "You aren't the leader of this coalition")

    db.execute("UPDATE treaties SET status='Active' WHERE id=(%s)", (offer_id,))

    connection.commit()
    connection.close()

    return redirect("/my_coalition")

# Route for breaking a treaty with another coalition
@login_required
@app.route("/break_treaty/<offer_id>", methods=["POST"])
def break_treaty(offer_id):
    
    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    cId = session["user_id"]

    user_role = get_user_role(cId)

    if user_role != "leader":
        return error(400, "You aren't the leader of this coalition")

    db.execute("DELETE FROM treaties WHERE id=(%s)", (offer_id,))

    connection.commit()
    connection.close()

    return redirect("/my_coalition")

@login_required
@app.route("/decline_treaty/<offer_id>", methods=["POST"])
def decline_treaty(offer_id):

    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    cId = session["user_id"]

    user_role = get_user_role(cId)

    if user_role != "leader":
        return error(400, "You aren't the leader of this coalition")

    db.execute("DELETE FROM treaties WHERE id=(%s)", (offer_id,))

    connection.commit()
    connection.close()

    return redirect("/my_coalition")