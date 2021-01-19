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
db.execute("DELETE FROM spyinfo")
db.execute("DELETE FROM reparation_tax")
print("Deleted war data")

conn.commit()
conn.close()