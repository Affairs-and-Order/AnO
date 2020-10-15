import psycopg2
    
connection = psycopg2.connect(
    database="ano",
    user="postgres",
    password="q",
    host="localhost",
    port="5432")
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