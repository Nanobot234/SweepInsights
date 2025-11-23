from pathlib import Path
import sys
import os
from data.addresses import TEST_ADDRESSES # Import the test addresses
from data.visualizations import visualize_ticket_likelihood
from typing import List, Dict, Optional

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


def initialize_tracker() -> SweepTracker:
    """Initialize and return a SweepTracker instance."""
    return SweepTracker()

def check_street_status(
    tracker: SweepTracker, 
    full_street_name: str, 
    house_number: str, 
    borough_code: str
) -> Optional[Dict[str, str]]:
    """Check the street sweeping status for a given address."""
   # print("Example 1: Check when a street was last swept")
   # print("-" * 60)

    info = get_sweep_rules_by_address(house_number, full_street_name,borough_code)
    print(info["rules"][0])


        # Check sweep status for the address
    result = tracker.get_sweep_statuses(full_street_name, house_number, borough_code, num_records=1000)
    print(result)


    times = []
    result_arr = {}
    if result[0].get("last_swept"):
        times = [entry['last_swept'].split('T')[1].split(':')[0] + ':' + entry['last_swept'].split('T')[1].split(':')[1] for entry in result]
        print("Number of sweep records retrieved:", len(times))
       # print(times)

    if len(times) > 0:

        # Analyze most likely sweep time range and print results
        result_arr = get_most_likely_sweep_time_range(times)

        print(f"Most common interval: {result_arr['most_common']['interval']} "
              f"(Frequency: {result_arr['most_common']['frequency']}, "
              f"Percentage: {result_arr['most_common']['percentage']}%)")

        return result_arr
    else:
        print("No sweep times available to analyze.")
        return None

# FUNCTION NOT USED AT THE MOMENT< BUT MAYBE LATER>
def fetch_parking_violations(
    tracker: SweepTracker, 
    full_street_name: str, 
    house_number: str, 
    violation_code: int = 21
) -> None:
    """Fetch parking violations for a specific street and house number."""
    parking_data = tracker.data_fetcher.get_violations_for_whole_block(full_street_name, house_number, violation_code, limit=60000)
    print(f"Recent parking violations for street cleaning on {full_street_name} near {house_number}:")
    if not parking_data.empty:
         #print first 40 rows and the house number date, and street name
        print(parking_data.head(40)[['House Number', 'Issue Date', 'Street Name']])
    else:

        print("No recent parking violations found.")


def fetch_ticket_analysis_for_addresses(
    tracker: SweepTracker, 
    addresses: List[Dict[str, str]]
) -> List[Dict[str, str]]:
    """Fetch ticket analysis for multiple addresses."""
    results = []
    for address in addresses:
        full_street_name = address['street_name']
        house_number = address['house_number']
        borough_code = address['borough_code']

        most_likely_sweep_time_for_address = check_street_status(tracker,full_street_name,house_number,borough_code)

        if most_likely_sweep_time_for_address:
            result = calculate_ticket_likelihood_after_sweep(tracker, full_street_name, house_number, borough_code, most_likely_range=most_likely_sweep_time_for_address)
            results.append(result)

    return results




def main() -> None:
    """Main entry point for the application."""
    print("=" * 60)
    print("NYC Street Sweeping Tracker")
    print("=" * 60)
    print()

    tracker = initialize_tracker()

    full_street_name = "Valentine Ave"
    house_number = "2025"

    #need to figure out dealing with the numbers
    borough_code = BOROUGH_CODES['bronx']

    results_for_various_addresses = fetch_ticket_analysis_for_addresses(tracker, TEST_ADDRESSES)

    #print the list of results
    for result in results_for_various_addresses:
        print("The result for this address is:")
        print(result)

    visualize_ticket_likelihood(results_for_various_addresses)



    # time_range_result = check_street_status(tracker, full_street_name, house_number, borough_code)

    # print()

    # result = calculate_ticket_likelihood_after_sweep(tracker, full_street_name, house_number, borough_code, most_likely_range=time_range_result)


    # if result["status"] =="success":
    #     print("\nTicket Likelihood Analysis:")
    #     print("=" * 50)
    #     print(f"Street: {result['street_name']}")
    #     print(f"House Number: {result['house_number']}")
    #     print(f"Most Recent Sweep Time: {result['recent_sweep_time']}")
    #     print(f"Total Violations: {result['total_violations']}")
    #     print(f"Violations After Sweep: {result['violations_after_sweep']}")
    #     print(f"Likelihood Percentage: {result['likelihood_percentage']}%")
    #     print(f"Likelihood Percentage (Optimal): {result['likelihood_percentage_optimal']}%")
    #     print(f"Likelihood Percentage (10 min): {result['likelihood_percentage_ten_minutes']}%")
    #     print(f"Likelihood Score: {result['likelihood_score']}")
    #     print(f"Likelihood Score (Optimal): {result['likelihood_score_optimal']}")
    #     print(f"Likelihood Score (10 min): {result['likelihood_score_ten_minutes']}")
    # else:
    #     print(f"Error: {result.get('message', 'Unknown error occurred.')}")
   # fetch_parking_violations(tracker, full_street_name, house_number)
 #   fetch_violations_for_both_sides(tracker, full_street_name, house_number)

if __name__ == "__main__":
    main()

