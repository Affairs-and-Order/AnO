# import psycopg2
import sqlite3

"""    
connection = psycopg2.connect(database="postgres", user="postgres", password="ano", host="127.0.0.1", port="5432")
db = connection.cursor()
"""

connection = sqlite3.connect('aao.db')  # connects to db
db = connection.cursor()  # creates the cursor for db connection
print("Connection Successful!")

tables = ["air", "coalitions", "colNames", "ground", "provinces",
"requests", "special", "stats", "users", "water", "offers", "resources"]

for i in tables:
    with open(f"sqlite/schemas/all/{i}.txt") as file:
        db.execute(f"DROP TABLE IF EXISTS {i}")
        db.execute(file.read())
        print(file.read())
        print(f"Recreated table {i}")
    connection.commit()

