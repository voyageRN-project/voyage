from typing import Any

from pydantic.v1 import BaseModel


class BusinessData(BaseModel):
    business_client_id: Any
    business_name: str
    business_type: str
    business_phone: str
    business_email: str
    business_match_interest_points: list[str]
    business_country: str
    business_description: str = None
    appearance_counter: int = 0
    business_longitude: str
    business_latitude: str
