import random
import sqlite3
import _pickle as pickle
import json
import random

path = "affo/aao.db"


# runs every 2 hours  (12pm, 2pm, 4pm, etc) check if any countries at war have not fought in 2 hours. if they have not fought in 2 hours, update the time they last fought and fight. Else just nothing happens... till the next 2 hours anyway. The user interface must also not allow clicking "attack" on the same country if they are already at war.
@celery.task()
def WarsHappenNow():
    # each table entry was put there either immediately because of a click, or because of a 2 hour later war result update
    # I expect each entry in the WarTable to have: attackingCountry, defendingCountry, 

    # Find all entries where the ACTIVE value is TRUE, meaning current wars.
    # all the entries where ACTIVE is False are just for history.
    allLatestWarEntries = db.execute("SELECT * FROM wartable WHERE ACTIVE=TRUE")
    
    # go through one war at a time.
    for warEntry in allLatestWarEntries:
        # find if the number of provinces for each country is the same in that war, IF it is the first war they've had (i'm assuming wars can continue even if the number of provinces change).
        attackerProvinces = db.execute("SELECT provinces FROM war WHERE ")
        # defendingProvinces = read from database(countryIDattacker): provinces
        # if they have the same number of provinces then allow the war to happen
        if attackerProvinces == defendingProvinces:
            print('you are already fighting this country!')
            read from database(countryIDattacker): units, morale, tech_score, effectiveness.
            x = lambda n, m, v, t, e : (n+v) * ((t*e)/10 + m)
            country1result = x(units, morale, tech_score, effectiveness, Math.random(1))

            sql.execute(new_units, new_morale, new_techscore, new_effectiveness)

        else:
            print('this country does not have the same number of provinces as you!')


        db.execute upload TABLE: WAR_TABLE

@WarScriptAttackButtonPressed
function WarScriptAttackButtonPressed(attackerID, defenderID):
        db.execute("NEW ENTRY TO WARTABLE ")


@HELPALLY


nation1score = multiplies all these inputs together. 
nation2score = multiplies all the 2nd inputs together.
if nation1score > nation2score:
    
