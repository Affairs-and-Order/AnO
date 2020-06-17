import sqlite3
    
conn = sqlite3.connect('aao.db')
db = conn.cursor()

tables = ["air", "coalitions", "colNames", "ground", "provinces",
"requests", "special", "stats", "users", "water", "offers", "resources"]

for i in tables:
    with open(f"raw/{i}.txt") as file:
        db.execute(f"DROP TABLE {i}")
        print(f"Dropped table {i}")
        db.execute(file.read())
        print(f"Recreated table {i}")
        conn.commit()

