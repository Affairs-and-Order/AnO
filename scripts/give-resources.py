# Script for giving resources to players
import os
from dotenv import load_dotenv
load_dotenv()
import psycopg2
import sys

conn = psycopg2.connect(
    database=os.getenv("PG_DATABASE"),
    user=os.getenv("PG_USER"),
    password=os.getenv("PG_PASSWORD"),
    host=os.getenv("PG_HOST"),
    port=os.getenv("PG_PORT"))

db = conn.cursor()

resource = sys.argv[1]
amount = sys.argv[2]
user_id = sys.argv[3]

if resource in ["money", "gold"]:

    db.execute("UPDATE stats SET gold=gold+%s WHERE id=%s", (amount, user_id))

    conn.commit()
    conn.close()
elif resource == "all":

    resources = [
        "rations", "oil", "coal", "uranium", "bauxite", "lead", "copper", "iron",
        "lumber", "components", "steel", "consumer_goods", "aluminium",
        "gasoline", "ammunition"
    ]

    for resource in resources:

        resource_update = f"UPDATE resources SET {resource}={resource}" + "+%s WHERE id=%s"
        db.execute(resource_update, (amount, user_id,))

    conn.commit()
    conn.close()
else:
    print("Unrecognized resource")

