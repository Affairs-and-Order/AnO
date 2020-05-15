import sqlite3

conn = sqlite3.connect('affo/aao.db')
db = conn.cursor()

pop = db.execute("SELECT population, id FROM stats").fetchall()

for row in pop:
    print(row[1], row[0])