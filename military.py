# FULLY MIGRATED

from flask import Flask, request, render_template, session, redirect, flash
from tempfile import mkdtemp
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
import datetime
import _pickle as pickle
import random
from celery import Celery
from helpers import login_required, error
import psycopg2
# from celery.schedules import crontab # arent currently using but will be later on
from helpers import get_influence, get_coalition_influence
# Game.ping() # temporarily removed this line because it might make celery not work
from app import app
from attack_scripts import Military
from dotenv import load_dotenv
load_dotenv()
import os

@login_required
@app.route("/military", methods=["GET", "POST"])
def military():
    
    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()
    cId = session["user_id"]

    if request.method == "GET":  # maybe optimise this later with css anchors
        simple_units = Military.get_military(cId)
        special_units = Military.get_special(cId)
        units = simple_units.copy()
        units.update(special_units)

        return render_template("military.html", units=units)

@login_required
@app.route("/<way>/<units>", methods=["POST"])
def military_sell_buy(way, units):  # WARNING: function used only for military

    if request.method == "POST":

        cId = session["user_id"]

        
        connection = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"))

        db = connection.cursor()

        allUnits = ["soldiers", "tanks", "artillery",
                    "bombers", "fighters", "apaches",
                    "destroyers", "cruisers", "submarines",
                    "spies", "icbms", "nukes"]  # list of allowed units

        if units not in allUnits and units != "apaches":
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
        
        iterable_resources = []

        price = mil_dict[f"{units}_price"]

        resource1_data = next(iter(mil_dict[f'{units}_resource'].items()))

        resource1 = resource1_data[0]
        resource1_amount = resource1_data[1]

        resource_dict = {}

        iterable_resources.append(1)

        resource_dict.update({'resource_1': {'resource': resource1, 'amount': resource1_amount}})

        try:
            resource2_data = next(iter(mil_dict[f'{units}_resource2'].items()))

            resource2 = resource2_data[0]
            resource2_amount = resource2_data[1]

            iterable_resources.append(2)

            resource_dict.update({'resource_2': {'resource': resource2, 'amount': resource2_amount}})

        except KeyError:
            pass

        try:
            resource3_data = next(iter(mil_dict[f'{units}_resource3'].items()))

            resource3 = resource3_data[0]
            resource3_amount = resource3_data[1]

            iterable_resources.append(3)
            
            resource_dict.update({'resource_3': {'resource': resource3, 'amount': resource3_amount}})

        except KeyError:
            pass

        db.execute("SELECT gold FROM stats WHERE id=(%s)", (cId,))
        gold = db.fetchone()[0]

        wantedUnits = request.form.get(units)
        totalPrice = int(wantedUnits) * price

        curUnStat = str(f"SELECT {units} FROM military " + "WHERE id=%s")
        db.execute(curUnStat, (cId,))
        currentUnits = db.fetchone()[0]

        if way == "sell":

            if int(wantedUnits) > int(currentUnits):  # checks if unit is legits
                return redirect("/too_much_to_sell")  # seems to work

            unitUpd = str(f"UPDATE military SET {units}=" + "%s WHERE id=%s")
            db.execute(unitUpd, (int(currentUnits) - int(wantedUnits), cId))

            db.execute("UPDATE stats SET gold=(%s) WHERE id=(%s)", ((int(gold) + int(wantedUnits) * int(price)), cId,))  # clean
            flash(f"You sold {wantedUnits} {units}")

            def update_resource_plus(x):

                resource = resource_dict[f'resource_{x}']['resource']
                resource_amount = resource_dict[f'resource_{x}']['amount']
                
                current_resource_statement = str(f"SELECT {resource} " + "FROM resources WHERE id=%s")
                db.execute(current_resource_statement, (cId,))
                current_resource = int(db.fetchone()[0])

                new_resource = current_resource + resource_amount

                resource_update_statement = f"UPDATE resources SET {resource}" + "=%s WHERE id=%s"
                db.execute(resource_update_statement, (new_resource, cId,))

            for resource_number in range(1, (len(iterable_resources) + 1)):
                update_resource_plus(resource_number)

        elif way == "buy":

            if int(totalPrice) > int(gold):  # checks if user wants to buy more units than he has gold
                return redirect("/error")

            db.execute("UPDATE stats SET gold=(%s) WHERE id=(%s)", (int(gold)-int(totalPrice), cId,))

            updStat = f"UPDATE military SET {units}" + "=%s WHERE id=%s"
            # fix weird table
            db.execute(updStat, ((int(currentUnits) + int(wantedUnits)), cId))
            flash(f"You bought {wantedUnits} {units}")

            def update_resource_minus(x):
                resource = resource_dict[f'resource_{x}']['resource']
                resource_amount = resource_dict[f'resource_{x}']['amount']
                
                current_resource_statement = f"SELECT {resource} " + "FROM resources WHERE id=%s"
                db.execute(current_resource_statement, (cId,))
                current_resource = int(db.fetchone()[0])

                if current_resource < resource_amount:
                    return error(400, "You don't have enough resources")

                new_resource = current_resource - resource_amount

                resource_update_statement = f"UPDATE resources SET {resource}" + "=%s WHERE id=%s"
                db.execute(resource_update_statement, (new_resource, cId,))

            for resource_number in range(1, (len(iterable_resources) + 1)):
                update_resource_minus(resource_number)

        else:
            return error(404, "Page not found")

        connection.commit()
        connection.close()

        return redirect("/military")
