# SweepInsights

A Python application that enables NYC drivers to buy back their time from alternate side parking rules.

## Features

- ✓ Calculate the most likely timeframe that a sweeper machine will pass on a NYC block.
- ✓ Calculate risk scores based on historical parking tickets
- ✓ View recent parking violations for any street
- ✓ Automatic caching of address lookups
- ✓ Support for all NYC boroughs

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. (Optional) Get Socrata App Token

For higher API rate limits (100,000 requests/day vs 1,000), get a free token:

1. Go to https://data.cityofnewyork.us/profile/app_tokens
2. Sign up or log in
3. Create a new app token
4. Add it to `config.py`:

```python
SOCRATA_APP_TOKEN = "your_token_here"
```

### 3. Run the Application

```bash
python main.py
```

SweepInsights/
├── requirements.txt      # Python dependencies
├── config.py             # Configuration settings
├── data_analysis.py      # Functions for analyzing sweep data and providing insights
├── main.py               # Entry point for the application
├── README.md             # Project documentation
├── cache/
│   └── address_cache.json  # Cached address-to-physical ID mappings
├── data/
│   ├── address_mapper.py  # Address-to-PhysicalID mapping with caching
│   ├── data_fetcher.py    # API data fetching logic for NYC Open Data
│   ├── sweep_tracker.py   # Main tracking logic for street sweeping data
│   └── __pycache__/       # Compiled Python files for the `data` module
├── geoclient/
│   ├── sweep_rules_geoclient.py  # Fetches sweep rules for a given address using geolocation
│   └── __pycache__/              # Compiled Python files for the `geoclient` module
├── network/              # (Empty directory, purpose not defined yet)
├── rules/                # (Empty directory, purpose not defined yet)
├── tests/                # (Empty directory, purpose not defined yet)
├── Utilities/
│   ├── check_columns.py  # Utility script to check available columns in datasets
│   ├── config.py         # Duplicate configuration file (may need cleanup)
│   ├── test_api.py       # Tests API queries for parking violations
│   ├── test_basic_query.py  # Tests basic queries to the street centerline dataset
│   ├── test_datasets.py  # Tests multiple dataset IDs for compatibility
│   ├── test_signs.py     # Tests fetching alternate side parking sign data
│   └── __pycache__/      # Compiled Python files for the `Utilities` module
└── .vscode/
    └── settings.json     # VS Code workspace settings for Python analysis
