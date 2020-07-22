import sqlite3

connection = sqlite3.connect('affo/aao.db')
db = connection.cursor()

colId = 1

leader = db.execute("SELECT leader FROM colNames WHERE id=(?)", (colId,)).fetchone()[0] # The id of the coalition leader
leaderProperties = db.execute("SELECT username, id FROM users WHERE id=(?)", (leader,)).fetchall()

print("Leader name:")