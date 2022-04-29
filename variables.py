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

INFRA_TYPES = ["electricity", "retail", "public_works", "military", "industry", "processing"]
INFRA_TYPE_BUILDINGS = {
    "electricity": ["coal_burners", "oil_burners", "hydro_dams", "nuclear_reactors", "solar_fields"],
    "retail": ['gas_stations', 'general_stores', 'farmers_markets', 'malls', 'banks'],
    "public_works": ['hospitals', 'libraries', 'universities', 'city_parks','monorails'],
    "military": ["army_bases", "harbours", "aerodomes", "admin_buildings", "silos"],
    "industry": ["farms", "pumpjacks", "coal_mines", "bauxite_mines", "copper_mines", "uranium_mines", "lead_mines", "iron_mines", 'lumber_mills',],
    "processing": [ "component_factories", "steel_mills", "ammunition_factories", "aluminium_refineries", "oil_refineries",]
}

BUILDINGS = [
    'coal_burners', 'oil_burners', 'hydro_dams', 'nuclear_reactors', 'solar_fields',

    'gas_stations', 'general_stores', 'farmers_markets', 'malls', 'banks',
    
    'hospitals', 'libraries', 'universities',

    "farms", "pumpjacks", "coal_mines", "bauxite_mines", "copper_mines", "uranium_mines",
    "lead_mines", "iron_mines", 'lumber_mills',

    "component_factories", "steel_mills", "ammunition_factories", "aluminium_refineries",
    "oil_refineries",

    'city_parks','monorails', # Had to put them here so pollution would be minused at the end
]

UPGRADES = {
    "oil_burners"
}

# Dictionary for which units give what resources, etc
INFRA = {
    ### Electricity (done) ###
    'coal_burners_plus': {'energy': 4}, # Energy increase
    'coal_burners_convert_minus': [{'coal': 48}], # Resource upkeep cost
    'coal_burners_money': 7800, # Monetary upkeep cost
    'coal_burners_effect': [{'pollution': 7}], # Pollution amount added

    'oil_burners_plus': {'energy': 5},
    'oil_burners_convert_minus': [{'oil': 56}],
    'oil_burners_money': 11700,
    'oil_burners_effect': [{'pollution': 5}],

    'hydro_dams_plus': {'energy': 6},
    'hydro_dams_money': 24000,

    'nuclear_reactors_plus': {'energy': 15}, 
    'nuclear_reactors_convert_minus': [{'uranium': 32}],
    'nuclear_reactors_money': 111000, 

    'solar_fields_plus': {'energy': 4},
    'solar_fields_money': 11000, 
    ####################

    ### Retail ### (Done)
    'gas_stations_plus': {'consumer_goods': 12},
    'gas_stations_effect': [{'pollution': 4}],
    'gas_stations_money': 20000,

    'general_stores_plus': {'consumer_goods': 10},
    'general_stores_effect': [{'pollution': 2}],
    'general_stores_money': 37500, 

    'farmers_markets_plus': {'consumer_goods': 16},
    'farmers_markets_effect': [{'pollution': 5}],
    'farmers_markets_money': 80000, 

    'banks_plus': {'consumer_goods': 20},
    'banks_money': 220000,

    'malls_plus': {'consumer_goods': 30},
    'malls_effect': [{'pollution': 10}],
    'malls_money': 450000, # Costs $750k
    ##############

    ### Public Works ### (Done)
    'city_parks_effect': [{'happiness': 5}],
    'city_parks_effect_minus': {'pollution': 6},
    'city_parks_money': 25000,

    'libraries_effect': [{'happiness': 5}, {'productivity': 3}],
    'libraries_money': 60000,

    'hospitals_effect': [{'happiness': 8}],   
    'hospitals_money': 85000,

    'universities_effect': [{'productivity': 10}, {'happiness': 4}],
    'universities_money': 175000,

    'monorails_effect': [{'productivity': 16}],
    'monorails_effect_minus': {'pollution': 20},
    'monorails_money': 270000,
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
    'farms_plus': {'rations': 20},
    'farms_effect': [{'pollution': 1}],

    'pumpjacks_money': 9500,
    'pumpjacks_plus': {'oil': 25},
    'pumpjacks_effect': [{'pollution': 2}],

    'coal_mines_money': 4200, # Costs $10k
    'coal_mines_plus': {'coal': 25},
    'coal_mines_effect': [{'pollution': 2}],

    'bauxite_mines_money': 8000, # Costs $8k
    'bauxite_mines_plus': {'bauxite': 20},
    'bauxite_mines_effect': [{'pollution': 2}],

    'copper_mines_money': 5000, # Costs $8k
    'copper_mines_plus': {'copper': 25},
    'copper_mines_effect': [{'pollution': 2}],

    'uranium_mines_money': 45000, # Costs $18k
    'uranium_mines_plus': {'uranium': 12},
    'uranium_mines_effect': [{'pollution': 1}],

    'lead_mines_money': 7200,
    'lead_mines_plus': {'lead': 16},
    'lead_mines_effect': [{'pollution': 2}],

    'iron_mines_money': 11000,
    'iron_mines_plus': {'iron': 25},
    'iron_mines_effect': [{'pollution': 2}],

    'lumber_mills_money': 7500,
    'lumber_mills_plus': {'lumber': 30},
    'lumber_mills_effect': [{'pollution': 1}],

    ################

    ### Processing (Done) ###
    'component_factories_money': 80000, # Costs $220k
    'component_factories_convert_minus': [{'copper': 20}, {'steel': 10}, {'aluminium': 15}],
    'component_factories_plus': {'components': 5},
    'component_factories_effect': [{'pollution': 5}],

    'steel_mills_money': 90000,
    'steel_mills_convert_minus': [{'coal': 35}, {'iron': 35}],
    'steel_mills_plus': {'steel': 12},
    'steel_mills_effect': [{'pollution': 4}],

    'ammunition_factories_money': 30000,
    'ammunition_factories_convert_minus': [{'copper': 10}, {'lead': 20}],
    'ammunition_factories_plus': {'ammunition': 12},
    'ammunition_factories_effect': [{'pollution': 3}],

    'aluminium_refineries_money': 72000,
    'aluminium_refineries_convert_minus': [{'bauxite': 15}],
    'aluminium_refineries_plus': {'aluminium': 16},
    'aluminium_refineries_effect': [{'pollution': 3}],

    'oil_refineries_money': 55000,
    'oil_refineries_convert_minus': [{'oil': 20}],
    'oil_refineries_plus': {'gasoline': 11},
    'oil_refineries_effect': [{'pollution': 6}]
}

MILDICT = {
    ## LAND
    "soldiers": {
        "price": 200,
        "resources": {"rations": 2},
        "manpower": 1
    },

    "tanks": {
        "price": 8000,
        "resources": {"steel": 5, "components": 5},
        "manpower": 4
    },

    "artillery": {
        "price": 16000,
        "resources": {"steel": 12, "components": 3},
        "manpower": 2
    },

    ## AIR
    "bombers": {
        "price": 25000,
        "resources": {"aluminium": 20, "steel": 5, "components": 6},
        "manpower": 1,
    },

    "fighters": {
        "price": 35000, 
        "resources": {"aluminium": 12, "components": 3},
        "manpower": 1,
    },

    "apaches": {
        "price": 32000,
        "resources": {"aluminium": 8, "steel": 2, "components": 4},
        "manpower": 1,
    },

    ## WATER
    "destroyers": {
        "price": 30000,
        "resources": {"steel": 30, "components": 7},
        "manpower": 6,
    },

    "cruisers": {
        "price": 55000, 
        "resources": {"steel": 60, "components": 12},
        "manpower": 5,
    },

    "submarines": {
        "price": 45000,
        "resources": {"steel": 20, "components": 8},
        "manpower": 6,
    },

    ## SPECIAL
    "spies": {
        "price": 25000, # Cost 25k
        "resources": {"rations": 50}, # Costs 50 rations
        "manpower": 0,
    },

    "icbms": {
        "price": 16000000, # Cost 16 million
        "resources": {"steel": 550}, 
        "manpower": 0,
    },

    "nukes": {
        "price": 80000000, 
        "resources": {"uranium": 1200, "steel": 900}, 
        "manpower": 0,
    }
}
