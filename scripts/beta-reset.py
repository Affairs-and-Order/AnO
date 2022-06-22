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

# Coalitions
resources = [
    "rations", "oil", "coal", "uranium", "bauxite", "lead", "copper", "iron",
    "lumber", "components", "steel", "consumer_goods", "aluminium",
    "gasoline", "ammunition"
]
db.execute("UPDATE colBanks SET money=0")
for resource in resources:
    cb_query = f"UPDATE colBanks SET {resource}=0"
    db.execute(cb_query)
print("Removed resources and money from coalition banks")
db.execute("DELETE FROM colBanksRequests")

# Military
units = ["soldiers", "artillery", "tanks", "bombers",
"fighters", "apaches", "spies", "ICBMs", "nukes", "destroyers", "cruisers",
"submarines"]
for unit in units:
    mil_query = f"UPDATE military SET {unit}=0"
    db.execute(mil_query)

db.execute("UPDATE military SET manpower=100")
db.execute("UPDATE military SET defcon=1")
print("Reset military units, manpower, etc")

# Player resources
resources = [
    "oil", "coal", "uranium", "bauxite", "lead", "copper", "iron",
    "components", "consumer_goods", "gasoline", "ammunition"
]

for resource in resources:
    rss_query = f"UPDATE resources SET {resource}=0"
    db.execute(rss_query)

db.execute("UPDATE resources SET rations=800")
db.execute("UPDATE resources SET lumber=400")
db.execute("UPDATE resources SET steel=250")
db.execute("UPDATE resources SET aluminium=200")
db.execute("UPDATE stats SET gold=20000000")
print("Updated players resources and money")

# Provinces
db.execute("DELETE FROM provinces")
db.execute("DELETE FROM proInfra")
print("Deleted province data")

# Market
db.execute("DELETE FROM offers")
db.execute("DELETE FROM trades")
print("Deleted market data")

# Wars
db.execute("DELETE FROM wars")
db.execute("DELETE FROM peace")
db.execute("DELETE FROM reparation_tax")
print("Deleted war data")

# TEMP
db.execute("DROP TABLE spyinfo")
db.execute("""CREATE TABLE spyinfo (
        id      SERIAL PRIMARY KEY NOT NULL,
        spyer   INTEGER NOT NULL,
        spyee   INTEGER NOT NULL,
        soldiers        TEXT NOT NULL DEFAULT 'false',
        tanks   TEXT NOT NULL DEFAULT 'false',
        artillery       TEXT NOT NULL DEFAULT 'false',
        bombers TEXT NOT NULL DEFAULT 'false',
        fighters        TEXT NOT NULL DEFAULT 'false',
        apaches TEXT NOT NULL DEFAULT 'false',
        cruisers        TEXT NOT NULL DEFAULT 'false',
        destroyers      TEXT NOT NULL DEFAULT 'false',
        submarines      TEXT NOT NULL DEFAULT 'false',
        spies   TEXT NOT NULL DEFAULT 'false',
        ICBMs   TEXT NOT NULL DEFAULT 'false',
        nukes   TEXT NOT NULL DEFAULT 'false',
        rations    TEXT NOT NULL DEFAULT 'false',
        bauxite TEXT NOT NULL DEFAULT 'false',
        uranium TEXT NOT NULL DEFAULT 'false',
        iron    TEXT NOT NULL DEFAULT 'false',
        coal    TEXT NOT NULL DEFAULT 'false',
        oil     TEXT NOT NULL DEFAULT 'false',
        lead    TEXT NOT NULL DEFAULT 'false',
        copper  TEXT NOT NULL DEFAULT 'false',
        lumber  TEXT NOT NULL DEFAULT 'false',
        components      TEXT NOT NULL DEFAULT 'false',
        steel   TEXT NOT NULL DEFAULT 'false',
        aluminium        TEXT NOT NULL DEFAULT 'false',
        gasoline        TEXT NOT NULL DEFAULT 'false',
        ammunition      TEXT NOT NULL DEFAULT 'false',
        consumer_goods  TEXT NOT NULL DEFAULT 'false',
        money  TEXT NOT NULL DEFAULT 'false',
        defense TEXT NOT NULL DEFAULT 'false',
        date    INTEGER NOT NULL);""")

conn.commit()
conn.close()