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
from data_analysis import get_most_likely_sweep_time_range, calculate_ticket_likelihood_after_sweep


def initialize_tracker():
    return SweepTracker()

def check_street_status(tracker, full_street_name, house_number, borough_code):
    print("Example 1: Check when a street was last swept")
    print("-" * 60)

    info = get_sweep_rules_by_address(house_number, full_street_name)
    print(info["rules"][0])

    result = tracker.get_sweep_statuses(full_street_name, house_number, borough_code, num_records=1000)
    times = [entry['last_swept'].split('T')[1].split(':')[0] + ':' + entry['last_swept'].split('T')[1].split(':')[1] for entry in result]
    print("Number of sweep records retrieved:", len(times))
    print(times)

    result_arr = get_most_likely_sweep_time_range(times)

    print(f"Most common interval: {result_arr['most_common']['interval']} "
          f"(Frequency: {result_arr['most_common']['frequency']}, "
          f"Percentage: {result_arr['most_common']['percentage']}%)")

    if result_arr['second_most_common']:
        print(f"Second most common interval: {result_arr['second_most_common']['interval']} "
              f"(Frequency: {result_arr['second_most_common']['frequency']}, "
              f"Percentage: {result_arr['second_most_common']['percentage']}%)")
    else:
        print("No second most common interval found.")

def fetch_parking_violations(tracker, full_street_name, house_number,violation_code=21):
    parking_data = tracker.data_fetcher.get_violations_for_whole_block(full_street_name, house_number, violation_code, limit=60000)
    print(f"Recent parking violations for street cleaning on {full_street_name} near {house_number}:")
    if not parking_data.empty:
         #print first 40 rows and the house number date, and street name
        print(parking_data.head(40)[['House Number', 'Issue Date', 'Street Name']])
    else:

        print("No recent parking violations found.")


def main():
    print("=" * 60)
    print("NYC Street Sweeping Tracker")
    print("=" * 60)
    print()

    tracker = initialize_tracker()

    full_street_name = "Valentine Ave"
    house_number = "2544"
    borough_code = BOROUGH_CODES['bronx']

    check_street_status(tracker, full_street_name, house_number, borough_code)

    print()

    result = calculate_ticket_likelihood_after_sweep(tracker, full_street_name, house_number, borough_code)

    if result["status"] =="success":
        print("\nTicket Likelihood Analysis:")
        print("=" * 50)
        print(f"Street: {result['street_name']}")
        print(f"House Number: {result['house_number']}")
        print(f"Most Recent Sweep Time: {result['recent_sweep_time']}")
        print(f"Total Violations: {result['total_violations']}")
        print(f"Violations After Sweep: {result['violations_after_sweep']}")
        print(f"Likelihood Percentage: {result['likelihood_percentage']}%")
        print(f"Likelihood Score: {result['likelihood_score']}")
    else:
        print(f"Error: {result.get('message', 'Unknown error occurred.')}")
   # fetch_parking_violations(tracker, full_street_name, house_number)
 #   fetch_violations_for_both_sides(tracker, full_street_name, house_number)

if __name__ == "__main__":
    main()

