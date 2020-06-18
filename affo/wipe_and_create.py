import sqlite3
    
conn = sqlite3.connect('aao.db')
db = conn.cursor()

tables = ["air", "coalitions", "colNames", "ground", "provinces",
"requests", "special", "stats", "users", "water"]

for i in tables:
    db.execute(f"DROP TABLE {i}")
    txt = open(f"raw/{i}.txt", "r")
    db.execute(txt.read())
