import os
from dotenv import load_dotenv
load_dotenv()
import psycopg2

def reset_user(cId):
    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = conn.cursor()

    # Military
    units = ["soldiers", "artillery", "tanks", "bombers",
    "fighters", "apaches", "spies", "ICBMs", "nukes", "destroyers", "cruisers",
    "submarines"]
    for unit in units:
        mil_query = f"UPDATE military SET {unit}=0" + " WHERE id=%s"
        db.execute(mil_query, (cId,))

    db.execute("UPDATE military SET manpower=100 WHERE id=%s", (cId,))
    db.execute("UPDATE military SET defcon=1 WHERE id=%s", (cId,))
    print("Reset military units, manpower, etc")

    # Player resources
    resources = [
        "oil", "coal", "uranium", "bauxite", "lead", "copper", "iron",
        "components", "consumer_goods", "gasoline", "ammunition"
    ]

    for resource in resources:
        rss_query = f"UPDATE resources SET {resource}=0" + " WHERE id=%s"
        db.execute(rss_query, (cId,))

    db.execute("UPDATE resources SET rations=800 WHERE id=%s", (cId,))
    db.execute("UPDATE resources SET lumber=400 WHERE id=%s", (cId,))
    db.execute("UPDATE resources SET steel=250 WHERE id=%s", (cId,))
    db.execute("UPDATE resources SET aluminium=200 WHERE id=%s", (cId,))
    db.execute("UPDATE stats SET gold=20000000 WHERE id=%s", (cId,))
    print("Updated players resources and money")

    # Market
    db.execute("DELETE FROM offers WHERE user_id=%s", (cId,))
    db.execute("DELETE FROM trades WHERE offerer=%s OR offeree=%s", (cId, cId))
    print("Deleted market data")

    # Provinces
    db.execute("SELECT id FROM provinces WHERE userid=%s", (cId,))
    provinces = db.fetchall()
    for id in provinces:
        id = id[0]
        print(f"Deleting province ({id}), user - {cId}")
        db.execute("DELETE FROM proInfra WHERE id=%s", (id,))
        db.execute("DELETE FROM provinces WHERE id=%s", (id,))

    conn.commit()
    conn.close()
