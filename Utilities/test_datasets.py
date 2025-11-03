from sodapy import Socrata
from config import SOCRATA_DOMAIN, SOCRATA_APP_TOKEN

def test_datasets():
    client = Socrata(SOCRATA_DOMAIN, SOCRATA_APP_TOKEN)

    # Updated dataset ID to test
    dataset_ids = [
        'pvqr-7yc4',  # Updated dataset ID
    ]

    print("Testing NYC Street Centerline dataset IDs...")
    print("=" * 50)

    for dataset_id in dataset_ids:
        try:
            # Try to get just one record
            results = client.get(dataset_id, limit=1)
            print(f"\nDataset ID {dataset_id}: SUCCESS")
            print("Sample columns:", list(results[0].keys()) if results else "No data")
            return dataset_id  # Return the first working dataset ID
        except Exception as e:
            print(f"\nDataset ID {dataset_id}: FAILED")
            print(f"Error: {str(e)}")

    return None

if __name__ == "__main__":
    working_id = test_datasets()
    if working_id:
        print(f"\nFound working dataset ID: {working_id}")
        print("Update your config.py with this ID")
    else:
        print("\nNo working dataset IDs found. You may need to:")
        print("1. Get an app token from https://data.cityofnewyork.us/profile/app_tokens")
        print("2. Check the current dataset ID at https://data.cityofnewyork.us/")