from flask import Flask, request, render_template, session, redirect, flash
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
import datetime
import _pickle as pickle
import random
from celery import Celery
from helpers import login_required, error
import sqlite3
# from celery.schedules import crontab # arent currently using but will be later on
from helpers import get_influence, get_coalition_influence
# Game.ping() # temporarily removed this line because it might make celery not work
from app import app

@login_required
@app.route("/upgrades", methods=["GET"])
def upgrades():
    # TODO: replace the falses with db selects
    conn = sqlite3.connect('affo/aao.db')  # connects to db
    db = conn.cursor()
    cId = session["user_id"]
    try:
        upgrades = {
            'betterEngineering': db.execute("SELECT betterEngineering FROM upgrades WHERE user_id=(?)", (cId,)).fetchone()[0],
            'cheaperMaterials': db.execute("SELECT cheaperMaterials FROM upgrades WHERE user_id=(?)", (cId,)).fetchone()[0],
            'onlineShopping': db.execute("SELECT onlineShopping FROM upgrades WHERE user_id=(?)", (cId,)).fetchone()[0],
            'governmentRegulation': db.execute("SELECT governmentRegulation FROM upgrades WHERE user_id=(?)", (cId,)).fetchone()[0],
            'nationalHealthInstitution': db.execute("SELECT nationalHealthInstitution FROM upgrades WHERE user_id=(?)", (cId,)).fetchone()[0],
            'highSpeedRail': db.execute("SELECT highSpeedRail FROM upgrades WHERE user_id=(?)", (cId,)).fetchone()[0],
            'advancedMachinery': db.execute("SELECT advancedMachinery FROM upgrades WHERE user_id=(?)", (cId,)).fetchone()[0],
            'strongerExplosives': db.execute("SELECT strongerExplosives FROM upgrades WHERE user_id=(?)", (cId,)).fetchone()[0],
            'widespreadPropaganda': db.execute("SELECT widespreadPropaganda FROM upgrades WHERE user_id=(?)", (cId,)).fetchone()[0],
            'increasedFunding': db.execute("SELECT increasedFunding FROM upgrades WHERE user_id=(?)", (cId,)).fetchone()[0],
            'automationIntegration': db.execute("SELECT automationIntegration FROM upgrades WHERE user_id=(?)", (cId,)).fetchone()[0],
            'largerForges': db.execute("SELECT largerForges FROM upgrades WHERE user_id=(?)", (cId,)).fetchone()[0],
            'lootingTeams': db.execute("SELECT lootingTeams FROM upgrades WHERE user_id=(?)", (cId,)).fetchone()[0],
            'organizedSupplyLines': db.execute("SELECT organizedSupplyLines FROM upgrades WHERE user_id=(?)", (cId,)).fetchone()[0],
            'largeStorehouses' : db.execute("SELECT largeStorehouses FROM upgrades WHERE user_id=(?)", (cId,)).fetchone()[0],
            'ballisticMissileSilo': db.execute("SELECT ballisticMissileSilo FROM upgrades WHERE user_id=(?)", (cId,)).fetchone()[0],
            'ICBMSilo': db.execute("SELECT ICBMSilo FROM upgrades WHERE user_id=(?)", (cId,)).fetchone()[0],
            'nuclearTestingFacility': db.execute("SELECT nuclearTestingFacility FROM upgrades WHERE user_id=(?)", (cId,)).fetchone()[0]
        }
        # working examples based on whether user has the upgrade. Database stores 0 or 1.
        # upgrades['betterEngineering'] = 0
        # upgrades['cheaperMaterials'] = 1
        # upgrades['onlineShopping'] = True
        # upgrades['governmentRegulation'] = False
    except:
        return "FATAL ERROR: User has no upgrades table! Contact admin to fix."
    return render_template("upgrades.html", upgrades=upgrades)

@login_required
@app.route("/upgrades_sb/<ttype>/<thing>", methods=["POST"])
def upgrade_sell_buy(ttype, thing):

    conn = sqlite3.connect('affo/aao.db')  # connects to db
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

        current_gold = int(db.execute("SELECT gold FROM stats WHERE id=(?)", (cId,)).fetchone()[0])

        if current_gold > price:
            return error(400, "You don't have enough gold")
        
        new_gold = current_gold - price

        # Removes the gold from the user
        db.execute("UPDATE stats SET gold=(?) WHERE id=(?)", (new_gold, cId))

        upgrade_statement = f"UPDATE upgrades SET {thing}=1 WHERE user_id=(?)"
        db.execute(upgrade_statement, (cId,))

    elif ttype == "sell":
        
        price = prices[thing]

        current_gold = int(db.execute("SELECT gold FROM stats WHERE id=(?)", (cId,)).fetchone()[0])

        new_gold = current_gold + price

        # Removes the gold from the user
        db.execute("UPDATE stats SET gold=(?) WHERE id=(?)", (new_gold, cId))

        upgrade_statement = f"UPDATE upgrades SET {thing}=0 WHERE user_id=(?)"
        db.execute(upgrade_statement, (cId,))

    conn.commit()
    conn.close()

    return redirect("/upgrades")