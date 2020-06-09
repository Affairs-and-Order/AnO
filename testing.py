import sqlite3

conn = sqlite3.connect('affo/aao.db')
db = conn.cursor()

key = input("Enter Key:\n")

allKeys = db.execute("SELECT key FROM keys").fetchall()

for keys in allKeys:
    print(keys[0])
    if key == keys[0]:
        print("LOGGED IN")

"""for key in keys:
  if key == keys[0]:
      print("eyy")"""

"""for key in keys:
  if user_input is key[0]:
      print("eyy")"""