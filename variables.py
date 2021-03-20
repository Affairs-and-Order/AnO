# File for variables that are repeated multiple times in other files (for example, the resources list)

CG_PER = 250000 # 1 Consumer good per x population
RATIONS_PER = 200000  # 1 Ration per x population

NO_ENERGY_MULTIPLIER = 0.6 # How much the tax income will decrease if there's no energy
NO_FOOD_MULTIPLIER = 0.4 # How much the tax income will decrease if there's no food

RESOURCES = [
    "rations", "oil", "coal", "uranium", "bauxite", "lead", "copper", "iron",
    "lumber", "components", "steel", "consumer_goods", "aluminium",
    "gasoline", "ammunition"
]

ENERGY_UNITS = ["coal_burners", "oil_burners", "hydro_dams", "nuclear_reactors", "solar_fields"]

ENERGY_CONSUMERS = [
    'gas_stations', 'general_stores', 'farmers_markets', 'malls', 'banks',
    'city_parks', 'hospitals', 'libraries', 'universities', 'monorails',

    "component_factories", "steel_mills", "ammunition_factories", "aluminium_refineries",
    "oil_refineries"
]

TRADE_TYPES = ["buy", "sell"]

BUILDINGS = [
    'coal_burners', 'oil_burners', 'hydro_dams', 'nuclear_reactors', 'solar_fields',
    'gas_stations', 'general_stores', 'farmers_markets', 'malls',
    'banks', 'hospitals', 'libraries', 'universities',

    "farms", "pumpjacks", "coal_mines", "bauxite_mines", "copper_mines", "uranium_mines",
    "lead_mines", "iron_mines", 'lumber_mills',

    "component_factories", "steel_mills", "ammunition_factories", "aluminium_refineries",
    "oil_refineries",

    'city_parks','monorails', # Had to put them here so pollution would be minused at the end
]

# Dictionary for which units give what resources, etc
INFRA = {
    ### Electricity (done) ###
    'coal_burners_plus': {'energy': 3}, # Energy increase
    'coal_burners_convert_minus': [{'coal': 48}], # Resource upkeep cost
    'coal_burners_money': 12000, # Monetary upkeep cost
    'coal_burners_effect': [{'pollution': 9}], # Pollution amount added
    'oil_burners_plus': {'energy': 4},
    'oil_burners_convert_minus': [{'oil': 56}],
    'oil_burners_money': 18000,
    'oil_burners_effect': [{'pollution': 3}],

    'hydro_dams_plus': {'energy': 8},
    'hydro_dams_money': 35000,

    'nuclear_reactors_plus': {'energy': 14}, 
    'nuclear_reactors_convert_minus': [{'uranium': 32}],
    'nuclear_reactors_money': 380000, 

    'solar_fields_plus': {'energy': 4},
    'solar_fields_money': 5000, 
    ####################

    ### Retail ### (Done)
    'gas_stations_plus': {'consumer_goods': 8},
    'gas_stations_effect': [{'pollution': 4}],
    'gas_stations_money': 20000, # Costs $20k

    'general_stores_plus': {'consumer_goods': 12},
    'general_stores_effect': [{'pollution': 2}],
    'general_stores_money': 35000, # Costs $35k

    'farmers_markets_plus': {'consumer_goods': 17}, # Generates 15 consumer goods,
    'farmers_markets_effect': [{'pollution': 5}],
    'farmers_markets_money': 80000, # Costs $110k

    'banks_plus': {'consumer_goods': 25},
    'banks_money': 220000, # Costs $320k

    'malls_plus': {'consumer_goods': 34},
    'malls_effect': [{'pollution': 10}],
    'malls_money': 450000, # Costs $750k
    ##############

    ### Public Works ### (Done)
    'libraries_effect': [{'happiness': 3}, {'productivity': 3}],
    'libraries_money': 60000,

    'city_parks_effect': [{'happiness': 3}],
    'city_parks_effect_minus': {'pollution': 6},
    'city_parks_money': 25000, # Costs $20k

    'hospitals_effect': {'happiness': 9},   
    'hospitals_money': 90000,

    'universities_effect': [{'productivity': 6}, {'happiness': 6}],
    'universities_money': 175000,

    'monorails_effect': [{'productivity': 12}],
    'monorails_effect_minus': {'pollution': 20}, # Removes 10 pollution
    'monorails_money': 510000,
    ###################

    ### Military (Done) ###
    'army_bases_money': 25000, # Costs $25k
    'harbours_money': 35000,
    'aerodomes_money': 55000,
    'admin_buildings_money': 90000,
    'silos_money': 340000,
    ################

    ### Industry (Done) ###

    'farms_money': 3000, # Costs $3k
    'farms_plus': {'rations': 2},
    'farms_effect': [{'pollution': 1}],

    'pumpjacks_money': 10000, # Costs $10k
    'pumpjacks_plus': {'oil': 23},
    'pumpjacks_effect': [{'pollution': 2}],

    'coal_mines_money': 10000, # Costs $10k
    'coal_mines_plus': {'coal': 26},
    'coal_mines_effect': [{'pollution': 2}],

    'bauxite_mines_money': 8000, # Costs $8k
    'bauxite_mines_plus': {'bauxite': 20},

    'copper_mines_money': 8000, # Costs $8k
    'copper_mines_plus': {'copper': 32},

    'uranium_mines_money': 18000, # Costs $18k
    'uranium_mines_plus': {'uranium': 12},

    'lead_mines_money': 12000,
    'lead_mines_plus': {'lead': 18},

    'iron_mines_money': 12000,
    'iron_mines_plus': {'iron': 25},

    'lumber_mills_money': 7500,
    'lumber_mills_plus': {'lumber': 32},
    'lumber_mills_effect': [{'pollution': 1}],

    ################

    ### Processing (Done) ###
    'component_factories_money': 220000, # Costs $220k
    'component_factories_convert_minus': [{'copper': 20}, {'steel': 10}, {'aluminium': 15}],
    'component_factories_plus': {'components': 5},

    'steel_mills_money': 180000,
    'steel_mills_convert_minus': [{'coal': 35}, {'iron': 35}],
    'steel_mills_plus': {'steel': 15},

    'ammunition_factories_money': 140000,
    'ammunition_factories_convert_minus': [{'copper': 10}, {'lead': 20}],
    'ammunition_factories_plus': {'ammunition': 10},

    'aluminium_refineries_money': 150000,
    'aluminium_refineries_convert_minus': [{'bauxite': 15}],
    'aluminium_refineries_plus': {'aluminium': 12},

    'oil_refineries_money': 160000,
    'oil_refineries_convert_minus': [{'oil': 20}],
    'oil_refineries_plus': {'gasoline': 8}
}