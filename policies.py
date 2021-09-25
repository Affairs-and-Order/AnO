from app import app
from flask import request, redirect, session
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

@app.route("/policies/update", methods=["POST"])
def policies():

    cId = session["user_id"]

    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = conn.cursor()

    military = request.form.get("military")
    education = request.form.get("education")

    db.execute("UPDATE policies SET military=%s WHERE user_id=%s", (military, cId))
    db.execute("UPDATE policies SET education=%s WHERE user_id=%s", (education, cId))

    conn.commit()
    conn.close()

    return redirect("/my_country")
