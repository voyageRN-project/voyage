from pydantic import BaseModel


class RestaurantRecommendation(BaseModel):
    restaurant_name: str
    restaurant_type: str
    restaurant_latitude: str
    restaurant_longitude: str
