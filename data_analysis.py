from collections import Counter
from datetime import datetime, timedelta

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

   
    return {
        "most_common": results[0],
        "second_most_common": results[1] if len(results) > 1 else None
    }
    


    # #count frequency of each time
    # time_counts = Counter(sweep_times)

    # #sorted times by Value(earliest time first)
    # sorted_times = sorted(time_counts.keys())

    # print("All recorded sweep times (occurences):")
    # print(time_counts)
    # # Find the most frequent earliest time
    # most_frequent_earliest_time = max(sorted_times, key=lambda t: (time_counts[t]))

    # #now i want to find the most frequent latest time
    # most_frequent_latest_time = sorted_times[2]

    # print("Range of times street was swept:")
    # print(f"From {most_frequent_earliest_time} to {most_frequent_latest_time}")