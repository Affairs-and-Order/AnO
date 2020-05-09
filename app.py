from flask import Flask, request, render_template, session
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
        print("todo")
    else:
        return render_template("login.html")