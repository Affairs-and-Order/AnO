from flask import request, render_template, session, redirect
from src import app

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        connection = sqlite3.connect('affo/aao.db') # connects to db
        db = connection.cursor() # creates the cursor for db connection

        password = request.form.get("password") # gets the password input from the form
        username = request.form.get("username") # gets the username input from the forms

        if not username or not password: # checks if inputs are blank
            return error(400, "No Password or Username")

        user = db.execute("SELECT * FROM users WHERE username = (?)", (username,)).fetchone() # selects data about user, from users
        connection.commit()

        if user is not None and check_password_hash(user[4], password): # checks if user exists and if the password is correct
            session["user_id"] = user[0] # sets session's user_id to current user's id
            try:
                coalition = db.execute("SELECT colId FROM coalitions WHERE userId=(?)", (session["user_id"], )).fetchone()[0]
            except TypeError:
                coalition = error(404, "Page Not Found")

            # print(f"coalition = {coalition}")

            session["coalition"] = coalition
            print('User has succesfully logged in.')
            connection.commit()
            connection.close()
            return redirect("/") # redirects user to homepage

        return error(403, "Wrong password")

    else:
        return render_template("login.html") # renders login.html when "/login" is acessed via get
