from app import app
from helpers import login_required, error
import sqlite3
from flask import Flask, request, render_template, session, redirect, flash


@login_required
@app.route("/market", methods=["GET", "POST"])
def market():
    if request.method == "GET":

        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        offer_ids_list = db.execute(
            "SELECT offer_id FROM offers ORDER BY price ASC").fetchall()

        try:
            filter_resource = request.values.get("filtered_resource")
        except TypeError:
            filter_resource = None

        if filter_resource != None:

            resources = [
                "rations", "oil", "coal", "uranium", "bauxite", "lead", "copper",
                "lumber", "components", "steel", "consumer_goods", "aluminium",
                "gasoline", "ammunition"]

            if filter_resource not in resources:  # Checks if the resource the user selected actually exists
                return error(400, "No such resource")

        ids = []
        names = []
        resources = []
        amounts = []
        prices = []
        total_prices = []
        offer_ids = []

        for i in offer_ids_list:

            resource = db.execute(
                "SELECT resource FROM offers WHERE offer_id=(?)", (i[0],)).fetchone()[0]

            if filter_resource != None:
                if filter_resource == resource:
                    pass
                else:
                    continue

            offer_ids.append(i[0])

            user_id = db.execute(
                "SELECT user_id FROM offers WHERE offer_id=(?)", (i[0],)).fetchone()[0]
            ids.append(user_id)

            name = db.execute(
                "SELECT username FROM users WHERE id=(?)", (user_id,)).fetchone()[0]
            names.append(name)

            resource = db.execute(
                "SELECT resource FROM offers WHERE offer_id=(?)", (i[0],)).fetchone()[0]
            resources.append(resource)

            amount = db.execute(
                "SELECT amount FROM offers WHERE offer_id=(?)", (i[0],)).fetchone()[0]
            amounts.append(amount)

            price = db.execute(
                "SELECT price FROM offers WHERE offer_id=(?)", (i[0],)).fetchone()[0]
            prices.append(price)

            total_price = price * amount
            total_prices.append(total_price)

        connection.close()

        offers = zip(ids, names, resources, amounts,
                     prices, offer_ids, total_prices)

        return render_template("market.html", offers=offers)


@login_required
@app.route("/buy_offer/<offer_id>", methods=["POST"])
def buy_market_offer(offer_id):

    connection = sqlite3.connect('affo/aao.db')
    db = connection.cursor()

    cId = session["user_id"]

    amount_wanted = request.form.get(f"amount_{offer_id}")

    if offer_id.isnumeric() is False or amount_wanted.isnumeric() is False:
        return error(400, "Values must be numeric")

    offer = db.execute(
        "SELECT resource, amount, price, user_id FROM offers WHERE offer_id=(?)", (offer_id,)).fetchone()

    seller_id = int(offer[3])

    resource = offer[0]

    if int(amount_wanted) > int(offer[1]):
        return error(400, "Amount wanted cant be higher than total amount")

    user_gold = db.execute(
        "SELECT gold FROM stats WHERE id=(?)", (cId,)).fetchone()[0]

    # checks if buyer doesnt have enough gold for buyin
    if int(amount_wanted) * int(offer[2]) > int(user_gold):

        # returns error if buyer doesnt have enough gold for buying
        return error(400, "You don't have enough gold")

    gold_sold = user_gold - (int(amount_wanted) * int(offer[2]))

    sellResStat = f"SELECT {resource} FROM resources WHERE id=(?)"
    sellTotRes = db.execute(sellResStat, (seller_id,)).fetchone()[0]

    db.execute("UPDATE stats SET gold=(?) WHERE id=(?)", (gold_sold, cId))

    # statement for getting the current resource from the buyer
    currentBuyerResource = f"SELECT {resource} FROM resources WHERE id=(?)"
    buyerResource = db.execute(currentBuyerResource, (cId,)).fetchone()[
        0]  # executes the statement

    # generates the number of the resource the buyer should have
    newBuyerResource = int(buyerResource) + int(amount_wanted)

    # statement for giving the user the resource bought
    buyUpdStat = f"UPDATE resources SET {resource}=(?) WHERE id=(?)"
    db.execute(buyUpdStat, (newBuyerResource, cId))  # executes the statement

    new_offer_amount = (int(offer[1]) - int(amount_wanted))

    if new_offer_amount == 0:
        db.execute("DELETE FROM offers WHERE offer_id=(?)", (offer_id,))
    else:
        db.execute("UPDATE offers SET amount=(?) WHERE offer_id=(?)",
                   (new_offer_amount, offer_id))

    # updates the offer with the new amount

    connection.commit()  # commits the connection
    connection.close()  # closes the connection

    # lol this whole function is a fucking shitstorm ill comment it later hopefully

    return redirect("/market")


@login_required
@app.route("/marketoffer", methods=["GET", "POST"])
def marketoffer():
    if request.method == "POST":

        cId = session["user_id"]

        connection = sqlite3.connect('affo/aao.db')
        db = connection.cursor()

        resource = request.form.get("resource")
        amount = int(request.form.get("amount"))
        price = request.form.get("price")

        """
        if amount.isnumeric() is False or price.isnumeric() is False:
            return error(400, "You can only type numeric values into /marketoffer ")
        """

        # List of all the resources in the game
        resources = [
            "rations", "oil", "coal", "uranium", "bauxite", "lead", "copper",
            "lumber", "components", "steel", "consumer_goods", "aluminium",
            "gasoline", "ammunition"
        ]

        if resource not in resources:  # Checks if the resource the user selected actually exists
            return error(400, "No such resource")

        if amount < 1:  # Checks if the amount is negative
            return error(400, "Amount must be greater than 0")

        # possible sql injection posibility TODO: look into this
        rStatement = f"SELECT {resource} FROM resources WHERE id=(?)"
        realAmount = int(db.execute(rStatement, (cId,)).fetchone()[0])
        if amount > realAmount:  # Checks if user wants to sell more than he has
            return error("400", "Selling amount is higher than actual amount You have.")

        # Calculates the resource amount the seller should have
        newResourceAmount = realAmount - amount

        upStatement = f"UPDATE resources SET {resource}=(?) WHERE id=(?)"
        db.execute(upStatement, (newResourceAmount, cId))

        # Creates a new offer
        db.execute("INSERT INTO offers (user_id, resource, amount, price) VALUES (?, ?, ?, ?)",
                   (cId, resource, int(amount), int(price), ))

        connection.commit()  # Commits the data to the database
        connection.close()  # Closes the connection
        return redirect("/market")
    else:
        return render_template("marketoffer.html")
