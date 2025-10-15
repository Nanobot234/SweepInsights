from sodapy import Socrata
from config import SOCRATA_DOMAIN, SOCRATA_APP_TOKEN, DATASET_IDS

def test_basic_query():
    client = Socrata(SOCRATA_DOMAIN, SOCRATA_APP_TOKEN)
    
    try:
        # Try a very basic query without specific columns
        results = client.get(
            DATASET_IDS['street_centerline'],
            limit=1
        )
        
        if results:
            print("\nSuccessful query!")
            print("Available fields:")
            for key in results[0].keys():
                print(f"- {key}")
            return results[0]
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    print("Testing basic query to street centerline dataset...")
    result = test_basic_query()
    
    if result:
        print("\nExample record:")
        print("=" * 50)
        for key, value in result.items():
            print(f"{key}: {value}")