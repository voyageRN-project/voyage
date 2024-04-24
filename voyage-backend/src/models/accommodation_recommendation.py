from pydantic import BaseModel


class AccommodationRecommendation(BaseModel):
    accommodation_name: str
    accommodation_type: str
