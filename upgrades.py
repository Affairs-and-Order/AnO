from flask import render_template, session, redirect
from helpers import login_required, error
import psycopg2
import os
# Game.ping() # temporarily removed this line because it might make celery not work
from app import app
from dotenv import load_dotenv
load_dotenv()
from psycopg2.extras import RealDictCursor

def get_upgrades(cId): 
    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"),
        cursor_factory=RealDictCursor)
    db = conn.cursor()

    db.execute("SELECT * FROM upgrades WHERE user_id=%s", (cId,))
    upgrades = db.fetchone()

    return upgrades

@app.route("/upgrades", methods=["GET"])
@login_required
def upgrades():
    # TODO: replace the falses with db selects
    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))
    db = conn.cursor()
    cId = session["user_id"]

    upgrades = {
        'betterEngineering': None,
        'cheaperMaterials': None,
        'onlineShopping': None,
        'governmentRegulation': None,
        'nationalHealthInstitution': None,
        'highSpeedRail': None,
        'advancedMachinery': None,
        'strongerExplosives': None,
        'widespreadPropaganda': None,
        'increasedFunding': None,
        'automationIntegration': None,
        'largerForges': None,
        'lootingTeams': None,
        'organizedSupplyLines': None,
        'largeStoreHouses' : None,
        'ballisticMissileSilo': None,
        'ICBMsilo': None,
        'nuclearTestingFacility': None
    }

    for upgrade in upgrades:
        db.execute("SELECT " + upgrade + " FROM upgrades WHERE user_id=%s", (cId,))
        upgrades[upgrade] = db.fetchone()[0] 

    # working examples based on whether user has the upgrade. Database stores 0 or 1.
    # upgrades['betterEngineering'] = 0
    # upgrades['cheaperMaterials'] = 1
    # upgrades['onlineShopping'] = True
    # upgrades['governmentRegulation'] = False
    return render_template("upgrades.html", upgrades=upgrades)

@app.route("/upgrades_sb/<ttype>/<thing>", methods=["POST"])
@login_required
def upgrade_sell_buy(ttype, thing):

    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))
    db = conn.cursor()
    cId = session["user_id"]

    prices = {
        'betterEngineering': 500,
        'cheaperMaterials': 500,
        'onlineShopping': 500,
        'governmentRegulation': 500,
        'nationalHealthInstitution': 500,
        'highSpeedRail': 500,
        'advancedMachinery': 500,
        'strongerExplosives': 500,
        'widespreadPropaganda': 500,
        'increasedFunding': 500,
        'automationIntegration': 500,
        'largerForges': 500,
        'lootingTeams': 500,
        'organizedSupplyLines': 500,
        'largeStoreHouses': 500,
        'ballisticMissileSilo': 500,
        'ICBMsilo': 500,
        'nuclearTestingFacility': 500
    }       
    if ttype == "buy":
        
        price = prices[thing]

        db.execute("SELECT gold FROM stats WHERE id=%s", (cId,))
        current_gold = int(db.fetchone()[0])

        if current_gold < price:
            return error(400, "You don't have enough money")
        
        new_gold = current_gold - price

        # Removes the gold from the user
        db.execute("UPDATE stats SET gold=%s WHERE id=%s", (new_gold, cId))

        upgrade_statement = f"UPDATE upgrades SET {thing}=1 " +  "WHERE user_id=%s"
        db.execute(upgrade_statement, (cId,))

    elif ttype == "sell":
        
        price = prices[thing]

        db.execute("SELECT gold FROM stats WHERE id=%s", (cId,))
        current_gold = int(db.fetchone()[0])

        new_gold = current_gold + price

        # Removes the gold from the user
        db.execute("UPDATE stats SET gold=%s WHERE id=%s", (new_gold, cId))

        upgrade_statement = f"UPDATE upgrades SET {thing}=0 " +  "WHERE user_id=%s"
        db.execute(upgrade_statement, (cId,))

    conn.commit()
    conn.close()

    return redirect("/upgrades")
