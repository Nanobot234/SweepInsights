import os
from sodapy import Socrata
import pandas as pd
from config import SOCRATA_DOMAIN, SOCRATA_APP_TOKEN, DATASET_IDS

class DataFetcher: 

    def __init__(self,data_path):
        self.client = Socrata(SOCRATA_DOMAIN, SOCRATA_APP_TOKEN)
        self.current_block_low = None # track current block range
        self.current_block_high = None
        self.current_block_middle = None
        self.data_path = data_path
        self.violations_data = None

        self.load_csv_data(self.data_path)
        '''
        Find street segment (physical_id) for a given address
        
        Args:
            street_name: Street name (e.g., "BLEECKER ST")
            house_number: House number (e.g., 123)
            borough_code: Optional borough code (1-5)
        
        Returns:
            List of matching records with physical_id
        '''

    def load_csv_data(self, file_path):
        try:
            self.violations_data = pd.read_csv(file_path)
            print(f"Loaded {len(self.violations_data)} rows from the CSV file.")
        except Exception as e:
            print(f"Error loading CSV data: {e}")
            self.violations_data = pd.DataFrame()
    
        #continue here to load the relevant CSV.
    def get_street_centerline_by_address(self, full_street_name, house_number, borough_code=None):
        full_street_name = full_street_name.upper().strip()
        house_number_str = str(house_number or '')
        try:
            house_number_int = int(house_number_str)
        except Exception:
            house_number_int = None

        # Build Socrata WHERE clause
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

        try:
            results = self.client.get(
                "inkn-q76z",  # dataset ID for Street Centerline
                where=where_clause,
                select="physicalid, full_street_name, l_low_hn, l_high_hn, r_low_hn, r_high_hn, boroughcode",
                #order by the closest house number to the one we are looking for
                #limit=1,  # Limit to the closest match
                limit=3
            )

            print(f"Street centerline results count: {len(results) }")  
            # Filter results by proximity if numeric house number provided
            if house_number_int is not None:
                filtered_results = [
                    segment for segment in results
                    if abs(int(segment['l_low_hn']) - house_number_int) <= 100 and abs(int(segment['r_low_hn']) - house_number_int) <= 100
                ]
            else:
                filtered_results = list(results)

            if filtered_results:
                first_result = filtered_results[0]

                # Determine side of street
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
        '''
        Get last swept date/time for a physical_id
        
        Args:
            physical_id: Street segment physical ID
        
        Returns:
            Dictionary with sweep data or None
        '''
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



    '''
        Get parking violations for a street
        
        Args:
            street_name: Street name
            violation_code: Violation code (21 = street cleaning)
            limit: Max number of results
        
        Returns:
            DataFrame of violations
        '''

    def get_current_block_info(self):
        '''
        Returns the current block range and side of street based on the last address lookup.
        
        Returns:
            Dictionary with 'low', 'high', and 'side' keys or None if not set
        '''
        if self.current_block_low is not None and self.current_block_high is not None and self.current_side is not None:
            return {
                'low': self.current_block_low,
                'high': self.current_block_high,
                'middle': self.current_block_middle,
                'side': self.current_side
            }
        return None

    #thois function may not be needed, liek gettign boths ides of the street tho
    def get_violations_for_whole_block(self, street_name, house_number, violation_code=21, limit=10000):
        '''
        Get parking violations for both sides of the street within the current block range.
        
        Args:
            street_name: Street name
            violation_code: Violation code (21 = street cleaning)
            limit: Max number of results
        
        Returns:
            DataFrame of violations, maybe dictionary
        '''
        centerline_data = self.get_street_centerline_by_address(street_name, house_number)

        print(centerline_data)

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
            house_number=house_number,
            block_range=block_range,
            limit=limit
        )
        return violations
    #continue from here! 

    def get_parking_violations_by_street(self, street_name, violation_code=21, house_number=None, limit=6000, block_range=None):
        """
        Fetch parking violations for a given street name and violation code, optionally within a block range.

        Args:
            street_name (str): The name of the street to search for violations.
            violation_code (int)): The violation code to filter by (default is 21 for street cleaning).
            limit (int): Maximum number of results to return (default is 100).
            block_range (tuple or None): Optional tuple specifying the (low, high) house number range.

        Returns:
            pd.DataFrame: DataFrame containing the parking violations matching the criteria.
        """
       # street_name = street_name.upper().strip()

        pd.set_option('display.max_rows', None)  # Ensure all rows are displayed

        if self.violations_data.empty:
            print("Violations data is not loaded make sure to load it before querying.")
            return pd.DataFrame()

        filtered_data = self.violations_data[
            (self.violations_data['Street Name'] == street_name) &
            (self.violations_data['Violation Code'] == violation_code)
        ]

    #this is the filtered violations for the one on the block tho!
        print(f"Total violations found for street '{street_name}' with code {violation_code}: {len(filtered_data)}")

        # house_number = str(house_number)
        #     filtered_data = filtered_data[filtered_data['House Number'] == house_number]
        # elif block_range:

        if house_number is not None:
            low, high = block_range
            filtered_data = filtered_data[
                (filtered_data['House Number'] >= str(low)) & (filtered_data['House Number'] <= str(high))
            ]

        print(f"Filtered {len(filtered_data)} violations for street '{street_name}' and house {house_number} with code {violation_code}.")

        #i want to print 200 rows of the hosue number column
        print(filtered_data['House Number'].head(200))
        return filtered_data


        
        #likely not needed here
    
    # #wil needt to look into this
    # def get_street_cleaning_violation_stats(self, street_name):
    #     '''Get aggregate stats for violations on a street'''
    #     try:
    #         results = self.client.get(
    #             DATASET_IDS['parking_violations_2024'],
    #             select="COUNT(*) as ticket_count",
    #             where=f"violation_code='21' AND street_name='{street_name.upper()}'",
    #             limit=1
    #         )
            
    #         if results:
    #             return int(results[0]['ticket_count'])
    #         return 0
    #     except Exception as e:
    #         print(f"Error fetching violation stats: {e}")
    #         return 0


