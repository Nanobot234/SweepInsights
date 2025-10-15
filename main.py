from pathlib import Path
import sys
import os

# Ensure project root (parent of this package dir) is on sys.path so `import data.*` works
_project_root = Path(__file__).resolve().parent.parent
print(f"Project root directory: {_project_root}")  # Add this line to print the project root

if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Also set PYTHONPATH for subprocesses (optional)
os.environ.setdefault("PYTHONPATH", str(_project_root))

from data.sweep_tracker import SweepTracker
from config import BOROUGH_CODES
from geoclient.sweep_rules_geoclient import get_sweep_rules_by_address # Import the function
from data_analysis import get_most_likely_sweep_time_range



def main():

    print("=" * 60)
    print("NYC Street Sweeping Tracker")
    print("=" * 60)
    print()


    #Initialize tracker
    tracker = SweepTracker()

    #Example 1: Check street status for an  address

    print("Example 1: Check when a street was last swept")
    print("-" * 60)

    full_street_name = "Walton AVE"
    house_number = "2320"
    borough_code = BOROUGH_CODES['bronx']


    info = get_sweep_rules_by_address(house_number, full_street_name)
    print(info["rules"][0])

    result = tracker.get_sweep_statuses(full_street_name, house_number, borough_code, num_records=1000)

   # block_info = tracker.data_fetcher.get_current_block_info()  # gets the lowest, highest, and middle house numbers for the current block


        #get a number of recent sweep records

    ''' Getting parking violations for a street'''
    parking_data = tracker.data_fetcher.get_parking_violations_by_street(full_street_name, house_number)
    print(f"Recent parking violations for street cleaning on {full_street_name} near {house_number}:")
    if not parking_data.empty:
        print(parking_data)
    else:
        print("No recent parking violations found.")

    times = [entry['last_swept'].split('T')[1].split(':')[0] + ':' + entry['last_swept'].split('T')[1].split(':')[1] for entry in result]
    print(times)

    result_arr = get_most_likely_sweep_time_range(times)

    #print the result
    print(f"Most common interval: {result_arr['most_common']['interval']} "
      f"(Frequency: {result_arr['most_common']['frequency']}, "
      f"Percentage: {result_arr['most_common']['percentage']}%)")

# Print the second most common interval
    if result_arr['second_most_common']:
        print(f"Second most common interval: {result_arr['second_most_common']['interval']} "
          f"(Frequency: {result_arr['second_most_common']['frequency']}, "
          f"Percentage: {result_arr['second_most_common']['percentage']}%)")
    else:
        print("No second most common interval found.")

    
    # street_rules_info = get_sweep_rules_by_address(house_number, full_street_name, "Bronx")

    # if isinstance(result, list):

    #     print(f"Rules are: {street_rules_info['rules'][0]}")
    #     for idx, res in enumerate(result, 1):
    #         print(f"Result {idx}:")
    #         if res.get('status') == 'success':
    #             print(f"✓ Address: {res['address']}")
    #             print(f"✓ Physical ID: {res['physical_id']}")
    #             print(f"✓ Last Swept: {res['last_swept']}")
    #         else:
    #             print(f"✗ Error: {res.get('message', 'Unknown error')}")
    #         print("-" * 40)
    # else:
    #     if result.get('status') == 'success':
    #         print(f"✓ Address: {result['address']}")
    #         print(f"✓ Physical ID: {result['physical_id']}")
    #         print(f"✓ Last Swept: {result['last_swept']}")
    #     else:
    #         print(f"✗ Error: {result.get('message', 'Unknown error')}")

    #risk score for a street getting that!

if __name__ == "__main__":
    main()

