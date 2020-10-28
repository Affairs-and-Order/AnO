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

resource = "oil"
cId = 1

statement = f"SELECT {resource} " + "FROM resources WHERE id=%s"
db.execute(statement, (cId,))
buyerResource = db.fetchone()[0]  # executes the statement

print(buyerResource)