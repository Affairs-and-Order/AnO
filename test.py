
def insist_upgrades(func, type):

    def insist(*args, **kwargs):
        if type == "supplies":
            pass
        elif type == "upkeep": pass

    return insist_upgrades

def update_supply(war_id):
    connection = sqlite3.connect("affo/aao.db")
    db = connection.cursor()

    attacker_supplies, defender_supplies, supply_date = db.execute("SELECT attacker_supplies,defender_supplies,last_visited FROM wars WHERE id=?", (war_id,)).fetchall()[0]
    current_time = time.time()

    if current_time < int(supply_date):
        return "TIME STAMP IS CORRUPTED"

    time_difference = current_time - supply_date
    hours_count = time_difference//3600
    supply_by_hours = hours_count*50 # 50 supply in every hour

    # TODO: give bonus supplies if there is specific infrastructure for it
    # if supply_bonus: xy

    if supply_by_hours > 0:
        db.execute("UPDATE wars SET attacker_supplies=(?), defender_supplies=(?), last_visited=(?) WHERE id=(?)", (supply_by_hours+attacker_supplies, supply_by_hours+defender_supplies, time.time(), war_id))
        connection.commit()


def infra():
    run = 1

    # Oil burners now cost $40,000 per hour in upkeep instead of $60,000
    if run:
        cost = 60000
