from pydantic import BaseModel
from src.models.content import Content
from src.models.accommodation_recommendation import AccommodationRecommendation
from src.models.restaurant_recommendation import RestaurantRecommendation


class DayItinerary(BaseModel):
    day: int
    morning_activity: list[Content]
    afternoon_activity: list[Content]
    evening_activity: list[Content]
    restaurants_recommendations: list[RestaurantRecommendation]
    accommodation_recommendations: list[AccommodationRecommendation]
