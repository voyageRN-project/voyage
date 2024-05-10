from typing import Any


class BusinessData:
    def __init__(self,
                 business_client_id: Any,
                 business_name: str,
                 business_type: str,
                 business_phone: str,
                 business_email: str,
                 business_match_interest_points: list[str],
                 business_country: str,
                 business_description: str,
                 business_longitude: str,
                 business_latitude: str):
        self.business_client_id = business_client_id
        self.business_name = business_name
        self.business_type = business_type
        self.business_phone = business_phone
        self.business_email = business_email
        self.business_match_interest_points = business_match_interest_points
        self.business_country = business_country
        self.appearance_counter = 0
        if business_description:
            self.business_description = business_description
        self.business_longitude = business_longitude
        self.business_latitude = business_latitude
