import sqlite3
import psycopg2
    
connection = psycopg2.connect(database="postgres", user="postgres", password="ano", host="127.0.0.1", port="5432")
db = connection.cursor()
print("Connection Successful!")

session = 2
inColit = db.execute("SELECT colId FROM coalitions WHERE userId = %s;", (session, )).fetchone()
print(inColit)

username = "ok"
user = db.execute("SELECT * FROM users WHERE username = %s", (username,))
print(user)