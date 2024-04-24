from pydantic import BaseModel
from models.day_itinerary import DayItinerary


class GeneratedTrip(BaseModel):
    trip_itinerary: list[DayItinerary]

