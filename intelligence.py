from app import app
from flask import Flask, request, render_template, session, redirect, abort, flash, url_for
from flask_session import Session
import sqlite3
from helpers import login_required, error
from attack_scripts import Nation, Military
from units import Units
import time


@login_required
@app.route("/intelligence", methods=["GET", "POST"])
def intelligence():
    connection = sqlite3.connect("affo/aao.db")
    db = connection.cursor()
    cId = session["user_id"]

    if request.method == "GET":
        yourCountry = db.execute(
            "SELECT username FROM users WHERE id=(?)", (cId,)).fetchone()[0]
        db.close()
        connection.close()
        units = 234234
        return render_template("intelligence.html", units=units, yourCountry=yourCountry, enemyCountry="enemyCountry")
