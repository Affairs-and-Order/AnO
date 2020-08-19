import sqlite3

conn = sqlite3.connect('aao.db') # connects to db
db = conn.cursor()

session = "String"
inColit = db.execute("SELECT colId FROM coalitions WHERE userId=(?)", (session, )).fetchone()[0]

username = "string"

user = db.execute("SELECT * FROM users WHERE username = (?)", (username,)).fetchone()