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


# rawCol (for easy finding using CTRL + F)
@login_required
@app.route("/coalition/<colId>", methods=["GET"])
def coalition(colId):
    if request.method == "GET":

        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        cId = session["user_id"]

        name = db.execute(
            "SELECT name FROM colNames WHERE id=(?)", (colId,)).fetchone()[0]
        colType = db.execute(
            "SELECT type FROM colNames WHERE id=(?)", (colId,)).fetchone()[0]
        members = db.execute(
            "SELECT COUNT(userId) FROM coalitions WHERE colId=(?)", (colId,)).fetchone()[0]
        total_influence = get_coalition_influence(colId)
        average_influence = total_influence / members

        # names = db.execute("SELECT username FROM users WHERE id = (SELECT userId FROM coalitions WHERE colId=(?))", (session["user_id"], )).fetchall()

        leader = db.execute("SELECT leader FROM colNames WHERE id=(?)", (colId,)).fetchone()[0]  # The id of the coalition leader
        leaderName = db.execute("SELECT username FROM users WHERE id=(?)", (leader,)).fetchone()[0]

        treaties = db.execute("SELECT name FROM treaty_ids").fetchall()

        if leader == cId:
            userLeader = True
        else:
            userLeader = False

        requestMessages = db.execute(
            "SELECT message FROM requests WHERE colId=(?)", (colId,)).fetchall()
        requestIds = db.execute(
            "SELECT reqId FROM requests WHERE colId=(?)", (colId,)).fetchall()
        requestNames = db.execute(
            "SELECT username FROM users WHERE id=(SELECT reqId FROM requests WHERE colId=(?))", (colId,)).fetchall()

        requests = zip(requestIds, requestNames, requestMessages)

        description = db.execute(
            "SELECT description FROM colNames WHERE id=(?)", (colId,)).fetchone()[0]

        colType = db.execute(
            "SELECT type FROM colNames WHERE id=(?)", (colId,)).fetchone()[0]

        try:
            userInCol = db.execute(
                "SELECT userId FROM coalitions WHERE userId=(?)", (cId,)).fetchone()[0]
            userInCol = True
        except:
            userInCol = False

        try:
            userInCurCol = db.execute(
                "SELECT userId FROM coalitions WHERE userId=(?) AND colId=(?)", (cId, colId)).fetchone()[0]
            userInCurCol = True
        except:
            userInCurCol = False

        connection.close()

        return render_template("coalition.html", name=name, colId=colId, members=members,
                               description=description, colType=colType, userInCol=userInCol, userLeader=userLeader,
                               requests=requests, userInCurCol=userInCurCol, treaties=treaties, total_influence=total_influence,
                               average_influence=average_influence, leaderName=leaderName, leader=leader)


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
                colId = db.execute(
                    "SELECT id FROM colNames WHERE name = (?)", (name,)).fetchone()[0]
                db.execute(
                    "INSERT INTO coalitions (colId, userId) VALUES (?, ?)", (colId, session["user_id"],))

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

    leader = db.execute(
        "SELECT leader FROM colNames WHERE id=(?)", (colId,)).fetchone()[0]

    if cId == leader:
        return error(400, "Can't leave coalition, you're the leader")

    db.execute(
        "DELETE FROM coalitions WHERE userId=(?) AND colId=(?)", (cId, colId))

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
        coalition = ""

    connection.close()

    if len(str(coalition)) == 0:
        return redirect("/")  # Redirects to home page instead of an error
    else:
        return redirect(f"/coalition/{coalition}")


@login_required
@app.route("/add/<uId>", methods=["POST"])
def adding(uId):

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()

    try:
        colId = db.execute(
            "SELECT colId FROM requests WHERE reqId=(?)", (uId,)).fetchone()[0]
    except TypeError:
        return error(400, "User hasn't posted a request to join")

    cId = session["user_id"]

    leader = db.execute(
        "SELECT leader FROM colNames WHERE id=(?)", (colId,)).fetchone()[0]

    if leader != cId:

        return error(400, "You are not the leader of the coalition")

    db.execute("DELETE FROM requests WHERE reqId=(?) AND colId=(?)", (uId, colId))
    db.execute(
        "INSERT INTO coalitions (colId, userId) VALUES (?, ?)", (colId, uId))

    connection.commit()
    connection.close()

    return redirect(f"/coalition/{ colId }")


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

    flash(f"{coalition_name} coalition was deleted.")

    return redirect("/")