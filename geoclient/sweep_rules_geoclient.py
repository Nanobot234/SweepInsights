import requests
import json
import time
from  geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable


# Fetching the sweep rules statement for a given address
def get_sweep_rules_by_address(house_number, street_name, borough="Bronx"):
    address = f"{house_number} {street_name}, {borough}, NY"
    print(f"Looking up address: {address}")

    # Step 2. Geocode the address
    geolocator = Nominatim(user_agent="sweepnyc_lookup", timeout=10)  # Increased timeout

    try:
        location = geolocator.geocode(address)
    except GeocoderUnavailable:
        print("Geocoding service is unavailable. Retrying...")
        time.sleep(1)  # Add delay before retrying
        try:
            location = geolocator.geocode(address)
        except GeocoderUnavailable:
            return {"error": f"Could not geocode address: {address}"}

    if not location:
        return {"error": f"Could not geocode address: {address}"}

    lat, lon = location.latitude, location.longitude

    # Step 3. Call SweepNYC API
    url = "https://sweepnyc.nyc.gov/mappingapi/api/highlight/sweepinfo"
    params = {
        "lat": lat,
        "lon": lon,
        "radius": 0.5,
        "t": int(round(time.time() * 1000))  # timestamp in ms
    }

    try:
        r = requests.get(url, params=params, timeout=10)  # Increased timeout for API request
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        return {"error": f"Failed to fetch data: {e}"}

    # Step 4. Parse JSON response
    notes = data.get("Notes")
    if not notes:
        return {"address": address, "rules": [], "info": "No cleaning rules found"}

    try:
        notes_json = json.loads(notes)
        signs = notes_json.get("Signs", [])
        rules = [sign.get("SignText") for sign in signs if sign.get("SignText")]
    except Exception:
        rules = ["Error parsing cleaning rules"]

    # Step 5. Return structured results
    return {
        "address": address,
        "street": data.get("Street"),
        "rules": rules,
    }

  

#check when this is RUNNN
# # Example usage
# lat = 40.8665208
# lon = -73.8929462
# info = get_sweep_rules_by_latlon(lat, lon)
# print(info)
