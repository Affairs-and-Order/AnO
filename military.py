# FULLY MIGRATED

from flask import request, render_template, session, redirect, flash
from helpers import login_required, error
import psycopg2
# Game.ping() # temporarily removed this line because it might make celery not work
from app import app
from attack_scripts import Military
from dotenv import load_dotenv
load_dotenv()
import os

@app.route("/military", methods=["GET", "POST"])
@login_required
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

        # finding daily limits through finding number of each military building in proinfra tables that belong to a user
        # The info of which proinfra tables belong to a user is in provinces table
        limits = Military.get_limits(cId)

        return render_template("military.html", units=units, limits=limits)

@app.route("/<way>/<units>", methods=["POST"])
@login_required
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

        wantedUnits = int(request.form.get(units))

        if wantedUnits < 1:
            return error(400, "You cannot buy or sell less than 1 unit")

        mil_dict = {

            ## LAND

            "soldiers_price": 200, # Cost 200
            "soldiers_resource": {"rations": 0},
            "soldiers_manpower": 1,

            "tanks_price": 8000, # Cost 8k
            "tanks_resource": {"steel": 5},
            "tanks_resource2": {"components": 5},
            "tanks_manpower": 4,

            "artillery_price": 16000, # Cost 16k
            "artillery_resource": {"steel": 12},
            "artillery_resource2": {"components": 3},
            "artillery_manpower": 2,

            ## AIR

            "bombers_price": 25000, # Cost 25k
            "bombers_resource": {"aluminium": 20},
            "bombers_resource2": {"steel": 5},
            "bombers_resource3": {"components": 6},
            "bombers_manpower": 1,

            "fighters_price": 35000, # Cost 35k
            "fighters_resource": {"aluminium": 12},
            "fighters_resource2": {"components": 3},
            "fighters_manpower": 1,

            "apaches_price": 32000, # Cost 32k
            "apaches_resource": {"aluminium": 8},
            "apaches_resource2": {"steel": 2},
            "apaches_resource3": {"components": 4},
            "apaches_manpower": 1,

            ## WATER

            "destroyers_price": 30000, # Cost 30k
            "destroyers_resource": {"steel": 30},
            "destroyers_resource2": {"components": 7},
            "destroyers_manpower": 6,

            "cruisers_price": 55000, # Cost 55k
            "cruisers_resource": {"steel": 25},
            "cruisers_resource2": {"components": 4},
            "cruisers_manpower": 5,

            "submarines_price": 45000, # Cost 45k
            "submarines_resource": {"steel": 20},
            "submarines_resource2": {"components": 8},
            "submarines_manpower": 6,

            ## SPECIAL

            "spies_price": 25000, # Cost 25k
            "spies_resource": {"rations": 50}, # Costs 50 rations
            "spies_manpower": 0,

            "icbms_price": 4000000, # Cost 4 million
            "icbms_resource": {"steel": 350}, # Costs 350 steel
            "icbms_manpower": 0,

            "nukes_price": 12000000, # Cost 12 million
            "nukes_resource": {"uranium": 800}, # Costs 800 uranium
            "nukes_resource2": {"steel": 600}, # Costs 600 steel
            "nukes_manpower": 0,
        }

        iterable_resources = []

        price = mil_dict[f"{units}_price"]

        resource1_data = list(mil_dict[f'{units}_resource'].items())[0]

        resource1 = resource1_data[0]
        resource1_amount = resource1_data[1]

        resource_dict = {}

        iterable_resources.append(1)

        resource_dict.update({'resource_1': {'resource': resource1, 'amount': resource1_amount}})

        try:
            resource2_data = list(mil_dict[f'{units}_resource2'].items())[0]

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

        totalPrice = wantedUnits * price

        curUnStat = str(f"SELECT {units} FROM military " + "WHERE id=%s")
        db.execute(curUnStat, (cId,))
        currentUnits = db.fetchone()[0]

        if way == "sell":

            if int(wantedUnits) > int(currentUnits):  # checks if unit is legits
                return error(400, "You don't have enough units to sell")

            unitUpd = str(f"UPDATE military SET {units}=" + "%s WHERE id=%s")
            db.execute(unitUpd, (int(currentUnits) - int(wantedUnits), cId))

            db.execute("UPDATE stats SET gold=(%s) WHERE id=(%s)", ((int(gold) + totalPrice), cId,))  # clean
            flash(f"You sold {wantedUnits} {units}")

            def update_resource_plus(x):

                resource = resource_dict[f'resource_{x}']['resource']
                resource_amount = resource_dict[f'resource_{x}']['amount']

                current_resource_statement = str(f"SELECT {resource} " + "FROM resources WHERE id=%s")
                db.execute(current_resource_statement, (cId,))
                current_resource = int(db.fetchone()[0])

                new_resource = current_resource + (resource_amount * wantedUnits)

                if new_resource < 0:
                    return error(400, f"You don't have enough {resource}")

                resource_update_statement = f"UPDATE resources SET {resource}" + "=%s WHERE id=%s"
                db.execute(resource_update_statement, (new_resource, cId,))

            for resource_number in range(1, (len(iterable_resources) + 1)):
                update_resource_plus(resource_number)

        elif way == "buy":

            wantedUnits = int(wantedUnits)
            limits = Military.get_limits(cId)

            if wantedUnits > limits[units]:
                return error(400, "You exceeded the unit buy limit, you might want to buy more military buildings.")

            if int(totalPrice) > int(gold):  # checks if user wants to buy more units than he has gold
                return error(400, "Don't have enough gold for that")

            def update_resource_minus(x):

                resource = resource_dict[f'resource_{x}']['resource']
                resource_amount = resource_dict[f'resource_{x}']['amount']

                current_resource_statement = f"SELECT {resource} FROM resources WHERE id=%s"
                db.execute(current_resource_statement, (cId,))
                current_resource = int(db.fetchone()[0])

                if current_resource < resource_amount * wantedUnits:
                    return -1

                new_resource = current_resource - (resource_amount * wantedUnits)

                # TODO: roll back when error
                # TODO; this may cause problems because it decreases the resource amount when: then previous didn't trow error therefore it is decreased but the second returned error
                # so the user reourse is decreased but the user hasn't got anything for that price
                resource_update_statement = f"UPDATE resources SET {resource}" + "=%s WHERE id=%s"
                db.execute(resource_update_statement, (new_resource, cId,))

            for resource_number in range(1, (len(iterable_resources) + 1)):
                err = update_resource_minus(resource_number)

                # IF error is returned
                if err == -1:
                    return error(400, "You don't have enough resources")

            db.execute("UPDATE stats SET gold=(%s) WHERE id=(%s)", (int(gold)-int(totalPrice), cId,))
            # fix weird table
            db.execute(f"UPDATE military SET {units}=%s WHERE id=%s", (int(currentUnits)+wantedUnits, cId))

            db.execute("SELECT manpower FROM military WHERE id=(%s)", (cId,))
            manpower = db.fetchone()[0]

            db.execute("UPDATE military SET manpower=(%s) WHERE id=(%s)", (manpower-wantedUnits*mil_dict[f"{units}_manpower"], cId))

        else:
            return error(404, "Page not found")

        connection.commit()
        connection.close()

        return redirect("/military")
