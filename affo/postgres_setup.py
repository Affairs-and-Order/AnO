import psycopg2
    
connection = psycopg2.connect(database="postgres", user="postgres", password="ano", host="127.0.0.1", port="5432")
db = connection.cursor()
print("Connection Successful!")

tables = ["air", "coalitions", "colNames", "ground", "provinces",
"requests", "special", "stats", "users", "water", "offers", "resources"]

for i in tables:
    with open(f"raw/{i}.txt") as file:
        db.execute(f"DROP TABLE IF EXISTS {i}")
        db.execute(file.read())
        print(f"Recreated table {i}")
        connection.commit()
