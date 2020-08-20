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
@app.route("/update_discord", methods=["POST"])
def update_discord():

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()
    cId = session["user_id"]

    discord_username = request.form.get("discordUsername")
    db.execute("UPDATE users SET discord=(?) WHERE id=(?)",
               (discord_username, cId))

    connection.commit()
    connection.close()

    return redirect(f"/country/id={cId}")  # Redirects the user to his country
