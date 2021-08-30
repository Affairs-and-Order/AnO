from flask import request, render_template, session, redirect, flash
from helpers import login_required, error
import psycopg2
from app import app
import os
from dotenv import load_dotenv
import bcrypt
from string import ascii_uppercase, ascii_lowercase, digits
from datetime import datetime
from random import SystemRandom
load_dotenv()

def generateResetCode():
    length = 64
    code = ''.join(SystemRandom().choice(ascii_uppercase + digits + ascii_lowercase) for _ in range(length))
    return code

def generateUrlFromCode(code):
    try:
        environment = os.getenv("ENVIRONMENT") # PROD
    except:
        environment = "DEV"

    if environment == "PROD": url = "https://affairsandorder.com"
    else: url = "http://localhost:5000"

    url += f"/reset_password/{code}"

    return url


def sendEmail(recipient, code):
    url = generateUrlFromCode(code)
    # Should send email here
    print(url)

# Route for requesting the reset of a password, after which the user can reset his password.
@app.route("/request_password_reset", methods=["POST"])
def request_password_reset():

    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    cId = session["user_id"]
    code = generateResetCode()
    if cId: # User is logged in
        db.execute("SELECT email FROM users WHERE id=%s", (cId,))
        email = db.fetchone()[0]
        db.execute("INSERT INTO reset_codes (url_code, user_id, created_at) VALUES (%s, %s, %s)", 
        (code, cId, int(datetime.now().timestamp())))
        sendEmail(email, code)
    else:
        ...

    connection.commit()
    connection.close()

    return redirect("/")


# Route for resetting password after request for changing password has been submitted.
@app.route("/reset_password/<code>", methods=["GET", "POST"])
def reset_password(code):

    if request.method == "GET":
        return render_template("reset_password.html", code=code)
    else:
        connection = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"))

        db = connection.cursor()

        new_password = request.form.get("password").encode("utf-8")
        print(f"Received URL code: {code}")
        try:
            db.execute("SELECT user_id FROM reset_codes WHERE url_code=%s", (code,))
            user_id = db.fetchone()[0]
        except:
            return error(400, "No such code exists.")

        hashed = bcrypt.hashpw(new_password, bcrypt.gensalt(14)).decode("utf-8")
        db.execute("UPDATE users SET hash=%s WHERE id=%s", (hashed, user_id))

        db.execute("DELETE FROM reset_codes WHERE url_code=%s", (code,))

        connection.commit()
        connection.close()

        return redirect("/account")

@app.route("/change", methods=["POST"])
@login_required
def change():

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
    name = request.form.get("name")

    if not password:
        return error(400, "No password provided")

    db.execute("SELECT hash FROM users WHERE id=%s", (cId,))
    hash = db.fetchone()[0].encode("utf-8")

    if bcrypt.checkpw(password, hash):
        if email:
            db.execute("UPDATE users SET email=%s WHERE id=%s", (email, cId))
        if name:
            db.execute("UPDATE users SET username=%s WHERE id=%s", (name, cId))
    else:
        return error(401, "Incorrect password")

    connection.commit()
    connection.close()

    return redirect("/account")