from flask import request, render_template, session, redirect, flash
from helpers import login_required, error
import psycopg2
from helpers import get_coalition_influence
from app import app
import os
from dotenv import load_dotenv
load_dotenv()
import variables
from operator import itemgetter

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
@app.route("/coalition/<colId>", methods=["GET"])
@login_required
def coalition(colId):

    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    cId = session["user_id"]

    try:
        db.execute("SELECT name FROM colNames WHERE id=(%s)", (colId,))
        name = db.fetchone()[0]
    except:
        return error(404, "This coalition doesn't exist")

    try:
        db.execute("SELECT type FROM colNames WHERE id=(%s)", (colId,))
        colType = db.fetchone()[0]
    except:
        colType = "Open"

    try:
        db.execute("SELECT COUNT(userId) FROM coalitions WHERE colId=(%s)", (colId,))
        members_count = db.fetchone()[0]
    except:
        members_count = 0

    try:
        total_influence = get_coalition_influence(colId)
    except:
        total_influence = 0

    try:
        average_influence = total_influence // members_count
    except:
        average_influence = 0

    try:
        db.execute("SELECT description FROM colNames WHERE id=(%s)", (colId,))
        description = db.fetchone()[0]
    except:
        description = ""

    try:
        db.execute("SELECT coalitions.userId, users.username FROM coalitions INNER JOIN users ON coalitions.userId=users.id AND coalitions.role='leader' AND coalitions.colId=%s", (colId,))
        leaders = db.fetchall() # All coalition leaders ids
    except:
        leaders = []

    try:
        db.execute("SELECT coalitions.userId, users.username, coalitions.role FROM coalitions INNER JOIN users ON coalitions.userId=users.id AND coalitions.colId=%s", (colId,))
        members = db.fetchall() # All coalition leaders ids
    except:
        members = []

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

    try:
        user_role = get_user_role(cId)
    except:
        user_role = None

    if user_role in ["leader", "deputy_leader", "domestic_minister"] and userInCurCol:

        member_roles = {
            "leader": None,
            "deputy_leader": None,
            "domestic_minister": None,
            "banker": None,
            "tax_collector": None,
            "foreign_ambassador": None,
            "general": None,
            "member": None
        }

        for role in member_roles:
            db.execute("SELECT COUNT(userId) FROM coalitions WHERE role=" + "'" + role  + "'" + " AND colId=%s", (colId,))
            member_roles[role] = db.fetchone()[0]

    else:
        member_roles = {}

    # Treaties
    if user_role in ["foreign_ambassador", "leader", "deputy_leader"] and userInCurCol:

        # Ingoing
        try:
            try:
                db.execute("SELECT id FROM treaties WHERE col2_id=(%s) AND status='Pending' ORDER BY id ASC", (colId,))
                ingoing_ids = list(db.fetchall()[0])
            except:
                ingoing_ids = []

            col_ids = []
            col_names = []
            trt_names = []
            trt_descriptions = []

            for treaty_id in ingoing_ids:

                treaty_id = treaty_id

                db.execute("SELECT col1_id, treaty_name, treaty_description FROM treaties WHERE id=(%s)", (treaty_id,))
                col_id, treaty_name, treaty_description = db.fetchone()
                col_ids.append(col_id)
                trt_names.append(treaty_name)
                trt_descriptions.append(treaty_description)

                db.execute("SELECT name FROM colNames WHERE id=(%s)", (col_id,))
                coalition_name = db.fetchone()[0]
                col_names.append(coalition_name)

            ingoing_treaties = {}
            ingoing_treaties["ids"] = ingoing_ids,
            ingoing_treaties["col_ids"] = col_ids,
            ingoing_treaties["col_names"] = col_names,
            ingoing_treaties["treaty_names"] = trt_names,
            ingoing_treaties["treaty_descriptions"] = trt_descriptions
            ingoing_length = len(ingoing_ids)
        except:
            ingoing_treaties = {}
            ingoing_length = 0

        #### ACTIVE ####
        try:
            try:
                db.execute("SELECT id FROM treaties WHERE col2_id=(%s) AND status='Active' OR col1_id=(%s) ORDER BY id ASC", (colId, colId))
                raw_active_ids = db.fetchall()
            except:
                raw_active_ids = []

            active_treaties = {}
            active_treaties["ids"] = []
            active_treaties["col_ids"] = []
            active_treaties["col_names"] = []
            active_treaties["treaty_names"] = []
            active_treaties["treaty_descriptions"] = []

            for i in raw_active_ids:
                offer_id = i[0]

                active_treaties["ids"].append(offer_id)

                db.execute("SELECT col1_id, treaty_name, treaty_description FROM treaties WHERE id=(%s)", (offer_id,))
                coalition_id, treaty_name, treaty_description = db.fetchone()
                if coalition_id == colId:
                    db.execute("SELECT col2_id FROM treaties WHERE id=(%s)", (offer_id,))
                    coalition_id = db.fetchone()[0]

                db.execute("SELECT name FROM colNames WHERE id=(%s)", (coalition_id,))
                coalition_name = db.fetchone()[0]

                active_treaties["col_ids"].append(coalition_id)
                active_treaties["col_names"].append(coalition_name)
                active_treaties["treaty_names"].append(treaty_name)
                active_treaties["treaty_descriptions"].append(treaty_description)

            active_length = len(raw_active_ids)
        except:
            active_treaties = {}
            active_length = 0
    else:
        ingoing_treaties = {}
        active_treaties = {}
        ingoing_length = 0
        active_length = 0

    if userInCurCol:
        bankRaw = {
            'money': None,
            'rations': None,
            'oil': None,
            'coal': None,
            'uranium': None,
            'bauxite': None,
            'iron': None,
            'copper': None,
            'lead': None,
            'lumber': None,
            'components': None,
            'steel': None,
            'consumer_goods': None,
            'aluminium': None,
            'gasoline': None,
            'ammunition': None
        }

        for raw in bankRaw:
            db.execute("SELECT " + raw  + " FROM colBanks WHERE colId=(%s)", (colId,))
            bankRaw[raw] = db.fetchone()[0]
    else:
        bankRaw = {}

    try:
        db.execute("SELECT flag FROM colNames WHERE id=(%s)", (colId,))
        flag = db.fetchone()[0]
    except:
        flag = None

    if user_role == "leader" and colType != "Open" and userInCurCol:

        db.execute("SELECT message FROM requests WHERE colId=(%s) ORDER BY reqId ASC", (colId,))
        requestMessages = db.fetchall()
        db.execute("SELECT reqId FROM requests WHERE colId=(%s) ORDER BY reqId ASC", (colId,))
        requestIds = db.fetchall()
        requestNames = []

        for request_id in requestIds:

            request_id = request_id[0]
            db.execute("SELECT username FROM users WHERE id=%s", (request_id,))
            requestName = db.fetchone()[0]
            requestNames.append(requestName)

        requests = zip(requestIds, requestNames, requestMessages)
    else:
        requests = []
        requestIds = []

    ### BANK STUFF
    if user_role == "leader" and userInCurCol:

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

    print(members)

    return render_template("coalition.html", name=name, colId=colId, user_role=user_role,
        description=description, colType=colType, userInCol=userInCol,
        requests=requests, userInCurCol=userInCurCol, total_influence=total_influence,
        average_influence=average_influence, leaders=leaders,
        flag=flag, bankRequests=bankRequests, active_treaties=active_treaties, bankRaw=bankRaw,
        ingoing_length=ingoing_length, active_length=active_length, member_roles=member_roles, 
        ingoing_treaties=ingoing_treaties, zip=zip, requestIds=requestIds,
        members=members)


# Route for establishing a coalition
@app.route("/establish_coalition", methods=["GET", "POST"])
@login_required
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
            return error(400, "Name too long! the coalition name needs to be under 40 characters")
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
@app.route("/coalitions", methods=["GET"])
def coalitions():

    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()
    search = request.values.get("search")
    sort = request.values.get("sort")
    sortway = request.values.get("sortway")

    db.execute("""SELECT colNames.id, colNames.type, colNames.name, COUNT(coalitions.userId) AS members
FROM colNames
INNER JOIN coalitions
ON colNames.id=coalitions.colId
GROUP BY colNames.id;
""")
    coalitionsDb = db.fetchall()

    connection.close()

    coalitions = []
    for col in coalitionsDb:
        col = list(col)
        addCoalition = True
        col_id = col[0]
        name = col[2]
        col_type = col[1]

        influence = get_coalition_influence(col_id)
        col.append(influence)

        if search and search not in name:
            addCoalition = False

        if sort == "invite_only" and col_type == "Open":
            addCoalition = False
        if sort == "open" and col_type == "Invite Only":
            addCoalition = False

        if addCoalition:
            coalitions.append(col)

    reverse = False
    if not sort or sort in ["open", "invite_only"]: # Default sort by influence for invite only and open
        if not sortway: sortway = "desc"
        sort = "influence"
    if sortway == "desc": reverse = True
    if sort == "influence":
        coalitions = sorted(coalitions, key=itemgetter(4), reverse=reverse)
    elif sort == "members":
        coalitions = sorted(coalitions, key=itemgetter(3), reverse=reverse)

    return render_template("coalitions.html", coalitions=coalitions)

# Route for joining a coalition
@app.route("/join/<colId>", methods=["POST"])
@login_required
def join_col(colId):

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
        db.fetchone()[0]

        return error(400, "You're already in a coalition")
    except:
        pass

    db.execute("SELECT type FROM colNames WHERE id=%s", (colId,))
    colType = db.fetchone()[0]

    if colType == "Open":
        db.execute("INSERT INTO coalitions (colId, userId) VALUES (%s, %s)", (colId, cId))
    else:

        db.execute("SELECT FROM requests WHERE colId=%s and reqId=%s", (colId, cId,))
        duplicate = db.fetchone()
        if duplicate is not None:
            return error(400, "You've already submitted a request to join this coalition")
            
        message = request.form["message"]
        db.execute("INSERT INTO requests (colId, reqId, message) VALUES (%s, %s, %s)", (colId, cId, message))

    connection.commit()
    connection.close()

    return redirect(f"/coalition/{colId}") # Redirects to the joined coalitions page

# Route for leaving a coalition
@app.route("/leave/<colId>", methods=["POST"])
@login_required
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

    if role == "leader":
        return error(400, "Can't leave coalition, you're the leader")

    db.execute("DELETE FROM coalitions WHERE userId=(%s) AND colId=(%s)", (cId, colId))

    connection.commit()
    connection.close()

    return redirect("/coalitions")

# Route for redirecting to the user's coalition
@app.route("/my_coalition", methods=["GET"])
@login_required
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
@app.route("/give_position", methods=["POST"])
@login_required
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

    if user_role not in ["leader", "deputy_leader", "domestic_minister"]:
        return error(400, "You're not a leader")

    # DO NOT EDIT LIST. USED FOR RANKS
    roles = ["leader", "deputy_leader", "domestic_minister", "banker", "tax_collector", "foreign_ambassador", "general", "member"]

    role = request.form.get("role")

    username = request.form.get("username")

    # The user id for the person being given the role
    try:
        db.execute("SELECT id FROM users WHERE username=%s", (username,))
        roleer = db.fetchone()[0]
    except:
        return error(400, f"Cannot find user {username}")

    try:
        db.execute("SELECT colId FROM coalitions WHERE colId=%s AND userId=%s", (colId, roleer))
        db.fetchone()[0]
    except:
        return error(400, "There is no such user in the coalition")

    db.execute("SELECT role FROM coalitions WHERE userId=%s", (roleer,))
    current_roleer_role = db.fetchone()[0]

    if role not in roles:
        return error(400, "No such role exists")

    # If the user role is lower up the hierarchy than the giving role
    # Or if the current role of the person being given the role is higher up the hierarchy than the user giving the role
    if roles.index(role) < roles.index(user_role) or roles.index(current_roleer_role) < roles.index(user_role): 
        return error(400, "Can't edit role for a person higher rank than you.")

    db.execute("UPDATE coalitions SET role=%s WHERE userId=%s", (role, roleer))

    conn.commit()
    conn.close()
    return redirect("/my_coalition")

# Route for accepting a coalition join request
@app.route("/add/<uId>", methods=["POST"])
@login_required
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

    if user_role not in ["leader", "deputy_leader", "domestic_minister"]:
        return error(400, "You are not a leader of the coalition")

    db.execute("DELETE FROM requests WHERE reqId=(%s) AND colId=(%s)", (uId, colId))
    db.execute("INSERT INTO coalitions (colId, userId) VALUES (%s, %s)", (colId, uId))

    connection.commit()
    connection.close()

    return redirect(f"/coalition/{colId}")


# Route for removing a join request
@app.route("/remove/<uId>", methods=["POST"])
@login_required
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

    if user_role not in ["leader", "deputy_leader", "domestic_minister"]:
        return error(400, "You are not the leader of the coalition")

    db.execute("DELETE FROM requests WHERE reqId=(%s) AND colId=(%s)", (uId, colId))

    connection.commit()

    return redirect(f"/coalition/{ colId }")

# Route for deleting a coalition
@app.route("/delete_coalition/<colId>", methods=["POST"])
@login_required
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
@app.route("/update_col_info/<colId>", methods=["POST"])
@login_required
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

    flag = request.files["flag_input"]
    if flag:
        if allowed_file(flag.filename):

            # Check if the user already has a flag
            try:
                db.execute("SELECT flag FROM colNames WHERE id=(%s)", (colId,))
                current_flag = db.fetchone()[0]

                # If he does, delete the flag
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], current_flag))

            except:
                pass

            # Save the file
            current_filename = flag.filename
            extension = current_filename.rsplit('.', 1)[1].lower()
            filename = f"col_flag_{colId}" + '.' + extension
            flag.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            db.execute("UPDATE colNames SET flag=(%s) WHERE id=(%s)", (filename, colId))
        else:
            return error(400, "File format not supported")

    # Application type
    application_type = request.form.get("application_type")
    if application_type not in ["", "Open", "Invite Only"]:
        return error(400, "No such type")

    if application_type != "":
        db.execute("UPDATE colNames SET type=%s WHERE id=%s", (application_type, colId))

    # Description
    description = request.form.get("description")
    if description not in [None, "None", ""]:
        db.execute("UPDATE colNames SET description=%s WHERE id=%s", (description, colId))

    connection.commit()
    connection.close()

    return redirect("/my_coalition")

### COALITION BANK STUFF ###

# Route for depositing resources into the bank
@app.route("/deposit_into_bank/<colId>", methods=["POST"])
@login_required
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

    resources = variables.RESOURCES

    deposited_resources = []

    for res in resources:

        try:
            resource = request.form.get(res)
        except:
            resource = ""

        if resource != "" and int(resource) > 0:
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

            current_resource_statement = f"SELECT {resource} FROM resources" + " WHERE id=%s"

            db.execute(current_resource_statement, (cId,))
            current_resource = int(db.fetchone()[0])

            if amount < 1:
                return error(400, "Amount cannot be less than 1")

            if current_resource < amount:
                return error(400, f"You don't have enough {resource}")

            new_resource = current_resource - amount

            update_statement = f"UPDATE resources SET {resource}" + "=%s WHERE id=%s"
            db.execute(update_statement, (new_resource, cId))

        # Gives the coalition the resource
        current_resource_statement = f"SELECT {resource} FROM colBanks" +  " WHERE colId=%s"
        db.execute(current_resource_statement, (colId,))
        current_resource = int(db.fetchone()[0])

        new_resource = current_resource + amount

        update_statement = f"UPDATE colBanks SET {resource}" + "=%s WHERE colId=%s"
        db.execute(update_statement, (new_resource, colId))

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

    current_resource_statement = f"SELECT {resource}" + " FROM colBanks WHERE colId=%s"
    db.execute(current_resource_statement, (colId,))
    current_resource = db.fetchone()[0]

    if amount < 1:
        return error(400, "Amount cannot be less than 1")

    if current_resource < amount:
        return error(400, f"Your coalition doesn't have enough {resource}")

    new_resource = current_resource - amount

    update_statement = f"UPDATE colBanks SET {resource}" + "=%s WHERE colId=%s"
    db.execute(update_statement, (new_resource, colId))

    # Gives the leader his resource
    # If the resource is money, gives him money
    if resource == "money":

        db.execute("SELECT gold FROM stats WHERE id=(%s)", (user_id,))
        current_money = int(db.fetchone()[0])

        new_money = current_money + amount

        db.execute("UPDATE stats SET gold=(%s) WHERE id=(%s)", (new_money, user_id))

    # If the resource is not money, gives him that resource
    else:

        current_resource_statement = f"SELECT {resource}" +  " FROM resources WHERE id=%s"
        db.execute(current_resource_statement, (user_id,))
        current_resource = db.fetchone()[0]

        new_resource = current_resource + amount

        update_statement = f"UPDATE resources SET {resource}" + "=%s WHERE id=%s"
        db.execute(update_statement, (new_resource, user_id))

    connection.commit()
    connection.close()

# Route from withdrawing from the bank
@app.route("/withdraw_from_bank/<colId>", methods=["POST"])
@login_required
def withdraw_from_bank(colId):

    cId = session["user_id"]

    user_role = get_user_role(cId)

    if user_role not in ["leader", "deputy_leader", "banker"]:
        return error(400, "You aren't the leader of this coalition")

    resources = variables.RESOURCES

    withdrew_resources = []

    for res in resources:
        resource = request.form.get(res)
        if resource != "":
            res_tuple = (res, int(resource))
            withdrew_resources.append(res_tuple)

    for resource in withdrew_resources:
        name = resource[0]
        amount = resource[1]

        if amount < 1:
            return error(400, "Amount has to be greater than 1")

        withdraw(name, amount, cId, colId)

    return redirect(f"/coalition/{colId}")

# Route for requesting a resource from the coalition bank
@app.route("/request_from_bank/<colId>", methods=["POST"])
@login_required
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

    resources = variables.RESOURCES

    requested_resources = []

    for res in resources:
        resource = request.form.get(res)
        if resource != "":
            res_tuple = (res, int(resource))
            requested_resources.append(res_tuple)

    if len(requested_resources) > 1:
        return error(400, "You can only request one resource at a time")

    requested_resources = tuple(requested_resources[0])

    amount = requested_resources[1]

    if amount < 1:
        return error(400, "Amount cannot be 0 or less")

    resource = requested_resources[0]

    db.execute("INSERT INTO colBanksRequests (reqId, colId, amount, resource) VALUES (%s, %s, %s, %s)", (cId, colId, amount, resource))

    connection.commit()
    connection.close()

    return redirect(f"/coalition/{colId}")

# Route for removing a request for a resource from the coalition bank
@app.route("/remove_bank_request/<bankId>", methods=["POST"])
@login_required
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

    if user_role not in ["leader", "deputy_leader", "banker"]:
        return error(400, "You aren't the leader of this coalition")

    db.execute("DELETE FROM colBanksRequests WHERE id=(%s)", (bankId,))

    connection.commit()
    connection.close()
    return redirect("/my_coalition")


# Route for accepting a bank request from the coalition bank
@app.route("/accept_bank_request/<bankId>", methods=["POST"])
@login_required
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

    if user_role not in  ["leader", "deputy_leader", "banker"]:
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
@app.route("/offer_treaty", methods=["POST"])
@login_required
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
    if col2_name == "":
        return error(400, "Please enter a coalition name")

    try:
        db.execute("SELECT id FROM colNames WHERE name=(%s)", (col2_name,))
        col2_id = db.fetchone()[0]
    except:
        return error(400, f"No such coalition: {col2_name}")

    try:
        db.execute("SELECT colId FROM coalitions WHERE userId=(%s)", (cId,))
        user_coalition = db.fetchone()[0]
    except:
        return error(400, "You are not in a coalition")

    if col2_id == user_coalition:
        return error(400, "Cannot declare treaty on your own coalition")

    user_role = get_user_role(cId)

    if user_role not in  ["leader", "deputy_leader", "foreign_ambassador"]:
        return error(400, "You aren't the leader of this coalition")

    treaty_name = request.form.get("treaty_name")
    if treaty_name == "":
        return error(400, "Please enter a treaty name")

    treaty_message = request.form.get("treaty_message")
    if treaty_message == "":
        return error(400, "Please enter a treaty description")
    try:
        db.execute("INSERT INTO treaties (col1_id, col2_id, treaty_name, treaty_description) VALUES (%s, %s, %s, %s)", (user_coalition, col2_id, treaty_name, treaty_message))
    except:
        return error(400, "Error inserting into database. Please contact the website admins")

    connection.commit()
    connection.close()

    return redirect("/my_coalition")

# Route for accepting a treaty offer from another coalition
@app.route("/accept_treaty/<offer_id>", methods=["POST"])
@login_required
def accept_treaty(offer_id):

    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    cId = session["user_id"]

    offer_id = int(offer_id)

    try:

        db.execute("SELECT colId FROM coalitions WHERE userId=(%s)", (cId,))
        user_coalition = db.fetchone()[0]

        db.execute("SELECT id FROM treaties WHERE col2_id=%s AND id=%s", (user_coalition, offer_id))
        permission_offer_id = db.fetchone()[0]

    except:
        return error(400, "You do not have such an offer")

    if permission_offer_id != offer_id:
        return error(400, "You do not have an offer for this id. Please report this bug if you're using the web ui and not testing for permission vulns haha")

    user_role = get_user_role(cId)

    if user_role not in ["leader", "deputy_leader", "foreign_ambassador"]:
        return error(400, "You aren't the leader of this coalition")

    db.execute("UPDATE treaties SET status='Active' WHERE id=(%s)", (offer_id,))

    connection.commit()
    connection.close()

    return redirect("/my_coalition")

# Route for breaking a treaty with another coalition
@app.route("/break_treaty/<offer_id>", methods=["POST"])
@login_required
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

    if user_role not in ["leader", "deputy_leader", "foreign_ambassador"]:
        return error(400, "You aren't the leader of this coalition")

    db.execute("DELETE FROM treaties WHERE id=(%s)", (offer_id,))

    connection.commit()
    connection.close()

    return redirect("/my_coalition")

@app.route("/decline_treaty/<offer_id>", methods=["POST"])
@login_required
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

    if user_role not in ["leader", "deputy_leader", "foreign_ambassador"]:
        return error(400, "You aren't the leader of this coalition")

    db.execute("DELETE FROM treaties WHERE id=(%s)", (offer_id,))

    connection.commit()
    connection.close()

    return redirect("/my_coalition")
