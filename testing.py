import sqlite3

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

"""
oil_burners_plus = tuple(infra['oil_burners_plus'])

oil_plus_resource = oil_burners_plus[0]
oil_plus_amount = oil_burners_plus[1]


oil_burners_minus = tuple(infra['oil_burners_minus'])
"""

def generate_revenue():

    conn = sqlite3.connect('affo/aao.db') # connects to db
    db = conn.cursor()

    columns = ['oil_burners', 'hydro_dams', 'nuclear_reactors', 'solar_fields']
    for unit in columns:
        plus_data = next(iter(infra[f'{unit}_plus'].items()))

        plus_resource = plus_data[0]
        plus_amount = plus_data[1]

        minus_data = next(iter(infra[f'{unit}_minus'].items()))

        minus_resource = minus_data[0]
        minus_amount = minus_data[1]

        print(f"Unit: {unit}")
        print(f"Add {plus_amount} to {plus_resource}")
        print(f"Remove {minus_amount} of {minus_resource}")
        print("\n")

    infra_ids = db.execute("SELECT id FROM proInfra").fetchall()

    """
    for province_id in infra_ids:

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
    """

generate_revenue()