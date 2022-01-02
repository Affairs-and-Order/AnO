from app import app
from helpers import login_required, error
import psycopg2
from flask import request, render_template, session, redirect, flash
import os
import variables

# TODO: implement connection passing here.
def give_resource(giver_id, taker_id, resource, amount):

    # If giver_id is bank, don't remove any resources from anyone
    # If taker_id is bank, just remove the resources from the player

    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = conn.cursor()

    if giver_id != "bank": giver_id = int(giver_id)
    if taker_id != "bank": taker_id = int(taker_id)
    amount = int(amount)

    resources_list = variables.RESOURCES

    # Returns error if resource doesn't exist
    if resource not in resources_list and resource != "money":
        return "No such resource"
    
    if resource in ["gold", "money"]:

        if giver_id != "bank":
            db.execute("SELECT gold FROM stats WHERE id=%s", (giver_id,))
            current_giver_money = db.fetchone()[0]

            if current_giver_money < amount:
                return "Giver doesn't have enough resources to transfer such amount."

            db.execute("UPDATE stats SET gold=gold-%s WHERE id=%s", (amount, giver_id))

        if taker_id != "bank":
            db.execute("UPDATE stats SET gold=gold+%s WHERE id=%s", (amount, taker_id))

    else:
        
        if giver_id != "bank":
            current_resource_statement = f"SELECT {resource} FROM resources WHERE " + "id=%s"
            db.execute(current_resource_statement, (giver_id,))
            current_giver_resource = db.fetchone()[0]

            if current_giver_resource < amount:
                return "Giver doesn't have enough resources to transfer such amount."

            giver_update_statement = f"UPDATE resources SET {resource}={resource}-{amount}" + " WHERE id=%s"
            db.execute(giver_update_statement, (giver_id,))

        if taker_id != "bank":
            taker_update_statement = f"UPDATE resources SET {resource}={resource}+{amount}" + " WHERE id=%s"
            db.execute(taker_update_statement, (taker_id,))

    conn.commit()
    conn.close()

    return True

@app.route("/market", methods=["GET", "POST"])
@login_required
def market():
    if request.method == "GET":

        # Connection
        connection = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"))

        db = connection.cursor()
        cId = session["user_id"]

        # GET Query Parameters
        try:
            filter_resource = request.values.get("filtered_resource")
        except TypeError:
            filter_resource = None

        try:
            price_type = request.values.get("price_type")
        except TypeError:
            price_type = None

        try:
            offer_type = request.values.get("offer_type")
        except TypeError:
            offer_type = None

        # Processing of query parameters into database statements
        if price_type is not None:
            list_of_price_types = ["ASC", "DESC"]

            if price_type not in list_of_price_types:
                return error(400, "No such price type")
        
        if offer_type is not None and price_type is None:  
            db.execute("SELECT offer_id FROM offers WHERE type=(%s)", (offer_type,))
            offer_ids_list = db.fetchall()

        elif offer_type is None and price_type is not None:
            offer_ids_statement = f"SELECT offer_id FROM offers ORDER BY price {price_type}"
            db.execute(offer_ids_statement)
            offer_ids_list = db.fetchall()

        elif offer_type is not None and price_type is not None:

            offer_ids_statement = "SELECT offer_id FROM offers WHERE type=%s" + f"ORDER by price {price_type}"
            db.execute(offer_ids_statement, (offer_type,))
            offer_ids_list = db.fetchall()

        elif offer_type is None and price_type is None:
            db.execute("SELECT offer_id FROM offers ORDER BY price ASC")
            offer_ids_list = db.fetchall()

        if filter_resource is not None:

            resources = variables.RESOURCES

            if filter_resource not in resources:  # Checks if the resource the user selected actually exists
                return error(400, "No such resource")

        ids = []
        types = []
        names = []
        resources = []
        amounts = []
        prices = []
        total_prices = []
        offer_ids = []

        for i in offer_ids_list:

            offer_id = i[0]

            db.execute("SELECT resource FROM offers WHERE offer_id=(%s)", (offer_id,))
            resource = db.fetchone()[0]

            if filter_resource is not None:
                if filter_resource == resource:
                    pass
                else:
                    continue

            offer_ids.append(offer_id)

            db.execute("SELECT user_id, type, resource, amount, price FROM offers WHERE offer_id=(%s)", (offer_id,))
            user_id, offer_type, resource, amount, price = db.fetchone()

            ids.append(user_id)
            types.append(offer_type)
            resources.append(resource)
            amounts.append(amount)
            prices.append(price)
            total_prices.append(price * amount)

            db.execute("SELECT username FROM users WHERE id=(%s)", (user_id,))
            name = db.fetchone()[0]
            names.append(name)

        connection.close() # Closes the connection

        offers = zip(ids, types, names, resources, amounts, prices, offer_ids, total_prices) # Zips everything into 1 list

        return render_template("market.html", offers=offers, price_type=price_type, cId=cId)

@app.route("/buy_offer/<offer_id>", methods=["POST"])
@login_required
def buy_market_offer(offer_id):

    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    cId = session["user_id"]
    amount_wanted = int(request.form.get(f"amount_{offer_id}").replace(",", ""))

    db.execute("SELECT resource, amount, price, user_id FROM offers WHERE offer_id=(%s)", (offer_id,))
    resource, total_amount, price_for_one, seller_id = db.fetchone()

    if amount_wanted < 1:
        return error(400, "Amount cannot be less than 1")

    if amount_wanted > total_amount:
        return error(400, "Amount wanted cant be higher than total amount")

    db.execute("SELECT gold FROM stats WHERE id=(%s)", (cId,))
    buyers_gold = int(db.fetchone()[0])

    total_price = amount_wanted * price_for_one

    if total_price > buyers_gold: # Checks if buyer doesnt have enough gold for buyin
        return error(400, "You don't have enough money.") # Returns error if true

    give_resource("bank", cId, resource, amount_wanted) # Gives the resource
    give_resource(cId, seller_id, "money", total_price) # Gives the money

    new_offer_amount = total_amount - amount_wanted

    if new_offer_amount == 0:
        db.execute("DELETE FROM offers WHERE offer_id=(%s)", (offer_id,))
    else:
        db.execute("UPDATE offers SET amount=(%s) WHERE offer_id=(%s)", (new_offer_amount, offer_id))

    connection.commit() # Commits the connection
    connection.close() # Closes the connection

    return redirect("/market")

@app.route("/sell_offer/<offer_id>", methods=["POST"])
@login_required
def sell_market_offer(offer_id):
  
    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = conn.cursor()

    seller_id = session["user_id"]
    amount_wanted = int(request.form.get(f"amount_{offer_id}"))

    if not offer_id.isnumeric():
        return error(400, "Values must be numeric")

    db.execute("SELECT resource, amount, price, user_id FROM offers WHERE offer_id=(%s)", (offer_id,))
    resource, total_amount, price_for_one, buyer_id = db.fetchone()

    # Sees how much of the resource the seller has
    resource_statement = f"SELECT {resource} FROM resources " + "WHERE id=%s"
    db.execute(resource_statement, (seller_id,))
    sellers_resource = db.fetchone()[0]

    if amount_wanted < 1:
        return error(400, "Amount cannot be less than 1")

    if amount_wanted > total_amount:
        return error(400, "The amount of resources you're selling is higher than what the buyer wants")

    # Checks if it's less than what the seller wants to sell
    if sellers_resource < amount_wanted:
        return error(400, "You don't have enough of that resource")

    # Removes the resource from the seller and gives it to the buyer
    give_resource(seller_id, buyer_id, resource, amount_wanted)

    # Takes away the money used for buying from the buyer and gives it to the seller
    give_resource(buyer_id, seller_id, "money", price_for_one * amount_wanted)

    # Generates the new amount, after the buyer has got his resources from the seller
    new_offer_amount = total_amount - amount_wanted

    if new_offer_amount == 0: # Checks if the new offer amount is equal to 0
        db.execute("DELETE FROM offers WHERE offer_id=(%s)", (offer_id,)) # If yes, it deletes the offer

    else:
        db.execute("UPDATE offers SET amount=(%s) WHERE offer_id=(%s)", (new_offer_amount, offer_id)) # Updates the database with the new amount

    conn.commit()
    conn.close()

    return redirect("/market")

@app.route("/marketoffer/", methods=["GET"])
@login_required
def marketoffer():
    return render_template("marketoffer.html")

@app.route("/post_offer/<offer_type>", methods=["POST"])
@login_required
def post_offer(offer_type):

    cId = session["user_id"]
            
    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    resource = request.form.get("resource")
    amount = int(request.form.get("amount"))
    price = request.form.get("price")

    # List of all the resources in the game
    resources = variables.RESOURCES

    offer_types = ["buy", "sell"]
    if offer_type not in offer_types:
        return error(400, "Offer type must be 'buy' or 'sell'")

    if resource not in resources: # Checks if the resource the user selected actually exists
        return error(400, "No such resource")

    if amount < 1:  # Checks if the amount is negative
        return error(400, "Amount must be greater than 0")

    if offer_type == "sell":

        rStatement = f"SELECT {resource} FROM resources " + "WHERE id=%s"
        db.execute(rStatement, (cId,))
        realAmount = int(db.fetchone()[0])

        if amount > realAmount:  # Checks if user wants to sell more than he has
            return error("400", "Selling amount is higher than the amount you have.")

        # Calculates the resource amount the seller should have
        give_resource(cId, "bank", resource, amount)

        # Creates a new offer
        db.execute("INSERT INTO offers (user_id, type, resource, amount, price) VALUES (%s, %s, %s, %s, %s)", 
        (cId, offer_type, resource, int(amount), int(price), ))

    elif offer_type == "buy":

        db.execute("INSERT INTO offers (user_id, type, resource, amount, price) VALUES (%s, %s, %s, %s, %s)",
        (cId, offer_type, resource, int(amount), int(price), ))

        money_to_take_away = int(amount) * int(price)
        db.execute("SELECT gold FROM stats WHERE id=(%s)", (cId,))
        current_money = db.fetchone()[0]

        if current_money < money_to_take_away:
            return error(400, "You don't have enough money")

        give_resource(cId, "bank", "money", money_to_take_away)

    connection.commit()
    flash("You just posted a market offer")
    connection.close()  # Closes the connection
    return redirect("/market")

@app.route("/my_offers", methods=["GET"])
@login_required
def my_offers():

    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = conn.cursor()
    cId = session["user_id"]

    offers = {}

    db.execute("""
SELECT trades.offer_id, trades.price, trades.resource, trades.amount, trades.type, trades.offeree, users.username
FROM trades INNER JOIN users ON trades.offeree=users.id
WHERE trades.offerer=(%s) ORDER BY trades.offer_id ASC
""", (cId,))
    offers["outgoing"] = db.fetchall()

    db.execute("""
SELECT trades.offer_id, trades.price, trades.resource, trades.amount, trades.type, trades.offerer, users.username
FROM trades INNER JOIN users ON trades.offerer=users.id
WHERE trades.offeree=(%s) ORDER BY trades.offer_id ASC
""", (cId,))
    offers["incoming"] = db.fetchall()

    db.execute("SELECT offer_id, price, resource, amount, type FROM offers WHERE user_id=(%s) ORDER BY offer_id ASC", (cId,))
    offers["market"] = db.fetchall()

    conn.close()

    return render_template("my_offers.html", cId=cId, offers=offers)

@app.route("/delete_offer/<offer_id>", methods=["POST"])
@login_required
def delete_offer(offer_id):

    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    cId = session["user_id"]

    db.execute("SELECT user_id FROM offers WHERE offer_id=(%s)", (offer_id,))
    offer_owner = db.fetchone()[0]

    # Checks if user owns the offer
    if cId != offer_owner:
        return error(400, "You didn't post that offer")

    db.execute("SELECT type FROM offers WHERE offer_id=(%s)", (offer_id,))
    offer_type = db.fetchone()[0]

    if offer_type == "buy":

        db.execute("SELECT amount, price FROM offers WHERE offer_id=(%s)", (offer_id,))
        amount, price = db.fetchone()

        give_resource("bank", cId, "money", price * amount)

    elif offer_type == "sell":

        db.execute("SELECT amount, resource FROM offers WHERE offer_id=(%s)", (offer_id,))
        amount, resource = db.fetchone()

        give_resource("bank", cId, resource, amount)

    db.execute("DELETE FROM offers WHERE offer_id=(%s)", (offer_id,)) # Deletes the offer

    connection.commit()
    connection.close()
    
    return redirect("/my_offers")

@app.route("/post_trade_offer/<offer_type>/<offeree_id>", methods=["POST"])
@login_required
def trade_offer(offer_type, offeree_id):

    if request.method == "POST":

        cId = session["user_id"]

        connection = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"))

        db = connection.cursor()

        resource = request.form.get("resource")
        amount = int(request.form.get("amount"))
        price = int(request.form.get("price"))

        if price < 1:
            return error(400, "Price cannot be less than 1")

        if not offeree_id.isnumeric():
            return error(400, "Offeree id must be numeric")

        offer_types = ["buy", "sell"]
        if offer_type not in offer_types:
            return error(400, "Offer type must be 'buy' or 'sell'")

        # List of all the resources in the game
        resources = variables.RESOURCES

        if resource not in resources:  # Checks if the resource the user selected actually exists
            return error(400, "No such resource")

        if amount < 1:  # Checks if the amount is negative
            return error(400, "Amount must be greater than 0")

        if offer_type == "sell":

            rStatement = f"SELECT {resource} FROM resources " + "WHERE id=%s"
            db.execute(rStatement, (cId,))
            realAmount = int(db.fetchone()[0])

            if amount > realAmount:  # Checks if user wants to sell more than he has
                return error("400", "Selling amount is higher the amount you have.")

            # Calculates the resource amount the seller should have
            newResourceAmount = realAmount - amount

            upStatement = f"UPDATE resources SET {resource}" + "=%s WHERE id=%s"
            db.execute(upStatement, (newResourceAmount, cId))

            # Creates a new offer
            db.execute("INSERT INTO trades (offerer, type, resource, amount, price, offeree) VALUES (%s, %s, %s, %s, %s, %s)",
            (cId, offer_type, resource, amount, price, offeree_id))

            connection.commit()  # Commits the data to the database

        elif offer_type == "buy":

            db.execute("INSERT INTO trades (offerer, type, resource, amount, price, offeree) VALUES (%s, %s, %s, %s, %s, %s)", (cId, offer_type, resource, amount, price, offeree_id))
            
            money_to_take_away = amount * price
            db.execute("SELECT gold FROM stats WHERE id=(%s)", (cId,))
            current_money = db.fetchone()[0]
            if current_money < money_to_take_away:
                return error(400, "You don't have enough money")
            new_money = current_money - money_to_take_away

            db.execute("UPDATE stats SET gold=(%s) WHERE id=(%s)", (new_money, cId))

            flash("You just posted a market offer")

            connection.commit()
    
        connection.close()  # Closes the connection
        return redirect(f"/country/id={offeree_id}")

@app.route("/decline_trade/<trade_id>", methods=["POST"])
@login_required
def decline_trade(trade_id):

    if not trade_id.isnumeric():
            return error(400, "Trade id must be numeric")

    cId = session["user_id"]

    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    db.execute("SELECT offeree, offerer FROM trades WHERE offer_id=(%s)", (trade_id,))
    offeree, offerer = db.fetchone()

    if cId not in [offeree, offerer]:
        return error(400, "You haven't been sent that offer")

    db.execute("DELETE FROM trades WHERE offer_id=(%s)", (trade_id,))

    connection.commit()
    connection.close()

    return redirect("/my_offers")

@app.route("/accept_trade/<trade_id>", methods=["POST"])
@login_required
def accept_trade(trade_id):
        
    cId = session["user_id"]

    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    db.execute("SELECT offeree, type, offerer, resource, amount, price FROM trades WHERE offer_id=(%s)", (trade_id,))
    offeree, trade_type, offerer, resource, amount, price = db.fetchone()

    if offeree != cId:
        return error(400, "You can't accept that offer")

    if trade_type == "sell":
        give_resource(offeree, offerer, "money", amount*price)
        give_resource(offerer, offeree, resource, amount)
    elif trade_type == "buy":
        give_resource(offerer, offeree, "money", amount*price)
        give_resource(offeree, offerer, resource, amount)

    db.execute("DELETE FROM trades WHERE offer_id=(%s)", (trade_id,))
    
    connection.commit()
    connection.close()
    return redirect("/my_offers")

@app.route("/transfer/<transferee>", methods=["POST"])
@login_required
def transfer(transferee):
        
    cId = session["user_id"]

    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    resource = request.form.get("resource")
    amount = int(request.form.get("amount"))

    ### DEFINITIONS ###

    # user - the user transferring the resource, whose id is 'cId'
    # transferee - the user upon whom the resource is transferred

    ###################

    # List of all the resources in the game
    resources = variables.RESOURCES

    if resource not in resources and resource not in ["gold", "money"]:  # Checks if the resource the user selected actually exists
        return error(400, "No such resource")

    if amount < 1:
        return error(400, "Amount cannot be less than 1")
    
    if resource in ["gold", "money"]:

        db.execute("SELECT gold FROM stats WHERE id=(%s)", (cId,))
        user_money = int(db.fetchone()[0])

        if amount > user_money:
            return error(400, "You don't have enough money")

        # Calculates the amount of money the user should have
        new_user_money_amount = user_money - amount

        # Removes the money from the user
        db.execute("UPDATE stats SET gold=(%s) WHERE id=(%s)", (new_user_money_amount, cId))

        # Sees how much money the transferee has
        db.execute("SELECT gold FROM stats WHERE id=(%s)", (transferee,))
        transferee_money = int(db.fetchone()[0])

        # Calculates the amount of money the transferee should have
        new_transferee_resource_amount = amount + transferee_money

        # Gives the money to the transferee
        db.execute("UPDATE stats SET gold=(%s) WHERE id=(%s)", (new_transferee_resource_amount, transferee))

    else:

        user_resource_statement = f"SELECT {resource} FROM resources " + "WHERE id=%s"
        db.execute(user_resource_statement, (cId,))
        user_resource = int(db.fetchone()[0])

        if amount > user_resource:
            return error(400, "You don't have enough resources")

        # Calculates the amount of resource the user should have
        new_user_resource_amount = user_resource - amount

        # Removes the resource from the user
        user_resource_update_statement = f"UPDATE resources SET {resource}" + "=%s WHERE id=%s"
        db.execute(user_resource_update_statement, (new_user_resource_amount, cId))

        # Sees how much of the resource the transferee has
        transferee_resource_statement = f"SELECT {resource} FROM resources " + "WHERE id=%s"
        db.execute(transferee_resource_statement, (transferee,))
        transferee_resource = int(db.fetchone()[0])

        # Calculates the amount of resource the transferee should have
        new_transferee_resource_amount = amount + transferee_resource

        # Gives the resource to the transferee
        transferee_update_statement = f"UPDATE resources SET {resource}" + "=%s WHERE id=%s"
        db.execute(transferee_update_statement, (new_transferee_resource_amount, transferee))

    connection.commit()
    connection.close()
    
    return redirect(f"/country/id={transferee}")