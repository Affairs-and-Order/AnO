import sqlite3

conn = sqlite3.connect('affo/aao.db') # connects to db
db = conn.cursor()

cId = 1

my_offers = db.execute("SELECT resource, price, amount, type, offer_id FROM offers WHERE user_id=(?) ORDER BY offer_id ASC", (cId,)).fetchall()

print(my_offers)

