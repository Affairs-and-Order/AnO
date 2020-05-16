import sqlite3

def populationGrowth():
    
    conn = sqlite3.connect('affo/aao.db')
    db = conn.cursor()

    pop = db.execute("SELECT population, id FROM stats").fetchall()

    for row in pop:
        user_id = row[1]
        curPop = row[0]
        newPop = curPop + (int(curPop/10))
        ple = db.execute("UPDATE stats SET population=(?) WHERE id=(?)", (newPop, user_id,))
        conn.commit()

    pop = db.execute("SELECT population FROM stats").fetchall()[0]
    print(pop)

populationGrowth()

