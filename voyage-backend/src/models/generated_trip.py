from pydantic import BaseModel
from src.models.day_itinerary import DayItinerary


class GeneratedTrip(BaseModel):
    trip_itinerary: list[DayItinerary]

