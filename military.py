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
@app.route("/military", methods=["GET", "POST"])
def military():
    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()
    cId = session["user_id"]
    if request.method == "GET":  # maybe optimise this later with css anchors
        # ground
        tanks = db.execute(
            "SELECT tanks FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        soldiers = db.execute(
            "SELECT soldiers FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        artillery = db.execute(
            "SELECT artillery FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        # air
        bombers = db.execute(
            "SELECT bombers FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        fighters = db.execute(
            "SELECT fighters FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        apaches = db.execute(
            "SELECT apaches FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        # water
        destroyers = db.execute(
            "SELECT destroyers FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        cruisers = db.execute(
            "SELECT cruisers FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        submarines = db.execute(
            "SELECT submarines FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        # special
        spies = db.execute(
            "SELECT spies FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        icbms = db.execute(
            "SELECT ICBMs FROM military WHERE id=(?)", (cId,)).fetchone()[0]
        nukes = db.execute(
            "SELECT nukes FROM military WHERE id=(?)", (cId,)).fetchone()[0]

        return render_template("military.html", tanks=tanks, soldiers=soldiers, artillery=artillery,
                               bombers=bombers, apaches=apaches, fighters=fighters,
                               destroyers=destroyers, cruisers=cruisers, submarines=submarines,
                               spies=spies, icbms=icbms, nukes=nukes
                               )


person = {"name": "galaxy"}
# easter egg probably or it has something to do with mail xD || aw thats nice test
person["message"] = "Thanks guys :D, you are all so amazing."


@login_required
@app.route("/<way>/<units>", methods=["POST"])
def military_sell_buy(way, units):  # WARNING: function used only for military

    if request.method == "POST":

        cId = session["user_id"]

        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        allUnits = ["soldiers", "tanks", "artillery",
                    "bombers", "fighters", "apaches"
                    "destroyers", "cruisers", "submarines",
                    "spies", "icbms", "nukes"]  # list of allowed units

        if units not in allUnits:
            return error("No such unit exists.", 400)

        mil_dict = {

            ## LAND

            "soldiers_price": 200, # Cost 200
            "soldiers_resource": {"rations": 2},

            "tanks_price": 8000, # Cost 8k 
            "tanks_resource": {"steel": 5},

            "artillery_price": 16000, # Cost 16k 
            "artillery_resource": {"steel": 12},

            ## AIR

            "bombers_price": 25000, # Cost 25k 
            "bombers_resource": {"aluminium": 20},
            "bombers_resource2": {"steel": 5},
            "bombers_resource3": {"components": 6},

            "fighters_price": 35000, # Cost 35k 
            "fighters_resource": {"aluminium": 12},
            "fighters_resource2": {"components": 3},

            "apaches_price": 32000, # Cost 32k
            "apaches_resource": {"aluminium": 8},
            "apaches_resource2": {"steel": 2},
            "apaches_resource3": {"components": 4},

            ## WATER

            "destroyers_price": 30000, # Cost 30k
            "destroyers_resource": {"steel": 30},
            "destroyers_resource2": {"components": 7},

            "cruisers_price": 55000, # Cost 55k
            "cruisers_resource": {"steel": 25},
            "cruisers_resource2": {"components": 4},

            "submarines_price": 45000, # Cost 45k
            "submarines_resource": {"steel": 20},
            "submarines_resource2": {"components": 8},

            ## SPECIAL

            "spies_price": 25000, # Cost 25k
            "spies_resource": {"rations": 50}, # Costs 50 rations

            "ICBMs_price": 4000000, # Cost 4 million
            "ICMBs_resource": {"steel": 350}, # Costs 350 steel

            "nukes_price": 12000000, # Cost 12 million
            "nukes_resource": {"uranium": 800}, # Costs 800 uranium
            "nukes_resource2": {"steel": 600} # Costs 600 steel

        }

        price = mil_dict[f"{units}_price"]

        resource1_data = next(iter(mil_dict[f'{units}_resource'].items()))

        resource1 = resource1_data[0]
        resource1_amount = resource1_data[1]

        try:
            resource2_data = next(iter(mil_dict[f'{units}_resource2'].items()))
            
            resource2 = resource2_data[0]
            resource2_amount = resource2_data[1]

            second_resource = True
        except KeyError:
            second_resource = False

        try:
            resource3_data = next(iter(mil_dict[f'{units}_resource3'].items()))
            
            resource3 = resource3_data[0]
            resource3_amount = resource3_data[1]

            third_resource = True
        except KeyError:
            third_resource = False


        gold = db.execute(
            "SELECT gold FROM stats WHERE id=(?)", (cId,)).fetchone()[0]
        wantedUnits = request.form.get(units)
        curUnStat = f'SELECT {units} FROM military WHERE id=?'
        totalPrice = int(wantedUnits) * price
        currentUnits = db.execute(curUnStat, (cId,)).fetchone()[0]

        if way == "sell":

            if int(wantedUnits) > int(currentUnits):  # checks if unit is legits
                return redirect("/too_much_to_sell")  # seems to work

            unitUpd = f"UPDATE military SET {units}=(?) WHERE id=(?)"
            db.execute(unitUpd, (int(currentUnits) - int(wantedUnits), cId))
            db.execute("UPDATE stats SET gold=(?) WHERE id=(?)", ((
                int(gold) + int(wantedUnits) * int(price)), cId,))  # clean
            flash(f"You sold {wantedUnits} {units}")

        elif way == "buy":

            if int(totalPrice) > int(gold):  # checks if user wants to buy more units than he has gold
                return redirect("/too_many_units")

            db.execute("UPDATE stats SET gold=(?) WHERE id=(?)",
                       (int(gold)-int(totalPrice), cId,))

            updStat = f"UPDATE military SET {units}=(?) WHERE id=(?)"
            # fix weird table
            db.execute(updStat, ((int(currentUnits) + int(wantedUnits)), cId))
            flash(f"You bought {wantedUnits} {units}")


            ### TODO: optimize this code by turning this into a function
            # Updating the first resoure
            current_resource1_statement = f"SELECT {resource1} FROM resources WHERE id=(?)"
            current_resource1 = db.execute(current_resource1_statement, (cId,)).fetchone()[0]

            if current_resource1 < resource1_amount:
                return error(400, "You don't have enough resources")

            new_resource1 = current_resource1 - resource1_amount
            
            resource1_update_statement = f"UPDATE resources SET {resource1}=(?) WHERE id=(?)"
            db.execute(resource1_update_statement, (new_resource1, cId,))

            # Updating the second resource (if exists)
            if second_resource == True:

                current_resource2_statement = f"SELECT {resource2} FROM resources WHERE id=(?)"
                current_resource2 = db.execute(current_resource2_statement, (cId,)).fetchone()[0]

                if current_resource2 < resource2_amount:
                    return error(400, "You don't have enough resources")

                new_resource2 = current_resource2 - resource2_amount
                
                resource2_update_statement = f"UPDATE resources SET {resource2}=(?) WHERE id=(?)"
                db.execute(resource2_update_statement, (new_resource2, cId,))

            if third_resource == True:

                current_resource3_statement = f"SELECT {resource3} FROM resources WHERE id=(?)"
                current_resource3 = db.execute(current_resource3_statement, (cId,)).fetchone()[0]

                if current_resource3 < resource3_amount:
                    return error(400, "You don't have enough resources")

                new_resource3 = current_resource3 - resource3_amount
                
                resource3_update_statement = f"UPDATE resources SET {resource3}=(?) WHERE id=(?)"
                db.execute(resource3_update_statement, (new_resource3, cId,))

        else:
            return error(404, "Page not found")

        connection.commit()
        connection.close()

        return redirect("/military")