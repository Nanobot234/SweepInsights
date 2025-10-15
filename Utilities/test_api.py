from sodapy import Socrata
from config import SOCRATA_DOMAIN, SOCRATA_APP_TOKEN, DATASET_IDS

def test_api(street_name, violation_code):
    client = Socrata(SOCRATA_DOMAIN, SOCRATA_APP_TOKEN)
    
    # Simple test query
    try:
        where_clause = f"violation_code='{violation_code}' AND street_name='{street_name}'"
        results = client.get(
            DATASET_IDS['parking_violations_2024'],
            where=where_clause,
            limit=1
        )
        print("Success! Found:", results)
    except Exception as e:
        print(f"Error accessing API: {e}")

if __name__ == "__main__":
    test_api("VALENTINE AVENUE", "21")