from app import app
from helpers import login_required, error
import psycopg2
from flask import request, render_template, session, redirect, flash
import os
import variables

def give_resource(giver_id, taker_id, resource, amount):

    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))
    db = conn.cursor()

    giver_id = int(giver_id)
    taker_id = int(taker_id)

    amount = int(amount)

    resources_list = variables.RESOURCES

    # Returns error if resource doesn't exist
    if resource not in resources_list and resource != "money":
        return "No such resource"
    
    if resource in ["gold", "money"]:

        print("money")
        
        db.execute("SELECT gold FROM stats WHERE id=%s", (giver_id,))
        current_giver_money = db.fetchone()[0]

        if current_giver_money < amount:
            return "Giver doesn't have enough resources to transfer such amount."

        db.execute("UPDATE stats SET gold=gold-%s WHERE id=%s", (amount, giver_id))
        db.execute("UPDATE stats SET gold=gold+%s WHERE id=%s", (amount, taker_id))

    else:
        
        current_resource_statement = f"SELECT {resource} FROM resources WHERE " + "id=%s"
        db.execute(current_resource_statement, (giver_id,))
        current_giver_resource = db.fetchone()[0]

        if current_giver_resource < amount:
            return "Giver doesn't have enough resources to transfer such amount."

        giver_update_statement = f"UPDATE resources SET {resource}={resource}-{amount}" + " WHERE id=%s"
        db.execute(giver_update_statement, (giver_id,))

        taker_update_statement = f"UPDATE resources SET {resource}={resource}+{amount}" + " WHERE id=%s"
        db.execute(taker_update_statement, (taker_id,))

    conn.commit()
    conn.close()

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

            db.execute("SELECT resource FROM offers WHERE offer_id=(%s)", (i[0],))
            resource = db.fetchone()[0]

            if filter_resource is not None:
                if filter_resource == resource:
                    pass
                else:
                    continue

            offer_ids.append(i[0])

            db.execute("SELECT user_id FROM offers WHERE offer_id=(%s)", (i[0],))
            user_id = db.fetchone()[0]
            ids.append(user_id)

            db.execute("SELECT type FROM offers WHERE offer_id=(%s)", (i[0],))
            offer_type = db.fetchone()[0]
            types.append(offer_type)

            db.execute("SELECT username FROM users WHERE id=(%s)", (user_id,))
            name = db.fetchone()[0]
            names.append(name)

            db.execute("SELECT resource FROM offers WHERE offer_id=(%s)", (i[0],))
            resource = db.fetchone()[0]
            resources.append(resource)

            db.execute("SELECT amount FROM offers WHERE offer_id=(%s)", (i[0],))
            amount = db.fetchone()[0]
            amounts.append(amount)

            db.execute("SELECT price FROM offers WHERE offer_id=(%s)", (i[0],))
            price = db.fetchone()[0]
            prices.append(price)

            total_price = price * amount
            total_prices.append(total_price)

        connection.close() # Closes the connection

        offers = zip(ids, types, names, resources, amounts, prices, offer_ids, total_prices)
        # Zips everything into 1 list

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

    amount_wanted = int(request.form.get(f"amount_{offer_id}"))

    db.execute("SELECT resource, amount, price, user_id FROM offers WHERE offer_id=(%s)", (offer_id,))
    offer = db.fetchone()

    resource = offer[0] # What resource will be bought

    total_amount = int(offer[1]) # Of resources

    price_for_one = int(offer[2]) # Price for one resource

    seller_id = int(offer[3]) # The user id of the seller

    if amount_wanted < 1:
        return error(400, "Amount cannot be less than 1")

    if amount_wanted > total_amount:
        return error(400, "Amount wanted cant be higher than total amount")

    db.execute("SELECT gold FROM stats WHERE id=(%s)", (cId,))
    buyers_gold = int(db.fetchone()[0])

    if (amount_wanted * price_for_one) > buyers_gold: # Checks if buyer doesnt have enough gold for buyin
        return error(400, "you don't have enough money") # Returns error if true
    gold_sold = buyers_gold - (amount_wanted * price_for_one)

    db.execute("UPDATE stats SET gold=(%s) WHERE id=(%s)", (gold_sold, cId))

    # Gets current amount of resource for the buyer
    currentBuyerResource = f"SELECT {resource} FROM resources " + " WHERE id=%s"
    db.execute(currentBuyerResource, (cId,))
    buyerResource = db.fetchone()[0]  # executes the statement

    # Generates the number of the resource the buyer should have
    newBuyerResource = int(buyerResource) + int(amount_wanted)

    # Gives the buyer the amount of resource he bought
    buyUpdStat = f"UPDATE resources SET {resource}" + "=%s WHERE id=%s"
    db.execute(buyUpdStat, (newBuyerResource, cId))  # executes the statement

    # Gives money to the seller
    db.execute("SELECT gold FROM stats WHERE id=(%s)", (seller_id,))
    sellers_money = db.fetchone()[0]

    new_sellers_money = sellers_money + (amount_wanted * price_for_one)
    db.execute("UPDATE stats SET gold=(%s) WHERE id=(%s)", (new_sellers_money, seller_id))

    new_offer_amount = (total_amount - amount_wanted)

    if new_offer_amount == 0:
        db.execute("DELETE FROM offers WHERE offer_id=(%s)", (offer_id,))
    else:
        db.execute("UPDATE offers SET amount=(%s) WHERE offer_id=(%s)", (new_offer_amount, offer_id))

    # updates the offer with the new amount

    connection.commit() # Commits the connection
    connection.close() # Closes the connection

    return redirect("/market")

@app.route("/sell_offer/<offer_id>", methods=["POST"])
@login_required
def sell_market_offer(offer_id):
  
    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    seller_id = session["user_id"]

    amount_wanted = int(request.form.get(f"amount_{offer_id}"))

    if not offer_id.isnumeric():
        return error(400, "Values must be numeric")

    db.execute("SELECT resource, amount, price, user_id FROM offers WHERE offer_id=(%s)", (offer_id,))
    offer = db.fetchone()

    resource = offer[0] # What resource it is

    total_amount = int(offer[1]) # Of resources

    price_for_one = int(offer[2]) # Price for one resource (in money)

    buyer_id = int(offer[3]) # The buyer's id

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

    # Removes the resource from the seller
    new_sellers_resource = sellers_resource - amount_wanted
    res_upd_statement = f"UPDATE resources SET {resource}" + "=%s WHERE id=%s"
    db.execute(res_upd_statement, (new_sellers_resource, seller_id))

    # Gives the resource to the buyer
    db.execute(resource_statement, (buyer_id,)) # Selects how many resources of wanted resource the buyer has
    buyers_resource = db.fetchone()[0]
    new_buyers_resource = buyers_resource + amount_wanted # Generates the new amount by adding current amount + bought amount

    db.execute(res_upd_statement, (new_buyers_resource, buyer_id))

    # Takes away the money used for buying from the buyer

    db.execute("SELECT gold FROM stats WHERE id=(%s)", (buyer_id,))
    current_buyers_money = db.fetchone()[0]

    new_buyers_money = current_buyers_money - (price_for_one * amount_wanted)

    db.execute("UPDATE stats SET gold=(%s) WHERE id=(%s)", (new_buyers_money, buyer_id,))

    # Gives the money to the seller

    db.execute("SELECT gold FROM stats WHERE id=(%s)", (seller_id,))
    current_sellers_money = db.fetchone()[0]
    new_sellers_money = current_sellers_money + (price_for_one * amount_wanted)

    db.execute("UPDATE stats SET gold=(%s) WHERE id=(%s)", (new_sellers_money, seller_id,))

    # Generates the new amount, after the buyer has got his resources from the seller

    new_offer_amount = (total_amount - amount_wanted)

    if new_offer_amount == 0: # Checks if the new offer amount is equal to 0
        db.execute("DELETE FROM offers WHERE offer_id=(%s)", (offer_id,)) # If yes, it deletes the offer

    else:
        db.execute("UPDATE offers SET amount=(%s) WHERE id=(%s)", (new_offer_amount, offer_id)) # Updates the database with the new amount

    connection.commit()
    connection.close()

    return redirect("/market")

@app.route("/marketoffer/", methods=["GET"])
@login_required
def marketoffer():
    return render_template("marketoffer.html")

@app.route("/post_offer/<offer_type>", methods=["POST"])
@login_required
def post_offer(offer_type):

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
        price = request.form.get("price")

        """
        if amount.isnumeric() is False or price.isnumeric() is False:
            return error(400, "You can only type numeric values into /marketoffer ")
        """

        # List of all the resources in the game
        resources = variables.RESOURCES

        offer_types = ["buy", "sell"]
        if offer_type not in offer_types:
            return error(400, "Offer type must be 'buy' or 'sell'")

        if resource not in resources:  # Checks if the resource the user selected actually exists
            return error(400, "No such resource")

        if amount < 1:  # Checks if the amount is negative
            return error(400, "Amount must be greater than 0")

        if offer_type == "sell":

            # possible sql injection posibility TODO: look into this
            # should be fine there's no user input in resource -- steven
            rStatement = f"SELECT {resource} FROM resources " + "WHERE id=%s"
            db.execute(rStatement, (cId,))
            realAmount = int(db.fetchone()[0])

            if amount > realAmount:  # Checks if user wants to sell more than he has
                return error("400", "Selling amount is higher than the amount you have.")

            # Calculates the resource amount the seller should have
            newResourceAmount = realAmount - amount

            upStatement = f"UPDATE resources SET {resource}" + "=%s WHERE id=%s"
            db.execute(upStatement, (newResourceAmount, cId))

            # Creates a new offer
            db.execute("INSERT INTO offers (user_id, type, resource, amount, price) VALUES (%s, %s, %s, %s, %s)", 
            (cId, offer_type, resource, int(amount), int(price), ))

            connection.commit()  # Commits the data to the database

        elif offer_type == "buy":

            db.execute("INSERT INTO offers (user_id, type, resource, amount, price) VALUES (%s, %s, %s, %s, %s)",
            (cId, offer_type, resource, int(amount), int(price), ))

            money_to_take_away = int(amount) * int(price)
            db.execute("SELECT gold FROM stats WHERE id=(%s)", (cId,))
            current_money = db.fetchone()[0]

            if current_money < money_to_take_away:
                return error(400, "You don't have enough money")
            new_money = current_money - money_to_take_away

            db.execute("UPDATE stats SET gold=(%s) WHERE id=(%s)", (new_money, cId))

            flash("You just posted a market offer")

            connection.commit()
    
        connection.close()  # Closes the connection
        return redirect("/market")


@app.route("/my_offers", methods=["GET"])
@login_required
def my_offers():

    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = connection.cursor()

    cId = session["user_id"]

    ## USER'S OUTGOING OFFERS
    db.execute("SELECT offer_id FROM offers WHERE user_id=(%s) ORDER BY offer_id ASC", (cId,))
    offer_ids_list = db.fetchall()

    outgoing_offer_amount = len(offer_ids_list)

    offer_ids = []
    total_prices = []
    prices = []
    resources = []
    amounts = []
    offer_types = []

    for offer_idd in offer_ids_list:

        offer_id = offer_idd[0]
        db.execute("SELECT price FROM offers WHERE offer_id=(%s)", (offer_id,))
        price = db.fetchone()[0]
        db.execute("SELECT resource FROM offers WHERE offer_id=(%s)", (offer_id,))
        resource = db.fetchone()[0]
        db.execute("SELECT amount FROM offers WHERE offer_id=(%s)", (offer_id,))
        amount = db.fetchone()[0]
        db.execute("SELECT type FROM offers WHERE offer_id=(%s)", (offer_id,))
        offer_type = db.fetchone()[0]
        total_price = int(price * amount)

        prices.append(price)
        resources.append(resource)
        amounts.append(amount)
        offer_types.append(offer_type)
        total_prices.append(total_price)
        offer_ids.append(offer_id)

    my_offers = zip(offer_ids, prices, resources, amounts, offer_types, total_prices)

    ## USER'S INCOMING TRADES

    db.execute("SELECT offer_id FROM trades WHERE offeree=(%s) ORDER BY offer_id ASC", (cId,))
    trade_ids_list = db.fetchall()

    incoming_amount = len(trade_ids_list)

    trade_ids = []
    total_pricess = []
    pricess = []
    resourcess = []
    amountss = []
    offer_typess = []
    offerer_ids = []
    offerer_names = []

    for offer_idd in trade_ids_list:

        offer_id = offer_idd[0]

        db.execute("SELECT price FROM trades WHERE offer_id=(%s)", (offer_id,))
        price = db.fetchone()[0]
        db.execute("SELECT resource FROM trades WHERE offer_id=(%s)", (offer_id,))
        resource = db.fetchone()[0]
        db.execute("SELECT amount FROM trades WHERE offer_id=(%s)", (offer_id,))
        amount = db.fetchone()[0]
        db.execute("SELECT type FROM trades WHERE offer_id=(%s)", (offer_id,))
        offer_type = db.fetchone()[0]
        total_price = int(price * amount)
        db.execute("SELECT offerer FROM trades WHERE offer_id=(%s)", (offer_id,))
        offerer = db.fetchone()[0]
        db.execute("SELECT username FROM users WHERE id=(%s)", (offerer,))
        offerer_name = db.fetchone()[0]

        pricess.append(price)
        resourcess.append(resource)
        amountss.append(amount)
        offer_typess.append(offer_type)
        total_pricess.append(total_price)
        trade_ids.append(offer_id)
        offerer_ids.append(offerer)
        offerer_names.append(offerer_name)

    incoming_trades = zip(trade_ids, pricess, resourcess, amountss, offer_typess, total_pricess, offerer_ids, offerer_names)

    connection.close()

    return render_template("my_offers.html", cId=cId, my_offers=my_offers, outgoing_offer_amount=outgoing_offer_amount,
    incoming_trades=incoming_trades, incoming_amount=incoming_amount)

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

        db.execute("SELECT amount FROM offers WHERE offer_id=(%s)", (offer_id,))
        amount = int(db.fetchone()[0])
        db.execute("SELECT price FROM offers WHERE offer_id=(%s)", (offer_id,))
        price = int(db.fetchone()[0])

        # Gives back the user his money
        db.execute("SELECT gold FROM stats WHERE id=(%s)", (cId,))
        current_money = int(db.fetchone()[0])
        new_money = current_money + (price * amount)

        db.execute("UPDATE stats SET gold=(%s) WHERE id=(%s)", (new_money, cId))

    elif offer_type == "sell":

        db.execute("SELECT amount FROM offers WHERE offer_id=(%s)", (offer_id,))
        amount = int(db.fetchone()[0])
        db.execute("SELECT resource FROM offers WHERE offer_id=(%s)", (offer_id,))
        resource = db.fetchone()[0]

        current_resource_statement = f"SELECT {resource} " + "FROM resources WHERE id=%s"
        db.execute(current_resource_statement, (cId,))
        current_resource = int(db.fetchone()[0])

        new_resource = current_resource + amount

        update_statement = f"UPDATE resources SET {resource}" + "=%s WHERE id=%s"
        db.execute(update_statement, (new_resource, cId))

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

            # possible sql injection posibility TODO: look into this
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

    db.execute("SELECT offeree FROM trades WHERE offer_id=(%s)", (trade_id,))
    trade_offeree = db.fetchone()[0]

    if cId != trade_offeree:
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

    db.execute("SELECT offeree FROM trades WHERE offer_id=(%s)", (trade_id,))
    trade_offeree = db.fetchone()[0]

    if trade_offeree != cId:
        return error(400, "You can't accept that offer")

    db.execute("SELECT type FROM trades WHERE offer_id=(%s)", (trade_id,))
    trade_type = db.fetchone()[0]
    db.execute("SELECT offerer FROM trades WHERE offer_id=(%s)", (trade_id,))
    offerer = db.fetchone()[0]
    db.execute("SELECT resource FROM trades WHERE offer_id=(%s)", (trade_id,))
    resource = db.fetchone()[0]
    db.execute("SELECT amount FROM trades WHERE offer_id=(%s)", (trade_id,))
    amount = db.fetchone()[0]
    db.execute("SELECT price FROM trades WHERE offer_id=(%s)", (trade_id,))
    price = db.fetchone()[0]

    trade_types = ["buy", "sell"]
    if trade_type not in trade_types:
        return error(400, "Trade type must be 'buy' or 'sell'")

    # List of all the resources in the game
    resources = variables.RESOURCES

    if resource not in resources:  # Checks if the resource the user selected actually exists
        return error(400, "No such resource")

    if amount < 1:  # Checks if the amount is negative
        return error(400, "Amount must be greater than 0")

    if trade_type == "sell":
        
        seller_id = offerer

        db.execute("SELECT gold FROM stats WHERE id=(%s)", (cId,))
        buyers_gold = int(db.fetchone()[0])

        if (amount * price) > buyers_gold: # Checks if buyer doesnt have enough gold for buyin
            return error(400, "you don't have enough money") # Returns error if true
        gold_sold = buyers_gold - (amount * price)

        db.execute("UPDATE stats SET gold=(%s) WHERE id=(%s)", (gold_sold, cId))

        # Gets current amount of resource for the buyer
        currentBuyerResource = f"SELECT {resource} FROM resources " + "WHERE id=%s"
        db.execute(currentBuyerResource, (cId,)) # executes the statement
        buyerResource = db.fetchone()[0]

        # Generates the number of the resource the buyer should have
        newBuyerResource = int(buyerResource) + int(amount)

        # Gives the buyer the amount of resource he bought
        buyUpdStat = f"UPDATE resources SET {resource}" + "=%s WHERE id=%s"
        db.execute(buyUpdStat, (newBuyerResource, cId))  # executes the statement

        # Gives money to the seller
        db.execute("SELECT gold FROM stats WHERE id=(%s)", (seller_id,))
        sellers_money = db.fetchone()[0]

        new_sellers_money = sellers_money + (amount * price)
        db.execute("UPDATE stats SET gold=(%s) WHERE id=(%s)", (new_sellers_money, seller_id))

    elif trade_type == "buy":

        seller_id = cId
        buyer_id = offerer

        # Sees how much of the resource the seller has
        resource_statement = f"SELECT {resource} FROM resources " + "WHERE id=%s"
        db.execute(resource_statement, (seller_id,))
        sellers_resource = int(db.fetchone()[0])

        # Checks if it's less than what the seller wants to sell
        if sellers_resource < amount:
            return error(400, "You don't have enough of that resource")

        # Removes the resource from the seller
        new_sellers_resource = sellers_resource - amount
        res_upd_statement = f"UPDATE resources SET {resource}" + "=%s WHERE id=%s"
        db.execute(res_upd_statement, (new_sellers_resource, seller_id))

        # Gives the resource to the buyer
        db.execute(resource_statement, (buyer_id,))
        buyers_resource =  db.fetchone()[0]
        new_buyers_resource = buyers_resource + amount # Generates the new amount by adding current amount + bought amount

        db.execute(res_upd_statement, (new_buyers_resource, buyer_id))

        # Takes away the money used for buying from the buyer

        db.execute("SELECT gold FROM stats WHERE id=(%s)", (buyer_id,))
        current_buyers_money = db.fetchone()[0]
        new_buyers_money = current_buyers_money - (price * amount)

        db.execute("UPDATE stats SET gold=(%s) WHERE id=(%s)", (new_buyers_money, buyer_id,))

        # Gives the money to the seller

        db.execute("SELECT gold FROM stats WHERE id=(%s)", (seller_id,))
        current_sellers_money = db.fetchone()[0]
        new_sellers_money = current_sellers_money + (price * amount)

        db.execute("UPDATE stats SET gold=(%s) WHERE id=(%s)", (new_sellers_money, seller_id,))

        db.execute("DELETE FROM trades WHERE offer_id=(%s)", (trade_id,)) # Deletes the offer
    
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