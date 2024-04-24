from pydantic import BaseModel
from models.content import Content
from models.accommodation_recommendation import AccommodationRecommendation
from models.restaurant_recommendation import RestaurantRecommendation


class DayItinerary(BaseModel):
    day: int
    morning_activity: list[Content]
    afternoon_activity: list[Content]
    evening_activity: list[Content]
    restaurants_recommendations: list[RestaurantRecommendation]
    accommodation_recommendations: list[AccommodationRecommendation]
