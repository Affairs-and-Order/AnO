import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

connection = psycopg2.connect(
    database=os.getenv("PG_DATABASE"),
    user=os.getenv("PG_USER"),
    password=os.getenv("PG_PASSWORD"),
    host=os.getenv("PG_HOST"),
    port=os.getenv("PG_PORT"))

db = connection.cursor()

tables = [
    "coalitions", "colBanks", "colBanksRequests", "colNames",
    "keys", "military", "offers", "proInfra", "provinces", "upgrades",
    "requests", "resources", "spyinfo", "stats", "trades",
    "treaties", "users", "peace", "wars", "reparation_tax", "news"
]


for i in tables:
    with open(f"postgres/{i}.txt") as file:
        try:
            db.execute(f"DROP TABLE IF EXISTS {i}")            
            db.execute(file.read())
            print(f"Recreated table {i}")
        except:
            print(f"Failed to recreate table {i}")
    connection.commit()

db.execute("INSERT INTO keys (key) VALUES ('a')")
db.execute("INSERT INTO keys (key) VALUES ('b')")
db.execute("INSERT INTO keys (key) VALUES ('c')")

print("Inserted keys: a, b, c")

connection.commit()
