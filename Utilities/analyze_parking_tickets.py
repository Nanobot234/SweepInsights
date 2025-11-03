import pandas as pd
from data.data_fetcher import DataFetcher
from geoclient.sweep_rules_geoclient import get_sweep_rules_by_address

# Ensure all rows are displayed when printing DataFrames
pd.set_option('display.max_rows', None)

def convert_time_format(time_str):
    """
    Convert time from format '0157A' to '01:57 AM'.

    Args:
        time_str (str): Time string in the format 'HHMMX', where X is 'A' or 'P'.

    Returns:
        str: Time string in the format 'HH:MM AM/PM'.
    """
    try:
        # Extract hour, minute, and period
        hour = int(time_str[:2])
        minute = int(time_str[2:4])
        period = 'AM' if time_str[4] == 'A' else 'PM'

        # Format the time
        return f"{hour:02}:{minute:02} {period}"
    except Exception as e:
        print(f"Error converting time format: {e}")
        return None


def analyze_parking_tickets(street_name, house_number, violation_code=21):
    """
    Analyze parking tickets for a given street address and show how they vary by date and time.

    Args:
        street_name (str): The name of the street (e.g., "Valentine Ave").
        house_number (str): The house number (e.g., "2544").
        violation_code (int): The violation code to filter by (default is 21 for street cleaning).

    Returns:
        None
    """
    # Initialize DataFetcher with the path to the CSV file
    data_fetcher = DataFetcher(data_path="/Users/nanabonsu/Downloads/StreetCleaningViolations.csv")

    # Fetch parking violations for the entire block
    print(f"Fetching parking violations for {street_name} near {house_number}...")
    violations = data_fetcher.get_violations_for_whole_block(street_name, house_number, violation_code)

    info = get_sweep_rules_by_address(house_number, street_name)
    print(info["rules"][0]) #print the sweep rules for the address

    if violations.empty:
        print(f"No parking violations found for {street_name} near {house_number}.")
        return

    # Convert the "Issue Date" column to datetime
    violations['Issue Date'] = pd.to_datetime(violations['Issue Date'])

    # Convert the "Violation Time" column to standard time format
    violations['Violation Time'] = violations['Violation Time'].apply(convert_time_format)

    # Extract date and time components
    violations['Date'] = violations['Issue Date'].dt.date
    violations['Time'] = violations['Violation Time']

    # Group by date and count violations
    violations_by_date = violations.groupby('Date').size().reset_index(name='Count')

    # Group by time and count violations
    violations_by_time = violations.groupby('Time').size().reset_index(name='Count')

    # Group by month and count violations
    violations['Month'] = violations['Issue Date'].dt.month
    violations_by_month = violations.groupby('Month').size().reset_index(name='Count')

    # Display results
    print("\nParking Violations by Date:")
    print("=" * 50)
    print(violations_by_date)

    print("\nParking Violations by Time:")
    print("=" * 50)
    print(violations_by_time)

    print("\nParking Violations by Month:")
    print("=" * 50)
    print(violations_by_month)

    # Optional: Plot the results (requires matplotlib)
    try:
        # import matplotlib.pyplot as plt

        # # Plot violations by date
        # plt.figure(figsize=(10, 5))
        # plt.plot(violations_by_date['Date'], violations_by_date['Count'], marker='o')
        # plt.title(f"Parking Violations by Date for {street_name}")
        # plt.xlabel("Date")
        # plt.ylabel("Number of Violations")
        # plt.grid()
        # plt.xticks(rotation=45)
        # plt.tight_layout()
        # plt.show()

        # Plot violations by time
        try:
            import matplotlib.pyplot as plt

            # Prepare data for plotting
            violations_by_time['Time'] = pd.to_datetime(violations_by_time['Time'], format='%I:%M %p').dt.time

            # Filter times to 30-minute increments starting at the hour
            filtered_times = violations_by_time['Time'].apply(
                lambda t: t.replace(minute=(0 if t.minute < 30 else 30), second=0)
            )
            violations_by_time['Filtered Time'] = filtered_times

            # Aggregate data by 30-minute increments
            aggregated_data = violations_by_time.groupby('Filtered Time').size().reset_index(name='Count')

            plt.figure(figsize=(12, 6))
            plt.bar(aggregated_data['Filtered Time'].astype(str), aggregated_data['Count'], color='purple', alpha=0.7)
            plt.title(f"Parking Violations by Time for {street_name}", fontsize=14)
            plt.xlabel("Time (30-Minute Increments)", fontsize=12)
            plt.ylabel("Number of Violations", fontsize=12)
            plt.grid(axis='y', linestyle='--', alpha=0.6)
            plt.xticks(rotation=45, fontsize=10)
            plt.tight_layout()
            plt.show()

        except ImportError:
            print("\nMatplotlib is not installed. Skipping plots.")

        # Plot violations by month
        plt.figure(figsize=(10, 5))
        plt.bar(violations_by_month['Month'], violations_by_month['Count'], color='blue')
        plt.title(f"Parking Violations by Month for {street_name}")
        plt.xlabel("Month")
        plt.ylabel("Number of Violations")
        plt.grid(axis='y')
        plt.xticks(range(1, 13), ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
        plt.tight_layout()
        plt.show()

    except ImportError:
        print("\nMatplotlib is not installed. Skipping plots.")

if __name__ == "__main__":
    # Example usage
    print("Enter the street name (e.g., 'Valentine Ave'):")
    street_name = input().strip()

    print("Enter the house number (e.g., '2544'):")
    house_number = input().strip()

    analyze_parking_tickets(street_name, house_number)