from app import app
from flask import request, redirect, session
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

# Getting all the policy numbers from a request form
def get_policies(type, prange, form):
    policies = []
    for i in range(1, prange+1):
        value = form.get(f"{type}{i}")
        if (value != None): policies.append(int(value))
    return policies

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

    military = get_policies("soldiers", 7, request.form)
    education = get_policies("education", 6, request.form)

    db.execute("UPDATE policies SET soldiers=%s WHERE user_id=%s", (military, cId))
    db.execute("UPDATE policies SET education=%s WHERE user_id=%s", (education, cId))

    conn.commit()
    conn.close()

    return redirect("/my_country")
