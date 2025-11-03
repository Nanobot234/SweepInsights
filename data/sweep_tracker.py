from datetime import datetime
from .data_fetcher import DataFetcher
from .address_mapper import AddressMapper


class SweepTracker:

    '''Main class for tracking street sweeping data'''

    def __init__(self):
        self.data_fetcher = DataFetcher(data_path="/Users/nanabonsu/Downloads/StreetCleaningViolations.csv")
        self.address_mapper = AddressMapper()


#multiple records
    def get_sweep_statuses(self, street_name, house_number, borough_code=None, num_records=1):
        '''
        Returns the last `num_records` sweep statuses for a given address.

        Args:
            street_name: Street name (e.g., "Bleecker St")
            house_number: House number
            borough_code: Optional borough code (1-5)
            num_records: Number of recent sweep records to return (default 1)

        Returns:
            If num_records == 1: Dictionary with sweep status information for the most recent sweep
            If num_records > 1: List of dictionaries with sweep status information for each of the last `num_records` sweeps
        '''
        # Try cache first
        physical_id = self.address_mapper.get_cached_physical_id(
            street_name, house_number, borough_code
        )

        print(f"Physical ID from cache: {physical_id}")


        # If not in cache, fetch from API
        if not physical_id:
            results = self.data_fetcher.get_street_centerline_by_address(
                street_name, house_number, borough_code
            )
            print(f"Street centerline results: {results}")

            if not results:
                error_result = {
                    "status": "error",
                    "message": "Address not found in NYC Street Centerline database"
                }
                return error_result if num_records == 1 else [error_result]

            physical_id = results[0]['physicalid']

            # Cache the result
            self.address_mapper.cache_physical_id(
                street_name, house_number, physical_id, borough_code
            )

        # Get sweep data
        sweep_data_list = self.data_fetcher.get_sweep_data(physical_id, limit=num_records)

        
        print(f"Sweep data list length: {len(sweep_data_list)}")

        if not sweep_data_list:
            no_data_result = {

                
                "status": "no_data",
                "address": f"{house_number} {street_name}",
                "physical_id": physical_id,
                "message": "No sweep data available for this street segment"
            }
            return no_data_result if num_records == 1 else [no_data_result]

        # Get up to the last `num_records` sweep dates with times
        
        #only need the times they visited!
        last_sweeps = [
            {

                #change 
              #  "status": "success",
               # "address": f"{house_number} {street_name}",
                #"physical_id": physical_id,
                "last_swept": entry.get("date_visited"), 
                #"message": f"Street was swept on {entry.get('date_visited')}"
            }
            for entry in sweep_data_list[:num_records]
        ]

        if num_records == 1:
            # Return a single dictionary for the most recent sweep
            entry = last_sweeps[0]
            print(f"Most recent sweep entry: {entry}")
            # Ensure all relevant fields are included
            return {
                "status": entry.get("status"),
                "address": entry.get("address"),
                "physical_id": entry.get("physical_id"),
                "last_swept": entry.get("last_swept"), #dte visited is in the data, last swept is just a key
                # "time_visited": entry.get("time_visited"), not importatn  I think here!~
                "message": f"Street was last swept on {entry.get('date_visited')}"
            }
        else:
            return last_sweeps
    
    
    def get_street_risk_score(self, street_name):
        '''
        Get risk score based on historical ticket data
        
        Returns:
            Dictionary with ticket count and risk level
        '''
        ticket_count = self.data_fetcher.get_violation_stats(street_name)
        
        # Simple risk scoring
        if ticket_count > 200:
            risk_level = "HIGH"
        elif ticket_count > 100:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return {
            "street_name": street_name,
            "ticket_count": ticket_count,
            "risk_level": risk_level
        }
    
    def get_recent_violations(self, street_name, limit=10):
        '''Get recent parking violations for a street'''
        violations_df = self.data_fetcher.get_parking_violations_by_street(
            street_name, limit=limit
        )
        
        if violations_df.empty:
            return []
        
        return violations_df.to_dict('records')


