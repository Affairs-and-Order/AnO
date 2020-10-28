# FULLY MIGRATED

from flask import Flask, request, render_template, session, redirect, flash
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
import datetime
import _pickle as pickle
import random
from helpers import login_required, error
import psycopg2
import os
# from celery.schedules import crontab # arent currently using but will be later on
from helpers import get_influence, get_coalition_influence
# Game.ping() # temporarily removed this line because it might make celery not work
from app import app
from dotenv import load_dotenv
load_dotenv()

@login_required
@app.route("/upgrades", methods=["GET"])
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
    
    db.execute("SELECT betterEngineering FROM upgrades WHERE user_id=%s", (cId,))
    betterEngineering = db.fetchone()[0]

    db.execute("SELECT cheaperMaterials FROM upgrades WHERE user_id=%s", (cId,))
    cheaperMaterials = db.fetchone()[0]

    db.execute("SELECT onlineShopping FROM upgrades WHERE user_id=%s", (cId,))
    onlineShopping = db.fetchone()[0]

    db.execute("SELECT governmentRegulation FROM upgrades WHERE user_id=%s", (cId,))
    governmentRegulation = db.fetchone()[0]

    db.execute("SELECT nationalHealthInstitution FROM upgrades WHERE user_id=%s", (cId,))
    nationalHealthInstitution = db.fetchone()[0]

    db.execute("SELECT highSpeedRail FROM upgrades WHERE user_id=%s", (cId,))
    highSpeedRail = db.fetchone()[0]

    db.execute("SELECT advancedMachinery FROM upgrades WHERE user_id=%s", (cId,))
    advancedMachinery = db.fetchone()[0]

    db.execute("SELECT strongerExplosives FROM upgrades WHERE user_id=%s", (cId,))
    strongerExplosives = db.fetchone()[0]

    db.execute("SELECT widespreadPropaganda FROM upgrades WHERE user_id=%s", (cId,))
    widespreadPropaganda = db.fetchone()[0]

    db.execute("SELECT increasedFunding FROM upgrades WHERE user_id=%s", (cId,))
    increasedFunding = db.fetchone()[0]

    db.execute("SELECT automationIntegration FROM upgrades WHERE user_id=%s", (cId,))
    automationIntegration = db.fetchone()[0]

    db.execute("SELECT largerForges FROM upgrades WHERE user_id=%s", (cId,))
    largerForges = db.fetchone()[0]

    db.execute("SELECT lootingTeams FROM upgrades WHERE user_id=%s", (cId,))
    lootingTeams = db.fetchone()[0]

    db.execute("SELECT increasedFunding FROM upgrades WHERE user_id=%s", (cId,))
    increasedFunding = db.fetchone()[0]

    db.execute("SELECT organizedSupplyLines FROM upgrades WHERE user_id=%s", (cId,))
    organizedSupplyLines = db.fetchone()[0]

    db.execute("SELECT largeStorehouses FROM upgrades WHERE user_id=%s", (cId,))
    largeStorehouses = db.fetchone()[0]

    db.execute("SELECT ballisticMissileSilo FROM upgrades WHERE user_id=%s", (cId,))
    ballisticMissileSilo = db.fetchone()[0]

    db.execute("SELECT ICBMSilo FROM upgrades WHERE user_id=%s", (cId,))
    ICBMSilo = db.fetchone()[0]

    db.execute("SELECT nuclearTestingFacility FROM upgrades WHERE user_id=%s", (cId,))
    nuclearTestingFacility = db.fetchone()[0]

    upgrades = {
        'betterEngineering': betterEngineering,
        'cheaperMaterials': cheaperMaterials,
        'onlineShopping': onlineShopping,
        'governmentRegulation': governmentRegulation,
        'nationalHealthInstitution': nationalHealthInstitution,
        'highSpeedRail': highSpeedRail,
        'advancedMachinery': advancedMachinery,
        'strongerExplosives': strongerExplosives,
        'widespreadPropaganda': widespreadPropaganda,
        'increasedFunding': increasedFunding,
        'automationIntegration': automationIntegration,
        'largerForges': largerForges,
        'lootingTeams': lootingTeams,
        'organizedSupplyLines': organizedSupplyLines,
        'largeStorehouses' : largeStorehouses,
        'ballisticMissileSilo': ballisticMissileSilo,
        'ICBMSilo': ICBMSilo,
        'nuclearTestingFacility': nuclearTestingFacility
    }

    # working examples based on whether user has the upgrade. Database stores 0 or 1.
    # upgrades['betterEngineering'] = 0
    # upgrades['cheaperMaterials'] = 1
    # upgrades['onlineShopping'] = True
    # upgrades['governmentRegulation'] = False
    return render_template("upgrades.html", upgrades=upgrades)

@login_required
@app.route("/upgrades_sb/<ttype>/<thing>", methods=["POST"])
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
        'betterEngineering': 50000,
        'cheaperMaterials': 50000,
        'onlineShopping': 50000,
        'governmentRegulation': 50000,
        'nationalHealthInstitution': 50000,
        'highSpeedRail': 50000,
        'advancedMachinery': 50000,
        'strongerExplosives': 50000,
        'widespreadPropaganda': 50000,
        'increasedFunding': 50000,
        'automationIntegration': 50000,
        'largerForges': 50000,
        'lootingTeams': 50000,
        'organizedSupplyLines': 50000,
        'largeStorehouses': 50000,
        'ballisticMissileSilo': 50000,
        'ICBMSilo': 50000,
        'nuclearTestingFacility': 50000,
    }       
    if ttype == "buy":
        
        price = prices[thing]

        current_gold = db.execute("SELECT gold FROM stats WHERE id=(?)", (cId,))
        current_gold = int(db.fetchone()[0])

        if current_gold > price:
            return error(400, "You don't have enough gold")
        
        new_gold = current_gold - price

        # Removes the gold from the user
        db.execute("UPDATE stats SET gold=%s WHERE id=%s", (new_gold, cId))

        upgrade_statement = f"UPDATE upgrades SET {thing}=1 " +  "WHERE user_id=%s"
        db.execute(upgrade_statement, (cId,))

    elif ttype == "sell":
        
        price = prices[thing]

        current_gold = db.execute("SELECT gold FROM stats WHERE id=(?)", (cId,))
        current_gold = int(db.fetchone()[0])


        new_gold = current_gold + price

        # Removes the gold from the user
        db.execute("UPDATE stats SET gold=%s WHERE id=%s", (new_gold, cId))

        upgrade_statement = f"UPDATE upgrades SET {thing}=0 " +  "WHERE user_id=%s"
        db.execute(upgrade_statement, (cId,))

    conn.commit()
    conn.close()

    return redirect("/upgrades")