from flask import request, render_template, session, redirect, flash
from helpers import login_required, error
import psycopg2
from app import app
import os
from dotenv import load_dotenv
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

    