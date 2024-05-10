from pydantic import BaseModel


class AccommodationRecommendation(BaseModel):
    accommodation_name: str
    accommodation_type: str
    accommodation_latitude: str
    accommodation_longitude: str
