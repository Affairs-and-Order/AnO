import sqlite3

connection = sqlite3.connect('affo/aao.db')
db = connection.cursor()

sell_str = "sell"
statement = f"SELECT offer_id FROM offers WHERE type='sell'"

offer_type = 'buy'
d = db.execute("SELECT offer_id FROM offers WHERE type=(?)", (offer_type,)).fetchall()

print(d)