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
@app.route("/upgrades_sb/<type>/<thing>", methods=["POST"])
def upgrade_sell_buy(type, thing):
    
    conn = sqlite3.connect('affo/aao.db')  # connects to db
    db = conn.cursor()
    cId = session["user_id"]