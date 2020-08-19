from flask import request, render_template, session, redirect
from src import app

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

        key = request.form.get("key")

        allKeys = db.execute("SELECT key FROM keys").fetchall()

        if password != confirmation: # checks if password is = to confirmation password
            return error(400, "Passwords must match.")
        for keys in allKeys: # lmao shitty way to do it idk why i did this im the epitomy of stupid
            if key == keys[0]: # i should've just used a fucking select statement
                hashed = generate_password_hash(password, method='pbkdf2:sha256', salt_length=32) # hashes the inputted password
                db.execute("INSERT INTO users (username, email, hash, date) VALUES (?, ?, ?, ?)", (username, email, hashed, str(datetime.date.today()))) # creates a new user || added account creation date
                user = db.execute("SELECT id FROM users WHERE username = (?)", (username,)).fetchone()
                session["user_id"] = user[0] # set's the user's "id" column to the sessions variable "user_id"
                session["logged_in"] = True

                db.execute("INSERT INTO stats (id, location) VALUES (?, ?)", ((session["user_id"]), ("Bosfront"))) #TODO  change the default location

                db.execute("INSERT INTO military (id) VALUES (?)", (session["user_id"],))
                db.execute("INSERT INTO resources (id) VALUES (?)", (session["user_id"],))

                """
                db.execute("INSERT INTO ground (id) VALUES (?)", (session["user_id"],))
                db.execute("INSERT INTO air (id) VALUES (?)", (session["user_id"],))
                db.execute("INSERT INTO water (id) VALUES (?)", (session["user_id"],))
                db.execute("INSERT INTO special (id) VALUES (?)", (session["user_id"],))
                """

                db.execute("DELETE FROM keys WHERE key=(?)", (key,)) # deletes the used key
                connection.commit()
                connection.close()
                return redirect("/")
    else:
        return render_template("signup.html")
