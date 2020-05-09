from flask import Flask, request, render_template, session, redirect
from flask_session import Session
from tempfile import mkdtemp
import sqlite3
from werkzeug.security import generate_password_hash


app = Flask(__name__)

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def index():
    if request.method == "GET":
        return render_template("index.html")

@app.route("/login")
def login():
    if request.method == "POST":
        print("todo")
    else:
        return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        connection.commit()
        if not confirmation or not password or not email or not username:
            return redirect("/") # TODO change to error
        elif password != confirmation:
            return redirect("/") # TODO change to error
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