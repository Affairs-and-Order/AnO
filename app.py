from flask import Flask, request, render_template, session, redirect
from flask_session import Session
from tempfile import mkdtemp

app = Flask(__name__)

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def index():
    if request.method == "GET":
        return render_template("index.html")

@app.route("/signup")
def signup():
    if request.method == "POST":
        print("todo")
    else:
        return render_template("signup.html")

@app.route("/login")
def login():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not confirmation or not password or not email or not username:
            return redirect("/") # TODO change to error
        elif password != confirmation:
            return redirect("/") # TODO change to error
        else:
            print("f")
    else:
        return render_template("login.html")