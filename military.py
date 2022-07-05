from flask import request, render_template, session, redirect, flash
from helpers import login_required, error
import psycopg2
from app import app
from attack_scripts import Military
from dotenv import load_dotenv
load_dotenv()
import os
from helpers import get_date
from upgrades import get_upgrades
from variables import MILDICT

@app.route("/military", methods=["GET", "POST"])
@login_required
def military():

    cId = session["user_id"]

    if request.method == "GET":  # maybe optimise this later with css anchors

        simple_units = Military.get_military(cId)
        special_units = Military.get_special(cId)
        units = simple_units.copy()
        units.update(special_units)
        upgrades = get_upgrades(cId)

        # finding daily limits through finding number of each military building in proinfra tables that belong to a user
        # The info of which proinfra tables belong to a user is in provinces table
        limits = Military.get_limits(cId)

        return render_template("military.html", units=units, limits=limits, upgrades=upgrades, mildict=MILDICT)

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

        if units == "soldiers":
            db.execute("SELECT widespreadpropaganda FROM upgrades WHERE user_id=%s", (cId,))
            wp = db.fetchone()[0]
            if wp:
                MILDICT["soldiers"]["price"] *= 0.65

        # TODO: clear this mess i called code once i get the time
        # if you're reading this please excuse the messiness 

        price = MILDICT[units]["price"]

        db.execute("SELECT gold FROM stats WHERE id=%s", (cId,))
        gold = db.fetchone()[0]

        totalPrice = wantedUnits * price

        curUnStat = f"SELECT {units} FROM military " + "WHERE id=%s"
        db.execute(curUnStat, (cId,))
        currentUnits = db.fetchone()[0]

        resources = MILDICT[units]["resources"]

        if way == "sell":

            if wantedUnits > currentUnits: 
                return error(400, f"You don't have enough {units} to sell ({wantedUnits}/{currentUnits})")

            for resource, amount in resources.items():
                addResources = wantedUnits * amount
                updateResource = f"UPDATE resources SET {resource}={resource}" + "+%s WHERE id=%s"
                db.execute(updateResource, (addResources, cId,))

            unitUpd = f"UPDATE military SET {units}={units}" + "-%s WHERE id=%s"
            db.execute(unitUpd, (wantedUnits, cId,))
            db.execute("UPDATE stats SET gold=gold+%s WHERE id=%s", (totalPrice, cId,))
            db.execute("UPDATE military SET manpower=manpower+%s WHERE id=%s", (wantedUnits*MILDICT[units]["manpower"], cId))

            # flash(f"You sold {wantedUnits} {units}")
        elif way == "buy":

            limits = Military.get_limits(cId)

            if wantedUnits > limits[units]:
                return error(400, f"You exceeded the unit buy limit, you might want to buy more military buildings. You can buy {limits[units]}/{wantedUnits} {units}.")

            if totalPrice > gold:  # checks if user wants to buy more units than he has gold
                return error(400, f"You don't have enough money for that ({gold}/{totalPrice}). You need {totalPrice-gold} more money.")

            for resource, amount in resources.items():
                selectResource = f"SELECT {resource} FROM resources WHERE id=" + "%s"
                db.execute(selectResource, (cId,))
                currentResources = db.fetchone()[0]
                requiredResources = amount * wantedUnits
                
                if requiredResources > currentResources:
                    return error(400, f"You have {currentResources}/{requiredResources} {resource}, meaning you need {requiredResources-currentResources} more.")

            for resource, amount in resources.items():
                requiredResources = amount * wantedUnits
                updateResource = f"UPDATE resources SET {resource}={resource}" + "-%s WHERE id=%s"
                db.execute(updateResource, (requiredResources, cId)) 

            print(totalPrice)

            db.execute("UPDATE stats SET gold=gold-%s WHERE id=%s", (totalPrice, cId))
            updMil = f"UPDATE military SET {units}={units}" + "+%s WHERE id=%s"
            db.execute(updMil, (wantedUnits, cId))

            db.execute("UPDATE military SET manpower=manpower-%s WHERE id=%s", (wantedUnits*MILDICT[units]["manpower"], cId))

        else:
            return error(404, "Page not found")

        ####### UPDATING REVENUE #############
        if way == "buy": rev_type = "expense"
        elif way == "sell": rev_type = "revenue"
        name = f"{way.capitalize()}ing {wantedUnits} {units} for your military."
        description = ""

        db.execute("INSERT INTO revenue (user_id, type, name, description, date, resource, amount) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
        (cId, rev_type, name, description, get_date(), units, wantedUnits,))
        #######################################

        connection.commit()
        connection.close()

        return redirect("/military")
