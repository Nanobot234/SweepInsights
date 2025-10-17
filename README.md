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
## Key Files
