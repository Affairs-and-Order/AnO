import os
from dotenv import load_dotenv
load_dotenv()
import psycopg2
from collections import defaultdict
from variables import INFRA, INFRA_TYPE_BUILDINGS

def get_econ_statistics(cId):

    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = conn.cursor()

    db.execute("SELECT id FROM provinces WHERE userId=%s", (cId,))
    provinces_list = db.fetchall()
    provinces = []

    for pId in provinces_list:
        provinces.append(pId[0])

    provinces = tuple(provinces)

    total = {}
    total = defaultdict(lambda:0, total)

    # This is a pretty bad way of doing this, but the best
    # I thought of in the time given
    # TODO: find way to do this that would take less LOC
    db.execute(
    """
    SELECT
    coal_burners, oil_burners, hydro_dams, nuclear_reactors, solar_fields,
    gas_stations, general_stores, farmers_markets, malls, banks,
    city_parks, hospitals, libraries, universities, monorails,
    army_bases, harbours, aerodomes, admin_buildings, silos,
    farms, pumpjacks, coal_mines, bauxite_mines,
    copper_mines, uranium_mines, lead_mines, iron_mines,
    lumber_mills, component_factories, steel_mills, ammunition_factories,
    aluminium_refineries, oil_refineries
    FROM proInfra WHERE id IN %s
    """, (provinces,))
    province_units = db.fetchall()

    for units in province_units:

        units = list(units)

        coal_burners, oil_burners, hydro_dams, nuclear_reactors, solar_fields, \
        gas_stations, general_stores, farmers_markets, malls, banks, \
        city_parks, hospitals, libraries, universities, monorails, \
        army_bases, harbours, aerodomes, admin_buildings, silos, \
        farms, pumpjacks, coal_mines, bauxite_mines, \
        copper_mines, uranium_mines, lead_mines, iron_mines, \
        lumber_mills, component_factories, steel_mills, ammunition_factories, \
        aluminium_refineries, oil_refineries = units

        total["coal_burners"] += coal_burners
        total["oil_burners"] += oil_burners
        total["hydro_dams"] += hydro_dams
        total["nuclear_reactors"] += nuclear_reactors
        total["solar_fields"] += solar_fields

        total["gas_stations"] += gas_stations
        total["general_stores"] += general_stores
        total["farmers_markets"] += farmers_markets
        total["malls"] += malls
        total["banks"] += banks

        total["city_parks"] += city_parks
        total["hospitals"] += hospitals
        total["libraries"] += libraries
        total["universities"] += universities
        total["monorails"] += monorails

        total["army_bases"] += army_bases
        total["harbours"] += harbours
        total["aerodomes"] += aerodomes
        total["admin_buildings"] += admin_buildings
        total["silos"] += silos

        total["farms"] += farms
        total["pumpjacks"] + pumpjacks
        total["coal_mines"] += coal_mines
        total["bauxite_mines"] += bauxite_mines
        
        total["copper_mines"] += copper_mines
        total["uranium_mines"] += uranium_mines
        total["lead_mines"] += lead_mines
        total["iron_mines"] += iron_mines

        total["lumber_mills"] += lumber_mills
        total["component_factories"] += component_factories
        total["steel_mills"] += steel_mills
        total["ammunition_factories"] += ammunition_factories

        total["aluminium_refineries"] += aluminium_refineries
        total["oil_refineries"] += oil_refineries

    expenses = {}
    expenses = defaultdict(lambda: defaultdict(lambda: 0), expenses)
    
    def get_unit_type(unit):
        for type_name, buildings in INFRA_TYPE_BUILDINGS.items():
            if unit in buildings: return type_name

    def check_for_resource_upkeep(unit, amount):
        try:
            convert_minus = list(INFRA[f'{unit}_convert_minus'][0].items())[0]
            minus = convert_minus[0]
            minus_amount = convert_minus[1] * amount
        except KeyError:
            minus, minus_amount = [None, None]
            convert_minus = []
            return False

        if minus != None:
            unit_type = get_unit_type(unit)
            expenses[unit_type][minus] += minus_amount
        return True

    def check_for_monetary_upkeep(unit, amount):
        operating_costs = int(INFRA[f'{unit}_money']) * amount
        unit_type = get_unit_type(unit)
        expenses[unit_type]["money"] += operating_costs

    for unit, amount in total.items():
        if amount != 0:
            check_for_resource_upkeep(unit, amount)
            check_for_monetary_upkeep(unit, amount)

    """
    for k, v in expenses.items():
        for f, g in v.items():
            print(k, f, g)
    """

    return expenses

def format_econ_statistics(statistics):

    formatted = {}
    formatted = defaultdict(lambda:"", formatted)

    for unit_type, unit_type_data in statistics.items():
        unit_type_data = list(unit_type_data.items())
        idx = 0
        for resource, amount in unit_type_data:

            if idx != len(unit_type_data)-1:
                expense_string = f"{amount} {resource}, "
            else:
                expense_string = f"{amount} {resource}"

            formatted[unit_type] += expense_string
            idx += 1

    return formatted

statistics = get_econ_statistics(1)
formatted_statistics = format_econ_statistics(statistics)
print(formatted_statistics)