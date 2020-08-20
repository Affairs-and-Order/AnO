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


@login_required
@app.route("/coalitions", methods=["GET", "POST"])
def coalitions():
    if request.method == "GET":

        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        coalitions = db.execute("SELECT id FROM colNames").fetchall()

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

    else:

        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        search = request.form.get("search")

        resultId = db.execute(
            "SELECT id FROM colNames WHERE name LIKE (?)", ('%'+search+'%',)).fetchall()
        ids = []
        names = []
        members = []
        types = []
        influences = []

        for i in resultId:
            names.append(db.execute(
                "SELECT name FROM colNames WHERE id=(?)", (i[0],)).fetchone()[0])
            ids.append(db.execute(
                "SELECT id FROM colNames WHERE id=(?)", (i[0],)).fetchone()[0])
            members.append(db.execute(
                "SELECT count(userId) FROM coalitions WHERE colId=(?)", (i[0],)).fetchone()[0])
            types.append(db.execute(
                "SELECT type FROM colNames WHERE id=(?)", (i[0],)).fetchone()[0])
            influences.append(get_coalition_influence(i[0]))

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
