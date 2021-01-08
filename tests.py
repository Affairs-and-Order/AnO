import variables
from helpers import error
import psycopg2
import os

def give_resource(giver_id, taker_id, resource, amount):

    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))
    db = conn.cursor()

    giver_id = int(giver_id)
    taker_id = int(taker_id)

    amount = int(amount)

    resources_list = variables.RESOURCES

    # Returns error if resource doesn't exist
    if resource not in resources_list and resource != "money":
        return "No such resource"
    
    if resource in ["gold", "money"]:

        print("money")
        
        db.execute("SELECT gold FROM stats WHERE id=%s", (giver_id,))
        current_giver_money = db.fetchone()[0]

        if current_giver_money < amount:
            return "Giver doesn't have enough resources to transfer such amount."

        db.execute("UPDATE stats SET gold=gold-%s WHERE id=%s", (amount, giver_id))
        db.execute("UPDATE stats SET gold=gold+%s WHERE id=%s", (amount, taker_id))

    else:
        
        current_resource_statement = f"SELECT {resource} FROM resources WHERE " + "id=%s"
        db.execute(current_resource_statement, (giver_id,))
        current_giver_resource = db.fetchone()[0]

        if current_giver_resource < amount:
            return "Giver doesn't have enough resources to transfer such amount."

        giver_update_statement = f"UPDATE resources SET {resource}={resource}-{amount}" + " WHERE id=%s"
        db.execute(giver_update_statement, (giver_id,))

        taker_update_statement = f"UPDATE resources SET {resource}={resource}+{amount}" + " WHERE id=%s"
        db.execute(taker_update_statement, (taker_id,))

    conn.commit()
    conn.close()


give_resource(2, 3, "rations", 10)