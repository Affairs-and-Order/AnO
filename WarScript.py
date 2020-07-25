import random
import sqlite3
import _pickle as pickle
import json
import random

path = "affo/aao.db"



# every 2 hours (12pm, 2pm, 4pm, etc), run WarScriptAttackButton. check if any countries at war have not fought in 2 hours.
# if they have not fought in 2 hours, update the time they last fought
# run warScriptAttackButton
# else:

# might need flask to call this, not sure?
def every2hours():
    warsHappenNow()

# might need flask to call this, not sure?
def WarsHappenNow():
    # each table entry was put there either immediately because of a click, or because 
    # Find all entries where the ACTIVE value is TRUE, meaning currently at war.
    warring_nations = db.execute("SELECT * FROM wartable WHERE ACTIVE=TRUE")
    provinces1 = read from database(countryIDattacker): provinces
    provinces2 = read from database(countryIDattacker): provinces
    # if they have the same number of provinces
    if provinces1 == provinces2:
        # then we allow the war to happen
        read from database(countryIDattacker): units, morale, tech_score, effectiveness.
        x = lambda n, m, v, t, e : (n+v) * ((t*e)/10 + m)
        country1result = x(units, morale, tech_score, effectiveness, Math.random(1))

        sql.execute(new_units, new_morale, new_techscore, new_effectiveness)

    else:
        print('this country does not have the same number of provinces as you!')
    # if they click attack again, don't let them spam it
    if warring == warring:
        print('you are already fighting this country!')

    db.execute upload TABLE: WAR_TABLE

@WarScriptAttackButtonPressed
function WarScriptAttackButtonPressed(attackerID, defenderID):
        db.execute("NEW ENTRY TO WARTABLE ")


@HELPALLY


nation1score = multiplies all these inputs together. 
nation2score = multiplies all the 2nd inputs together.
if nation1score > nation2score:
    
