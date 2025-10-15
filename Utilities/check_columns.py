from sodapy import Socrata
from config import SOCRATA_DOMAIN, SOCRATA_APP_TOKEN, DATASET_IDS

def check_columns():
    client = Socrata(SOCRATA_DOMAIN, SOCRATA_APP_TOKEN)
    
    try:
        # Get just one record to see the column names
        results = client.get(
            DATASET_IDS['sweep_nyc'],
            select="*",
            limit=1
        )
        if results:
            print("\nAvailable columns:")
            print("=" * 50)
            for key in results[0].keys():
                print(f"- {key}")
        else:
            print("No data returned")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_columns()