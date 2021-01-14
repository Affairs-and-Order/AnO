# FULLY MIGRATED

from flask import request, render_template, session, redirect
from helpers import login_required
import psycopg2
# from celery.schedules import crontab # arent currently using but will be later on
from helpers import get_influence, error
# Game.ping() # temporarily removed this line because it might make celery not work
from app import app
import os
from dotenv import load_dotenv
from coalitions import get_user_role
load_dotenv()

app.config['UPLOAD_FOLDER'] = 'static/flags'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024    # 2 Mb limit

@app.route("/country/id=<cId>")
@login_required
def country(cId):

    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    try:
        db.execute("SELECT username, description, date FROM users WHERE id=%s", (cId,))
        user_data = db.fetchall()[0]
    except:
        return error(404, "Country doesn't exit")

    username = user_data[0]
    description = user_data[1]
    dateCreated = user_data[2]

    influence = get_influence(cId)

    db.execute("SELECT SUM(population), SUM(happiness), COUNT(id) FROM provinces WHERE userId=%s", (cId,))
    province_data = db.fetchall()[0]

    population = province_data[0]
    happiness = province_data[1]
    provinceCount = province_data[2]

    db.execute("SELECT location FROM stats WHERE id=%s", (cId,))
    location = db.fetchone()[0]

    db.execute("SELECT provinceName, id, population, cityCount, land FROM provinces WHERE userId=(%s) ORDER BY id DESC", (cId,))
    provinces = db.fetchall()

    status = cId == str(session["user_id"])

    try:
        db.execute("SELECT colId, role FROM coalitions WHERE userId=(%s)", (cId,))
        coalition_data = db.fetchall()[0]

        colId = coalition_data[0]
        colRole = coalition_data[1]

        db.execute("SELECT name FROM colNames WHERE id =%s", (colId,))
        colName = db.fetchone()[0]

    except:
        colId = 0
        colRole = None
        colName = ""

    try:
        db.execute("SELECT flag FROM colNames WHERE id=%s", (colId,))
        colFlag = db.fetchone()[0]
    except:
        colFlag = None


    try:
        db.execute("SELECT flag FROM users WHERE id=(%s)", (cId,))
        flag = db.fetchone()[0]
    except:
        flag = None

    """
    db.execute("SELECT spies FROM military WHERE id=(%s)", (cId,))
    spyCount = db.fetchone()[0]
    spyPrep = 1 # this is an integer from 1 to 5
    eSpyCount = 0 # this is an integer from 0 to 100
    eDefcon = 1 # this is an integer from 1 to 5

    if eSpyCount == 0:
        successChance = 100
    else:
        successChance = spyCount * spyPrep / eSpyCount / eDefcon
    """

    spyCount = 0
    successChance = 0

    connection.close()

    return render_template("country.html", username=username, cId=cId, description=description,
                           happiness=happiness, population=population, location=location, status=status,
                           provinceCount=provinceCount, colName=colName, dateCreated=dateCreated, influence=influence,
                           provinces=provinces, colId=colId, flag=flag, spyCount=spyCount, successChance=successChance,
                           colFlag=colFlag, colRole=colRole)


@app.route("/countries", methods=["GET"])
@login_required
def countries():  # TODO: fix shit ton of repeated code in function

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
        search = ""

    try:
        lowerinf = float(request.values.get("lowerinf"))
    except TypeError:
        lowerinf = None

    try:
        upperinf = float(request.values.get("upperinf"))
    except TypeError:
        upperinf = None

    try:
        province_range = int(request.values["province_range"])
    except:
        province_range = None

    # Optimize
    # if not search and upperinf is None and lowerinf is None:
    if not search:
        db.execute("SELECT id FROM users ORDER BY id")
        users = db.fetchall()

    # elif search is not None and upperinf is None and lowerinf is None:
    elif search != "":
        db.execute("SELECT id FROM users WHERE username=(%s) ORDER BY id", (search,))
        users = db.fetchall()

    if lowerinf is not None and upperinf is None:
        for user in users:
            user_id = int(user[0])
            if get_influence(user_id) < lowerinf:
                users.remove(user)

    elif upperinf is not None and lowerinf is None:
        for user in users:
            user_id = int(user[0])
            if get_influence(user_id) > upperinf:
                users.remove(user)

    elif upperinf is not None and lowerinf is not None:
        for user in users:
            user_influence = get_influence(int(user[0]))
            if user_influence > upperinf or user_influence < lowerinf:
                users.remove(user)

    # db.execute("SELECT username FROM users ORDER BY id")
    # names = db.fetchall()

    # db.execute("SELECT username FROM users ORDER BY id")
    # names = db.fetchall()
    # Check province range
    if province_range is not None:
        for user in users:
            user_id = user[0]
            db.execute(f"SELECT COUNT(id) FROM provinces WHERE userid=(%s)", (user_id,))
            target_province = db.fetchone()[0]
            print(target_province)
            if abs(target_province-province_range) > 1:
                users.remove(user)

    populations = []
    coalition_ids = []
    coalition_names = []
    dates = []
    influences = []
    flags = []
    names = []

    for i in users:

        db.execute("SELECT username FROM users WHERE id=(%s)", (i[0],))
        names.append(db.fetchone())

        db.execute("SELECT date FROM users WHERE id=(%s)", ((i[0]),))
        date = db.fetchone()[0]
        dates.append(date)

        db.execute("SELECT SUM(population) FROM provinces WHERE userId=%s", (i[0],))
        population = db.fetchone()[0]
        populations.append(population)

        influence = get_influence(str(i[0]))
        influences.append(influence)

        try:
            db.execute("SELECT flag FROM users WHERE id=(%s)", (i[0],))
            flag = db.fetchone()[0]
        except TypeError:
            flag = None

        flags.append(flag)

        try:
            db.execute("SELECT colId FROM coalitions WHERE userId = (%s)", (i[0],))
            coalition_id = db.fetchone()[0]
            coalition_ids.append(coalition_id)

            db.execute("SELECT name FROM colNames WHERE id = (%s)", (coalition_id,))
            coalition_name = db.fetchone()[0]
            coalition_names.append(coalition_name)
        except:
            coalition_ids.append("No Coalition")
            coalition_names.append("No Coalition")

    connection.commit()
    connection.close()

    resultAll = zip(populations, users, names, coalition_ids,
                    coalition_names, dates, influences, flags)

    return render_template("countries.html", resultAll=resultAll)



@app.route("/update_country_info", methods=["POST"])
@login_required
def update_info():

    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()
    cId = session["user_id"]

    # Description changing
    description = request.form["description"]

    if description not in ["None", ""]:
        db.execute("UPDATE users SET description=%s WHERE id=%s", (description, cId))

    # Flag changing
    ALLOWED_EXTENSIONS = ['png', 'jpg']

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    flag = request.files["flag_input"]
    if flag:

        if not allowed_file(flag.filename):
            return error(400, "Bad flag file format")

        current_filename = flag.filename

        try:
            db.execute("SELECT flag FROM users WHERE id=(%s)", (cId,))
            current_flag = db.fetchone()[0]

            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], current_flag))
        except:
            pass

        # Save the file & shit
        if allowed_file(current_filename):
            extension = current_filename.rsplit('.', 1)[1].lower()
            filename = f"flag_{cId}" + '.' + extension
            new_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            flag.save(new_path)
            db.execute("UPDATE users SET flag=(%s) WHERE id=(%s)", (filename, cId))

    """
    bg_flag = request.files["bg_flag_input"]
    if bg_flag and allowed_file(bg_flag.filename):

        print("bg flag")

        # Check if the user already has a flag
        try:
            db.execute("SELECT bg_flag FROM users WHERE id=(%s)", (cId,))
            current_bg_flag = db.fetchone()[0]

            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], current_bg_flag))
        except FileNotFoundError:
            pass

        # Save the file & shit
        current_filename = bg_flag.filename
        if allowed_file(current_filename):
            extension = current_filename.rsplit('.', 1)[1].lower()
            filename = f"bg_flag_{cId}" + '.' + extension
            flag.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            db.execute("UPDATE users SET bg_flag=(%s) WHERE id=(%s)", (filename, cId))
    """

    # Location changing
    new_location = request.form.get("countryLocation")

    continents = ["Tundra", "Savanna", "Desert", "Jungle", "Boreal Forest", "Grassland", "Mountain Range"]

    if new_location not in continents and new_location not in ["", "none"]:
        return error(400, "No such continent")

    if new_location not in ["", "none"]:

        try:
            db.execute("SELECT id FROM provinces WHERE userId=%s", (cId,))
            provinces = db.fetchall()[0]

            for province_id in provinces:

                db.execute("UPDATE proInfra SET pumpjacks=0 WHERE id=%s", (province_id,))
                db.execute("UPDATE proInfra SET coal_mines=0 WHERE id=%s", (province_id,))
                db.execute("UPDATE proInfra SET bauxite_mines=0 WHERE id=%s", (province_id,))
                db.execute("UPDATE proInfra SET copper_mines=0 WHERE id=%s", (province_id,))
                db.execute("UPDATE proInfra SET uranium_mines=0 WHERE id=%s", (province_id,))
                db.execute("UPDATE proInfra SET lead_mines=0 WHERE id=%s", (province_id,))
                db.execute("UPDATE proInfra SET iron_mines=0 WHERE id=%s", (province_id,))
                db.execute("UPDATE proInfra SET lumber_mills=0 WHERE id=%s", (province_id,))

            connection.commit()  # Commits the data

        except:
            return error(400, "")

        db.execute("UPDATE stats SET location=(%s) WHERE id=(%s)", (new_location, cId))

        connection.commit()

    connection.commit()  # Commits the data

    connection.close()  # Closes the connection

    return redirect(f"/country/id={cId}")  # Redirects the user to his country

@app.route("/delete_own_account", methods=["POST"])
@login_required
def delete_own_account():

    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()
    cId = session["user_id"]

    # Deletes all the info from database created upon signup
    db.execute("DELETE FROM users WHERE id=(%s)", (cId,))
    db.execute("DELETE FROM stats WHERE id=(%s)", (cId,))
    db.execute("DELETE FROM military WHERE id=(%s)", (cId,))
    db.execute("DELETE FROM resources WHERE id=(%s)", (cId,))
    # Deletes all market things the user is associateed with
    try:
        db.execute("DELETE FROM offers WHERE user_id=(%s)", (cId,))
    except:
        pass

    try:
        db.execute("DELETE FROM wars WHERE defender=%s OR attacker=%s", (cId, cId))
    except:
        pass

    # Deletes all the users provinces and their infrastructure
    try:
        db.execute("SELECT id FROM provinces WHERE userId=(%s)", (cId,))
        province_ids = db.fetchall()[0]
        for province_id in province_ids:
            db.execute("DELETE FROM provinces WHERE id=(%s)", (province_id,))
            db.execute("DELETE FROM proInfra WHERE id=(%s)", (province_id,))
    except:
        pass

    try:
        db.execute("DELETE FROM upgrades WHERE user_id=%s", (cId,))
    except:
        pass

    try:
        db.execute("DELETE FROM trades WHERE offeree=%s OR offerer=%s", (cId, cId))
    except:
        pass

    try:
        db.execute("DELETE FROM spyinfo WHERE spyer=%s OR spyee=%s", (cId, cId))
    except:
        pass

    try:
        db.execute("DELETE FROM requests WHERE reqId=%s", (cId,))
    except:
        pass

    try:
        db.execute("DELETE FROM reparation_tax WHERE loser=%s OR winner=%s", (cId, cId))
    except:
        pass

    try:
        db.execute("DELETE FROM peace WHERE author=%s", (cId,))
    except:
        pass

    coalition_role = get_user_role(cId)
    if coalition_role != "leader":
        pass
    else:

        db.execute("SELECT colId FROM coalitions WHERE userId=%s", (cId,))
        user_coalition = db.fetchone()[0]

        db.execute("SELECT COUNT(userId) FROM coalitions WHERE role='leader' AND colId=%s", (user_coalition,))
        leader_count = int(db.fetchone()[0])

        if leader_count != 1:

            pass

        else:

            try:
                db.execute("DELETE FROM coalitions WHERE colId=%s", (user_coalition,))
                db.execute("DELETE FROM colNames WHERE id=%s", (user_coalition,))
                db.execute("DELETE FROM colBanks WHERE colid=%s", (user_coalition,))
                db.execute("DELETE FROM requests WHERE colId=%s", (user_coalition,))
            except:
                pass

    try:
        db.execute("DELETE FROM coalitions WHERE userId=%s", (cId,))
    except:
        pass

    try:
        db.execute("DELETE FROM colBanksRequests WHERE userId=%s", (cId,))
    except:
        pass

    connection.commit()
    connection.close()

    session.clear()

    return redirect("/")

@app.route("/username_available/<username>", methods=["GET"])
def username_avalaible(username):

    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    try:
        db.execute("SELECT username FROM users WHERE username=(%s)", (username,))
        username_exists = db.fetchone()[0]
        username_exists = True
    except TypeError:
        username_exists = False

    if username_exists:
        return "No"
    else:
        return "Yes"
