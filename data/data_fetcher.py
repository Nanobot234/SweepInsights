import os
from sodapy import Socrata
import pandas as pd
from config import SOCRATA_DOMAIN, SOCRATA_APP_TOKEN, DATASET_IDS, BOROUGH_CODES

class DataFetcher: 

    def __init__(self, data_path):
        """
        Initialize the DataFetcher class.

        Args:
            data_path (str): Path to the directory containing CSV files.
        """
        self.client = Socrata(SOCRATA_DOMAIN, SOCRATA_APP_TOKEN)
        self.current_block_low = None  # Track the lower bound of the current block range
        self.current_block_high = None  # Track the upper bound of the current block range
        self.current_block_middle = None  # Track the middle of the current block range
        self.data_path = data_path

        self.violations_data = None  # Placeholder for loaded violations data

    def load_csv_data(self, file_path):
        """
        Load data from a CSV file into a DataFrame.

        Args:
            file_path (str): Path to the CSV file.
        """
        try:
            self.violations_data = pd.read_csv(file_path)
            print(f"Loaded {len(self.violations_data)} rows from the CSV file.")
        except Exception as e:
            print(f"Error loading CSV data: {e}")
            self.violations_data = pd.DataFrame()  # Initialize as an empty DataFrame in case of error

    def load_csv_for_borough(self, borough_code):
        """
        Load the appropriate CSV file based on the borough code.

        Args:
            borough_code (str): The borough code (e.g., '1' for Manhattan, '2' for Bronx).
        """
        # Get the borough name corresponding to the borough code
        borough_name = next((name for name, code in BOROUGH_CODES.items() if code == borough_code), None)
        if not borough_name:
            print(f"Invalid borough code: {borough_code}")
            self.violations_data = pd.DataFrame()  # Initialize as an empty DataFrame
            return

        # Construct the file path for the borough's CSV file
        file_path = os.path.join(self.data_path, f"{borough_name.lower().replace(' ', '')}StreetCleaningViolations.csv")
        if not os.path.exists(file_path):
            print(f"CSV file not found for borough: {borough_name} ({file_path})")
            self.violations_data = pd.DataFrame()  # Initialize as an empty DataFrame
            return

        # Load the CSV data
        try:
            self.violations_data = pd.read_csv(file_path)
            print(f"Loaded {len(self.violations_data)} rows from {file_path}")
        except Exception as e:
            print(f"Error loading CSV file for borough {borough_name}: {e}")
            self.violations_data = pd.DataFrame()  # Initialize as an empty DataFrame

    def get_street_centerline_by_address(self, full_street_name, house_number, borough_code=None):
        """
        Find street segment (physical_id) for a given address.

        Args:
            full_street_name (str): Street name (e.g., "BLEECKER ST").
            house_number (int): House number (e.g., 123).
            borough_code (str, optional): Borough code (1-5).

        Returns:
            list: List of matching records with physical_id.
        """
        # Normalize and validate inputs
        full_street_name = full_street_name.upper().strip()
        house_number_str = str(house_number or '')
        try:
            house_number_int = int(house_number_str)
        except Exception:
            house_number_int = None

        # Build Socrata WHERE clause for querying the dataset
        where_clause = f"""
        (full_street_name = '{full_street_name}')
        AND (
            (l_low_hn <= '{house_number_str}' AND l_high_hn >= '{house_number_str}')
            OR
            (r_low_hn <= '{house_number_str}' AND r_high_hn >= '{house_number_str}')
        )
        """

        if borough_code:
            where_clause += f" AND boroughcode = '{borough_code}'"

        # Query the Socrata API
        try:
            results = self.client.get(
                "inkn-q76z",  # Dataset ID for Street Centerline
                where=where_clause,
                select="physicalid, full_street_name, l_low_hn, l_high_hn, r_low_hn, r_high_hn, boroughcode",
                limit=3  # Limit to the top 3 results
            )

            print(f"Street centerline results count: {len(results)}")

            # Filter results by proximity if numeric house number is provided
            if house_number_int is not None:
                filtered_results = [
                    segment for segment in results
                    if abs(int(segment['l_low_hn']) - house_number_int) <= 100 and abs(int(segment['r_low_hn']) - house_number_int) <= 100
                ]
            else:
                filtered_results = list(results)

            # Process the first result to determine the side of the street
            if filtered_results:
                first_result = filtered_results[0]

                try:
                    left_side = (int(first_result['l_low_hn']) <= house_number_int <= int(first_result['l_high_hn'])) if house_number_int is not None else False
                except Exception:
                    left_side = False

                if left_side:
                    self.current_block_low = first_result['l_low_hn']
                    self.current_block_high = first_result['l_high_hn']
                    self.current_side = 'L'
                else:
                    self.current_block_low = first_result['r_low_hn']
                    self.current_block_high = first_result['r_high_hn']
                    self.current_side = 'R'

                try:
                    self.current_block_middle = str((int(self.current_block_low) + int(self.current_block_high)) // 2)
                except Exception:
                    self.current_block_middle = None

                return filtered_results
            return []

        except Exception as e:
            print(f"Error fetching street centerline: {e}")
            return []

    def get_sweep_data(self, physical_id, limit=1):
        """
        Get the last swept date/time for a physical_id.

        Args:
            physical_id (str): Street segment physical ID.
            limit (int): Maximum number of records to fetch.

        Returns:
            list or None: List of sweep data records or None if an error occurs.
        """
        try:
            results = self.client.get(
                DATASET_IDS['sweep_nyc'],
                where=f"physical_id='{physical_id}'",
                order="date_visited DESC",
                limit=limit
            )

            if results:
                return results  # Return all records up to the requested limit
            return None
        except Exception as e:
            print(f"Error fetching sweep data: {e}")
            return None

    def get_violations_for_whole_block(self, street_name, house_number, violation_code=21, limit=10000, borough_code=None):
        """
        Get parking violations for both sides of the street within the current block range.

        Args:
            street_name (str): Street name.
            house_number (int): House number.
            violation_code (int): Violation code (default is 21 for street cleaning).
            limit (int): Maximum number of results.
            borough_code (str, optional): Borough code.

        Returns:
            dict or pd.DataFrame: Violations data or error message.
        """
        centerline_data = self.get_street_centerline_by_address(street_name, house_number)

        if not centerline_data:
            return {"error": "Address not found in NYC Street Centerline database"}

        # Extract block ranges for both sides of the street
        block_info = centerline_data[0]
        house_number = str(house_number)
        left_side = (block_info['l_low_hn'] <= house_number <= block_info['l_high_hn'])

        if left_side:
            block_range = (block_info['l_low_hn'], block_info['l_high_hn'])
            print(f"House number {house_number} is on the LEFT side of the street.")
        else:
            block_range = (block_info['r_low_hn'], block_info['r_high_hn'])
            print(f"House number {house_number} is on the RIGHT side of the street.")

        violations = self.get_parking_violations_by_street(
            street_name,
            violation_code,
            borough_code=borough_code,
            house_number=house_number,
            block_range=block_range,
            limit=limit
        )
        return violations

    def get_parking_violations_by_street(self, street_name, violation_code=21, borough_code=None, house_number=None, limit=6000, block_range=None):
        """
        Fetch parking violations for a given street name and violation code, optionally within a block range.

        Args:
            street_name (str): The name of the street to search for violations.
            violation_code (int): The violation code to filter by (default is 21 for street cleaning).
            borough_code (str, optional): Borough code.
            house_number (str, optional): House number.
            limit (int): Maximum number of results to return.
            block_range (tuple, optional): Tuple specifying the (low, high) house number range.

        Returns:
            pd.DataFrame: DataFrame containing the parking violations matching the criteria.
        """
        # Load the relevant borough CSV file
        self.load_csv_for_borough(borough_code)

        if self.violations_data.empty:
            print("Violations data is not loaded. Make sure to load it before querying.")
            return pd.DataFrame()

        # Filter data by street name and violation code
        filtered_data = self.violations_data[
            (self.violations_data['Street Name'] == street_name) &
            (self.violations_data['Violation Code'] == violation_code)
        ]

        if house_number is not None and block_range:
            low, high = block_range
            filtered_data = filtered_data[
                (filtered_data['House Number'] >= str(low)) & (filtered_data['House Number'] <= str(high))
            ]

        print(f"Filtered {len(filtered_data)} violations for street '{street_name}' with code {violation_code}.")
        return filtered_data


