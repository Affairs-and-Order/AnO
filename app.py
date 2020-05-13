from flask import Flask, request, render_template, session, redirect
from flask_session import Session
from tempfile import mkdtemp
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from helpers import login_required


app = Flask(__name__)

# basic cache configuration
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def index():
    if request.method == "GET":
        try: 
            uId = session["user_id"]
            uId = True
            return render_template("index.html", uId=uId)
        except KeyError:
            uId = False
            return render_template("index.html", uId=uId) # renders index.html when "/" is accesed

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        connection = sqlite3.connect('affo/aao.db') # connects to db
        db = connection.cursor()

        password = request.form.get("password") # gets the password input from the form
        username = request.form.get("username") # gets the username input from the forms

        if not username or not password: # checks if inputs are blank
            return redirect("/error_no_pw_or_un") #TODO change to actual error
        user = db.execute("SELECT * FROM users WHERE username = (?)", (username,)).fetchone() # selects data about user, from users
        connection.commit()

        if user is not None and check_password_hash(user[3], password): # checks if user exists and if the password is correct
            session["user_id"] = user[0] # sets session's user_id to current user's id
            print('User has succesfully logged in.')
            connection.commit()
            connection.close()
            return redirect("/")
        return redirect("/error_wrong_pw")
    else:
        return render_template("login.html") # renders login.html when "/login" is acessed via get

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        
        # connects the db to the signup function
        connection = sqlite3.connect('affo/aao.db') # connects to db
        db = connection.cursor()

        username = request.form.get("username") # gets corresponding form inputs
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        connection.commit()
        if not confirmation or not password or not email or not username: # checks for blank inputs
            return redirect("/error_blank") #TODO change to actual error
        elif password != confirmation: # checks if password is = to confirmation password
            return redirect("/error_wrong_cn") #TODO change to actual error
        else:
            hashed = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16) # hashes the inputted password
            db.execute("INSERT INTO users (username, email, hash) VALUES (?, ?, ?)", (username, email, hashed,)) # creates a new user
            user = db.execute("SELECT id FROM users WHERE username = (?)", (username,)).fetchone()
            session["user_id"] = user[0]
            connection.commit()
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
    username = db.execute("SELECT username FROM users WHERE id=(?)", (cId,)).fetchone()[0] # gets country's name from db
    connection.commit()
    return render_template("country.html", username=username, cId=cId)


if __name__ == "__main__":

    app.run(debug=True)