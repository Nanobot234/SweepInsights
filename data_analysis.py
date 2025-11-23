from collections import Counter
from datetime import datetime, timedelta
import pandas as pd
from Utilities.analyze_parking_tickets import convert_time_format


"""Functions that analyze sweep data and provide insights."""

def get_most_likely_sweep_time_range(sweep_times):
    """
    Analyzes a list of sweep times and prints the most likely time range.

    Parameters:
        sweep_times (list): A list of time values (e.g., strings or datetime objects) representing street sweep times.

    Returns:
        None
    """

    time_objects = [datetime.strptime(time, "%H:%M") for time in sweep_times]

    intervals = []
    for time in time_objects:
        rounded_time = time.replace(minute=(time.minute // 30) * 30, second=0, microsecond=0)
        intervals.append(rounded_time)

    
    # # Count frequency of each interval
    interval_counts = Counter(intervals)

    # Find the most common interval
    most_common_interval, frequency = interval_counts.most_common(1)[0]

     # Calculate the percentage of times in the most common interval
    total_times = len(sweep_times)
    results = []
    percentage = (frequency / total_times) * 100

    # Format the interval as a readable range
    interval_start = most_common_interval
    interval_end = most_common_interval + timedelta(minutes=30)

    results.append({
        "interval": f"{interval_start.strftime('%H:%M')} - {interval_end.strftime('%H:%M')}",
        "frequency": frequency,
        "percentage": round(percentage, 2)  # Rounded to 2 decimal places
    })

   
    try:
        if not sweep_times:
            return {"status": "error", "message": "No sweep_times provided."}

        if total_times == 0:
            return {"status": "error", "message": "No valid sweep times after parsing."}

        counts_debug = {k.strftime("%H:%M"): v for k, v in interval_counts.items()}

        most = results[0] if results else None
        second = results[1] if len(results) > 1 else None

        return {
            "status": "success",
            "most_common": most,
            "second_most_common": second,
            "counts_debug": counts_debug,
            "total_samples": total_times
        }

    except Exception as e:
        return {"status": "error", "message": f"Exception: {e}"}

def calculate_ticket_likelihood_after_sweep(tracker,street_name, house_number, borough_code,most_likely_range=None):
    """
    Calculate the likelihood of receiving a parking ticket after a street sweep.

    Args:
        street_name (str): The name of the street.
        house_number (str): The house number on the street.
        borough_code (int): The borough code (1-5).

    Returns:
        dict: A dictionary containing likelihood percentages and scores such as "High", "Medium", or "Low" for risk
    """
    # Get sweep data
    last_swept_time = tracker.get_sweep_statuses(street_name, house_number, borough_code)
    if not last_swept_time or isinstance(last_swept_time, dict) and last_swept_time.get("status") == "error":
        return {"status": "error", "message": "No sweep data available for this block."}

    #get recent sweep time!! 
    recent_sweep_time = last_swept_time['last_swept']

    recent_sweep_time = pd.to_datetime(recent_sweep_time).time()

    print(f"Recent sweep time: {recent_sweep_time}")

    # Fetch parking violations for the block
    violations = tracker.data_fetcher.get_violations_for_whole_block(street_name, house_number, violation_code=21, borough_code=borough_code)

    if violations.empty:
        return {"status": "no_data", "message": "No parking violations found for this block."}

    # Step 3: Filter violations that occurred after the most recent sweep


    #check here!!
    # Convert 'Violation Time' to pandas
    
    violations['Violation Time'] = violations['Violation Time'].apply(_parse_violation_time)

    latest_time_in_range = datetime.strptime(most_likely_range['most_common']['interval'].split(" - ")[1], "%H:%M").time() #get latest time in most likely range

    # Add 10 minutes to the latest time
    latest_time_plus_10 = (datetime.combine(datetime.today(), latest_time_in_range) + timedelta(minutes=10)).time()


    violations_after_sweep = violations[violations['Violation Time'] > recent_sweep_time]
    violations_after_optimal_time_range = violations[(violations['Violation Time'] > latest_time_in_range)]
    violations_ten_minutes_after = violations[(violations['Violation Time'] > latest_time_plus_10)]
    # Step 4: Calculate likelihood
    total_violations = len(violations)
    violations_after_count = len(violations_after_sweep)
    likelihood_percentage = (violations_after_count / total_violations) * 100

    # Calculate likelihood for optimal time range
    violations_after_optimal_time_range_count = len(violations_after_optimal_time_range)
    likelihood_percentage_optimal = (violations_after_optimal_time_range_count / total_violations) * 100

    # Calculate likelihood for ten minutes after
    violations_ten_minutes_after_count = len(violations_ten_minutes_after)
    likelihood_percentage_ten_minutes = (violations_ten_minutes_after_count / total_violations) * 100

    def _score(p):
        return "High" if p > 50 else "Medium" if p > 20 else "Low"

    likelihood_score = _score(likelihood_percentage)
    likelihood_score_optimal = _score(likelihood_percentage_optimal)
    likelihood_score_ten_minutes = _score(likelihood_percentage_ten_minutes)

    print("Likelihood of receiving a parking ticket after sweep: " f"{likelihood_percentage:.2f}% ({likelihood_score})")

    # Return results
    return {
        "status": "success",
        "street_name": street_name,
        "house_number": house_number,
        "recent_sweep_time": recent_sweep_time,
        "total_violations": total_violations,
        "violations_after_sweep": violations_after_count,
        "likelihood_percentage": round(likelihood_percentage, 2),
        "likelihood_percentage_optimal": round(likelihood_percentage_optimal, 2),
        "likelihood_percentage_ten_minutes": round(likelihood_percentage_ten_minutes, 2),
        "likelihood_score": likelihood_score,
        "likelihood_score_optimal": likelihood_score_optimal,
        "likelihood_score_ten_minutes": likelihood_score_ten_minutes,
    }


def _parse_violation_time(t):
    """
    Parse violation time from string format to datetime.time object.
    Args:
        t (str): Time string in the format 'HHMMA' or 'HHM
        P'.
    Returns:
        datetime.time: Parsed time object.
    """
    if pd.isna(t):
        return pd.NaT

    s = str(t).strip().upper()

    # Handle formats like '0157A' or '1230P'
    if len(s) == 5 and s[-1] in ('A', 'P'):
        # Add missing 'M' to make 'AM' or 'PM'
        s = s[:-1] + s[-1] + 'M'  # e.g. '0807A' -> '0807AM'
        time_obj = convert_time_format_to_datetime(s)
        if time_obj is None:
            print(f"Failed to convert violation time: {t}")
            return pd.NaT
        return time_obj

    # Try parsing already well-formed strings like '0807AM' or '12:34 PM' or '08:07'
    try:
        # Directly parse '0807AM' style (6 chars, e.g. '0807AM')
        if len(s) == 6 and s[-2:] in ('AM', 'PM'):
            return datetime.strptime(s, "%I%M%p").time()

        # Try common human-readable formats
        for fmt in ("%I:%M %p", "%H:%M", "%I:%M%p"):
            try:
                return datetime.strptime(s, fmt).time()
            except ValueError:
                continue
    except Exception:
        pass

    # If all parsing fails, return NaT and log
    print(f"Unable to parse violation time: {t}")
    return pd.NaT


def convert_time_format_to_datetime(time_str):
    """
    Convert time from format '0157A' to a datetime.time object.

    Args:
        time_str (str): Time string in the format 'HHMMX', where X is 'A' or 'P'.

    Returns:
        datetime.time: Time object representing the converted time.
    """
    try:
        time_str = str(time_str).strip().upper()

        # Expected format is 6 characters like '0814AM'
        if len(time_str) != 6 or not time_str[-2:] in ['AM', 'PM']:
            raise ValueError(f"Invalid time format: {time_str}")

        # Parse the time string
        time_obj = datetime.strptime(time_str, "%I%M%p").time()
        return time_obj

    except Exception as e:
        print(f"Error converting time format: {e}")
        return None