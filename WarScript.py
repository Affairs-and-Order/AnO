import random
import sqlite3
import _pickle as pickle
import json
import random
import sqlite3

path = "affo/aao.db"
conn = sqlite3.connect(path)
db = conn.cursor() # syntax sqlite3 to convert to usable python interface

# runs every 2 hours  (12pm, 2pm, 4pm, etc) check if any countries at war have not fought in 2 hours. if they have not fought in 2 hours, update the time they last fought and fight. Else just nothing happens... till the next 2 hours anyway. The user interface must also not allow clicking "attack" on the same country if they are already at war.
# THIS METHOD IS OBSOLETE USE SUPPLIES INSTEAD OF AUTO ATTACK EVERY 2 HOURS
def WarsHappenNow():
    # each table entry was put there either immediately because of a click, or because of a 2 hour later war result update
    # I expect each entry in the WarTable to have: attackingCountry, defendingCountry,

    # Find all entries where the ACTIVE value is TRUE, meaning current wars.
    # all the entries where ACTIVE is False are just for history.
    allLatestWarEntries = db.execute(
        "SELECT * FROM wartable WHERE ACTIVE=TRUE").fetchall()

    # go through one war at a time.
    for warEntry in allLatestWarEntries:

            print('you are already fighting this country!')
            db.execute(
                "read from database(countryIDattacker): units, morale, tech_score, effectiveness").fetchall()
            # x = lambda n, m, v, t, e : (n+v) * ((t*e)/10 + m)
            # use the multiplication for now, later the different unit weights can be factored in. etc: fight ground vs ground, sea vs sea, air vs air, giving bonuses if a certain fight was completely dominated.
            #country1result = units*morale * \
            #    tech_score*effectiveness*Math.random(1)

            #sql.execute(new_units, new_morale,
            #            new_techscore, new_effectiveness)



        #db.execute upload TABLE: WAR_TABLE

def declareWarButtonPressed(attackerID, defenderID):
        db.execute("NEW ENTRY TO WARTABLE ")
        # find if the number of provinces for each country is the same in that war, IF it is the first war they've had (i'm assuming wars can continue even if the number of provinces change).
        attackerProvinces = db.execute("SELECT provinces FROM war WHERE ").fetchall()
        defendingProvinces = db.execute("SELECT provinces FROM war WHERE ").fetchall() #read from database(countryIDattacker): provinces
        # if they have the same number of provinces then allow the war to happen
        if attackerProvinces == defendingProvinces:
            # war continues
            print('war allowed put war entry in war table.')
        else:
            print('this country does not have the same number of provinces as you!')



def helpAlly(helperID, attackerID, troops):
    db.execute("MODIFY TABLE WAR (troops) WHERE id=attackerID")
    db.execute("MODIFY TABLE WAR (troops) WHERE id=helperID")


# nation1score = multiplies all these inputs together. 
# nation2score = multiplies all the 2nd inputs together.
#if nation1score > nation2score:
    # some kind of destruction, this will be on a per round basis just like in pnw.
