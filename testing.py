import sqlite3

def username_avalaible(username):
    conn = sqlite3.connect('affo/aao.db') # connects to db
    db = conn.cursor()

    try:
        username_exists = db.execute("SELECT username FROM users WHERE username=(?)", (username,)).fetchone()[0]
        username_exists = True
    except TypeError:
        username_exists = False

    if username_exists == True:
        return "Yes"
    else:
        return "No"

username_avalaible('rt')