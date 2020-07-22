import sqlite3

connection = sqlite3.connect('affo/aao.db')
db = connection.cursor()

colId = 1

users = db.execute("SELECT id FROM users ORDER BY id").fetchall()
