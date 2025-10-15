import os
from sodapy import Socrata
import pandas as pd
from config import SOCRATA_DOMAIN, SOCRATA_APP_TOKEN, DATASET_IDS

class DataFetcher: 

    def __init__(self):
        self.client = Socrata(SOCRATA_DOMAIN, SOCRATA_APP_TOKEN)
        self.current_block_low = None # track current block range
        self.current_block_high = None
        self.current_block_middle = None
        self.current_side = None
        '''
        Find street segment (physical_id) for a given address
        
        Args:
            street_name: Street name (e.g., "BLEECKER ST")
            house_number: House number (e.g., 123)
            borough_code: Optional borough code (1-5)
        
        Returns:
            List of matching records with physical_id
        '''
    def get_street_centerline_by_address(self, full_street_name, house_number, borough_code=None):
        full_street_name = full_street_name.upper().strip()
        house_number = int(house_number or 0)

    # Build Socrata WHERE clause
        where_clause = f"""
        (full_street_name = '{full_street_name}')
     AND (
        (l_low_hn::number <= {house_number} AND l_high_hn::number >= {house_number})
        OR
        (r_low_hn::number <= {house_number} AND r_high_hn::number >= {house_number})
    )
    """

        if borough_code:
            where_clause += f" AND boroughcode = '{borough_code}'"

        try:
            results = self.client.get(
            "inkn-q76z",  # dataset ID for Street Centerline
            where=where_clause,
            select="physicalid, full_street_name, l_low_hn, l_high_hn, r_low_hn, r_high_hn, boroughcode",
            limit=5
        )
        
            if results:
                first_result = results[0]
                house_number = int(house_number)

            # Determine side of street
                left_side = (int(first_result['l_low_hn']) <= house_number <= int(first_result['l_high_hn']))

                if left_side:
                    self.current_block_low = int(first_result['l_low_hn'])
                    self.current_block_high = int(first_result['l_high_hn'])
                    self.current_side = 'L'
                else:
                    self.current_block_low = int(first_result['r_low_hn'])
                    self.current_block_high = int(first_result['r_high_hn'])
                    self.current_side = 'R'

                self.current_block_middle = (self.current_block_low + self.current_block_high) // 2

            return results
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

    def get_parking_violations_by_street(self, street_name, house_number, violation_code="21", limit=100):
        # street_name = street_name.upper().strip()
        # safe_street = street_name.replace("'", "''")
        # house_number = str(house_number).strip()
        # violation_code = str(violation_code).strip()

        # where = (
        #     f"violation_code = {violation_code} "
        #     f"AND street_name = '{safe_street}' "
        #     f"AND house_number = '{house_number}'"
        # )

        where_clause = (
            f"violation_code = '{violation_code}' "
            f"AND street_name = '{street_name}' "
        )
          
       # where_clause = "violation_code LIKE '%%%s%%' AND street_name LIKE '%%%s%%' AND house_number LIKE '%%%s%%'" % (violation_code, street_name, house_number)
          
        try:
            results = self.client.get(
                DATASET_IDS['parking_violations_2024'],
                where=where_clause,
                select="summons_number, issue_date, violation_time, street_name",
                # select="summons_number, issue_date, violation_time, street_name",
                limit=limit
            )
            print(f"Fetched {len(results)} violations for {house_number} {street_name}")
            return pd.DataFrame.from_records(results)
        except Exception as e:
            print(f"Error fetching parking violations: {e}")
            return pd.DataFrame()

    
    #wil needt to look into this
    def get_street_cleaning_violation_stats(self, street_name):
        '''Get aggregate stats for violations on a street'''
        try:
            results = self.client.get(
                DATASET_IDS['parking_violations_2024'],
                select="COUNT(*) as ticket_count",
                where=f"violation_code='21' AND street_name='{street_name.upper()}'",
                limit=1
            )
            
            if results:
                return int(results[0]['ticket_count'])
            return 0
        except Exception as e:
            print(f"Error fetching violation stats: {e}")
            return 0

    #Not used right now!
    # def get_parking_regulations(self, street_name, from_street=None):
    #     '''
    #     Get alternate side parking regulations for a street
        
    #     Args:
    #         street_name: Street name (e.g., "DEKALB AVENUE")
    #         from_street: Optional cross street to filter location
            
    #     Returns:
    #         List of parking regulation signs and their details
    #     '''
    #     street_name = street_name.upper().strip()
    #     where_clause = f"on_street = '{street_name}' AND sign_description LIKE '%ALTERNATE%'"
        
    #     if from_street:
    #         from_street = from_street.upper().strip()
    #         where_clause += f" AND from_street = '{from_street}'"
            
    #     try:
    #         results = self.client.get(
    #             DATASET_IDS['street_signs'],
    #             where=where_clause,
    #             select="order_number,sign_description,on_street,from_street,borough,side_of_street,order_completed_on_date,sign_location",
    #             order="order_completed_on_date DESC",
    #             limit=10
    #         )
            
    #         if not results:
    #             return []
                
    #         # Process and format the regulations
    #         regulations = []
    #         for sign in results:
    #             regulation = {
    #                 'description': sign.get('sign_description', ''),
    #                 'location': {
    #                     'street': sign.get('on_street', ''),
    #                     'cross_street': sign.get('from_street', ''),
    #                     'borough': sign.get('borough', ''),
    #                     'side': sign.get('side_of_street', ''),
    #                     'specific_location': sign.get('sign_location', '')
    #                 },
    #                 'order_number': sign.get('order_number', ''),
    #                 'updated': sign.get('order_completed_on_date', '')
    #             }
    #             regulations.append(regulation)
                
    #         return regulations
            
    #     except Exception as e:
    #         print(f"Error fetching parking regulations: {e}")
    #         return []
    

    #     # results = self.client.get(DATASET_IDS['street_centerline'], where=where_clause, limit=1)
    #     # if results:
    #     #     return pd.DataFrame.from_records(results)
    #     # return pd.DataFrame()