from flask import Flask, request, render_template, session, redirect
from flask_session import Session
from tempfile import mkdtemp
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from helpers import login_required


app = Flask(__name__)

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def index():
    if request.method == "GET":
        return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()

    if request.method == "POST":

        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        password = request.form.get("password")
        username = request.form.get("username")

        if not username or not password:
            return redirect("/error_no_pw_or_un") #TODO change to actual error
        user = db.execute("SELECT * FROM users WHERE username = (?)", (username,)).fetchone()
        connection.commit()

        if user is not None and check_password_hash(user[3], password):
            session["user_id"] = user[0]
            print('User has succesfully logged in.')
            connection.commit()
            connection.close()
            return redirect("/")
        return redirect("/error_wrong_pw")
    else:
        return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        
        # connects the db to the signup function
        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        connection.commit()
        if not confirmation or not password or not email or not username:
            return redirect("/error_blank") #TODO change to actual error
        elif password != confirmation:
            return redirect("/error_wrong_cn") #TODO change to actual error
        else:
            hashed = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
            db.execute("INSERT INTO users (username, email, hash) VALUES (?, ?, ?)", (username, email, hashed,))
            connection.commit()
            for row in db.execute("SELECT * FROM users"):
                print(row)
            connection.close()
            return redirect("/")
    else:
        return render_template("signup.html")

@login_required
@app.route("/country")
def country():
    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()
    cId = session["user_id"]
    username = db.execute("SELECT username FROM users WHERE id=(?)", (cId,)).fetchone()[0]
    connection.commit()
    return render_template("country.html", username=username, cId=cId)