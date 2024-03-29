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
    cId = session["user_id"]
    upgrades = dict(get_upgrades(cId)) # upgrades['betterEngineering'] = 0
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
        'betterEngineering': {
            "money": 254000000,
            "resources": {
                "steel": 500,
                "aluminium": 420
            }
        },
        'cheaperMaterials': {
            "money": 22000000,
            "resources": {
                "lumber": 220
            }
        },
        'onlineShopping': {
            "money": 184000000,
            "resources": {
                "steel": 600,
                "aluminium": 450,
                "lumber": 800
            }
        },
        'governmentRegulation': {
            "money": 112000000,
            "resources": {
                "steel": 980,
                "aluminium": 750,
            }
        },
        'nationalHealthInstitution': {
            "money": 95000000,
            "resources": {
                "steel": 320,
                "aluminium": 80,
                "lumber": 675
            }
        },
        'highSpeedRail': {
            "money": 220000000,
            "resources": {
                "steel": 1350,
                "aluminium": 450,
            }
        },
        'advancedMachinery': {
            "money": 180000000,
            "resources": {
                "steel": 1400,
                "aluminium": 320,
                "lumber": 850
            }
        },
        'strongerExplosives': {
            "money": 65000000,
            "resources": {}
        },
        'widespreadPropaganda': {
            "money": 150000000,
            "resources": {}
        },
        'increasedFunding': {
            "money": 225000000,
            "resources": {
                "steel": 950,
                "aluminium": 450
            }
        },
        'automationIntegration': {
            "money": 420000000,
            "resources": {
                "steel": 2200,
                "aluminium": 1150
            }
        },
        'largerForges': {
            "money": 320000000,
            "resources":  {
                "steel": 1850,
                "aluminium": 650
            }
        }
    }
    """
        'lootingTeams': 500,
        'organizedSupplyLines': 500,
        'largeStoreHouses': 500,
        'ballisticMissileSilo': 500,
        'ICBMsilo': 500,
        'nuclearTestingFacility': 500
    }
    """    

    money = prices[thing]["money"]
    resources = prices[thing]["resources"]

    if ttype == "buy": # TODO Make resources and gold into one update query.

        # Removal of money for purchase and error handling
        try:
            db.execute("UPDATE stats SET gold=gold-%s WHERE id=%s", (money, cId,))
        except psycopg2.errors.lookup("23514"): # CheckViolation error
            return error(400, "You don't have enough money to buy this upgrade.")

        # Removal of resources for purchase and error handling
        for resource, amount in resources.items():
            try:
                resource_statement = f"UPDATE resources SET {resource}={resource}" + "-%s WHERE id=%s"
                db.execute(resource_statement, (amount, cId,))
            except psycopg2.errors.lookup("23514") as e: # CheckViolation error
                estr = str(e)
                check_failed = (estr[:estr.index("_check")]).partition("_")[2]
                return error(400, f"You don't have enough {check_failed.upper()} to buy this upgrade.")
        
        upgrade_statement = f"UPDATE upgrades SET {thing}=1 " +  "WHERE user_id=%s"
        db.execute(upgrade_statement, (cId,))

    elif ttype == "sell":

        db.execute("UPDATE stats SET gold=gold+%s WHERE id=%s", (money, cId))
        for resource, amount in resources.items():
            resource_statement = f"UPDATE resources SET {resource}={resource}" + "+%s WHERE id=%s"
            db.execute(resource_statement, (amount, cId,))

        upgrade_statement = f"UPDATE upgrades SET {thing}=0 " +  "WHERE user_id=%s"
        db.execute(upgrade_statement, (cId,))

    conn.commit()
    conn.close()

    return redirect("/upgrades")
