import sqlite3
    
conn = sqlite3.connect('aao.db')
db = conn.cursor()

tables = ["air", "coalitions", "colNames", "ground", "provinces",
"requests", "special", "stats", "users", "water", 'offers', 'keys']
"""
    db.execute(f"DROP TABLE {i}")
    txt = open(f"raw/{i}.txt", "r")
    print(f"Dropped and recreated table {i}")
    db.execute(txt.read())
    print(txt.read())"""

for i in tables:
    with open(f'raw/{i}.txt', 'r') as file:
        db.execute(f"DROP TABLE {i}")
        db.execute(file.read())
        print(f"Dropped and recreated table {i}")