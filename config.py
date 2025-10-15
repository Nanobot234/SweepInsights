


# Configuration file for NYC Street Sweeping Tracker

# Socrata API Configuration
SOCRATA_DOMAIN = "data.cityofnewyork.us"
SOCRATA_APP_TOKEN = "9w7K6nm2xXI9j3d4n59R250Jj" # Get free token at: https://data.cityofnewyork.us/profile/app_tokens

# Dataset IDs
DATASET_IDS = {
    'parking_violations_2024': 'pvqr-7yc4',
    'street_centerline': 'inkn-q76z',
    'sweep_nyc': 'c23c-uwsm',
    'street_signs': 'qt6m-xctn'
}

# Borough Codes
BOROUGH_CODES = {
    'manhattan': '1',
    'bronx': '2',
    'brooklyn': '3',
    'queens': '4',
    'staten island': '5'
}

# Cache settings
CACHE_FILE = 'cache/address_cache.json'
ENABLE_CACHE = True
