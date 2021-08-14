from flask import request, render_template, session, redirect, flash
from helpers import login_required, error
import psycopg2
from app import app
import os
from dotenv import load_dotenv
import bcrypt
load_dotenv()

@app.route("/change_email", methods=["POST"])
@login_required
def change_email():

    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()
    cId = session["user_id"]

    password = request.form.get("current_password").encode("utf-8")
    email = request.form.get("email")

    db.execute("SELECT hash FROM users WHERE id=%s", (cId,))
    hash = db.fetchone()[0].encode("utf-8")

    if bcrypt.checkpw(password, hash):
        db.execute("UPDATE users SET email=%s WHERE id=%s", (email, cId))
    else:
        return error(401, "Incorrect password")

    connection.commit()
    connection.close()

    return redirect("/account")