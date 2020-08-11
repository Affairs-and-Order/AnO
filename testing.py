import sqlite3

def generate_revenue():

    infra = {
    'oil_burners_plus': {'uranium': 12},
    'oil_burners_minus': {'oil': 4},

    'hydro_dams_plus': {'uranium': 8},
    'hydro_dams_minus': {'oil': 2},

    'nuclear_reactors_plus': {'uranium': 24},
    'nuclear_reactors_minus': {'iron': 8},

    'solar_fields_plus': {'iron': 4},
    'solar_fields_minus': {'oil': 0}
    }

    conn = sqlite3.connect('affo/aao.db') # connects to db
    db = conn.cursor()

    columns = ['oil_burners', 'hydro_dams', 'nuclear_reactors', 'solar_fields']

    infra_ids = db.execute("SELECT id FROM proInfra").fetchall()

    for unit in columns:
        plus_data = next(iter(infra[f'{unit}_plus'].items()))

        plus_resource = plus_data[0]
        plus_amount = plus_data[1]

        minus_data = next(iter(infra[f'{unit}_minus'].items()))

        minus_resource = minus_data[0]
        minus_amount = minus_data[1]

        """
        print(f"Unit: {unit}")
        print(f"Add {plus_amount} to {plus_resource}")
        print(f"Remove {minus_amount} of {minus_resource}")
        print(f"\n")
        """
    
        for province_id in infra_ids:

            province_id = province_id[0]

            user_id = db.execute("SELECT userId FROM provinces WHERE id=(?)", (province_id,)).fetchone()[0]

            ### REMOVING
            current_minus_resource = db.execute(f"SELECT {minus_resource} FROM resources WHERE id=(?)", (user_id,)).fetchone()[0]
            if current_minus_resource < minus_amount:
                continue
            else:
                new_minus_resource_amount = current_minus_resource - minus_amount
                db.execute(f"UPDATE resources SET {minus_resource}=(?) WHERE id=(?)", (new_minus_resource_amount, user_id))

                ### ADDING
                current_plus_resource = db.execute(f"SELECT {plus_resource} FROM resources WHERE id=(?)", (user_id,)).fetchone()[0]
                new_resource_number = current_plus_resource + plus_amount # 12 is how many uranium it generates
                db.execute(f"UPDATE resources SET {plus_resource}=(?) WHERE id=(?)", (new_resource_number, user_id))

    conn.commit()
    conn.close()

generate_revenue()