import sqlite3

def generate_revenue():

    conn = sqlite3.connect('affo/aao.db') # connects to db
    db = conn.cursor()

    # columns = ['oil_burners', 'hydro_dams', 'nuclear_reactors', 'solar_fields']
    oil_burners = db.execute("SELECT id FROM proInfra").fetchall()
    for province_id in oil_burners:

        province_id = province_id[0]
        
        user_id = db.execute("SELECT userId FROM provinces WHERE id=(?)", (province_id,)).fetchone()[0]

        current_oil = db.execute("SELECT oil FROM resources WHERE id=(?)", (user_id,)).fetchone()[0]
        if current_oil < 4:
            continue
        else:
            new_oil = current_oil - 4
            db.execute("UPDATE resources SET oil=(?) WHERE id=(?)", (new_oil, user_id))
            # right now oil burners make 12 uranium while burning 4 oil
            current_resource_number = db.execute("SELECT uranium FROM resources WHERE id=(?)", (user_id,)).fetchone()[0]
            new_resource_number = current_resource_number + 12 # 12 is how many uranium it generates
            db.execute("UPDATE resources SET uranium=(?) WHERE id=(?)", (new_resource_number, user_id))

    conn.commit()
    conn.close()

generate_revenue()