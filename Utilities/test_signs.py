from sodapy import Socrata
from config import SOCRATA_DOMAIN, SOCRATA_APP_TOKEN

def test_sign_data():
    client = Socrata(SOCRATA_DOMAIN, SOCRATA_APP_TOKEN)
    
    try:
        # First, get just one record to see the structure
        results = client.get(
            'qt6m-xctn',  # Street Sign Work Orders dataset
            limit=1
        )
        
        if results:
            print("\nAvailable columns:")
            print("=" * 50)
            for key in results[0].keys():
                print(f"- {key}: {results[0][key]}")
                
        # Now try to get some actual alternate side parking signs
        print("\nTesting alternate side parking query:")
        print("=" * 50)
        test_results = client.get(
            'qt6m-xctn',
            where="sign_description LIKE '%ALTERNATE%'",
            limit=2
        )
        
        if test_results:
            print(f"\nFound {len(test_results)} results:")
            for sign in test_results:
                print("\nSign details:")
                for key, value in sign.items():
                    print(f"{key}: {value}")
        else:
            print("No alternate side parking signs found")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_sign_data()