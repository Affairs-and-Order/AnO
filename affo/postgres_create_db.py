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
    "keys", "military", "offers", "proInfra", "provinces",
    "requests", "resources", "spyinfo", "stats", "trades", "treaty_ids",
    "treaties", "users"
]

for i in tables:
    with open(f"postgres/{i}.txt") as file:
        db.execute(f"DROP TABLE IF EXISTS {i}")
        db.execute(file.read())
        print(f"Recreated table {i}")
    connection.commit()