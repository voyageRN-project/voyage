from pycountry_convert import country_alpha2_to_country_name
from ..helpers.error_handling import CountryNameError
from ..models.day_itinerary import DayItinerary
from ..models.content import Content
from ..models.generated_trip import GeneratedTrip
from ..models.accommodation_recommendation import AccommodationRecommendation
from ..models.restaurant_recommendation import RestaurantRecommendation


class PromptBuilder:
    def __init__(self):
        self.required_keys = {}
        self.optional_keys = {}
        self.optional_business_recommendations = {}
        self.error_identification = []

    def with_required_keys(self, headers: dict[str, str]) -> 'PromptBuilder':
        self.required_keys = headers
        return self

    def with_optional_keys(self, headers: dict[str, str]) -> 'PromptBuilder':
        self.optional_keys = headers
        return self

    def with_optional_business_recommendations(self, lines_from_table) -> 'PromptBuilder':
        self.optional_business_recommendations = lines_from_table
        return self

    def with_error_identification(self, found_errors: list[str]) -> 'PromptBuilder':
        self.error_identification = found_errors
        return self

    def get_country_code(self) -> str:
        try:
            c_name = country_alpha2_to_country_name(self.required_keys.get('country-code'), cn_name_format="default")
        except Exception as e:
            raise CountryNameError(f"Could not get country name from country code: "
                                   f"{self.required_keys.get('country-code')}", 400)
        return c_name

    def get_business_activities(self) -> str:
        str_recommendations = ("to the result trip itinerary, please add at least one of the following activities ("
                               "=content):\n")
        str_recommendations += self.optional_business_recommendations
        return str_recommendations

    @staticmethod
    def get_json_model() -> str:
        """This function is used to get the json model of the GeneratedTrip class
        to be used in the prompt generation."""

        content_template = Content(content_name="<content name>",
                                   content_type="<content type>",
                                   content_description="<content_description>",
                                   content_latitude="<content_latitude>",
                                   content_longitude="<content_longitude>")
        restaurant_template = RestaurantRecommendation(restaurant_name="<restaurant_name>",
                                                       restaurant_type="<restaurant_type>",
                                                       restaurant_latitude="<restaurant_latitude>",
                                                       restaurant_longitude="<restaurant_longitude>")
        accommodation_template = AccommodationRecommendation(accommodation_name="<accommodation_name>",
                                                             accommodation_type="<accommodation_type>",
                                                             accommodation_latitude="<accommodation_latitude>",
                                                             accommodation_longitude="<accommodation_longitude>")
        fist_day_itinerary = DayItinerary(day=1,
                                          morning_activity=[content_template],
                                          afternoon_activity=[content_template],
                                          evening_activity=[content_template],
                                          restaurants_recommendations=[restaurant_template],
                                          accommodation_recommendations=[accommodation_template])
        second_day_itinerary = DayItinerary(day=2,
                                            morning_activity=[content_template],
                                            afternoon_activity=[content_template],
                                            evening_activity=[content_template],
                                            restaurants_recommendations=[restaurant_template],
                                            accommodation_recommendations=[accommodation_template])
        trip_itinerary_template = GeneratedTrip(trip_itinerary=[fist_day_itinerary, second_day_itinerary])

        return trip_itinerary_template.model_dump_json()

    def build(self) -> str:
        # get the country name from the country code
        c_name = self.get_country_code()
        # build the basic prompt
        base_prompt = (
            f"You are a great trip planner. I need you to generate a trip itinerary according to the following"
            f" properties.\n"
            f"the vacation duration should be: {self.required_keys.get('duration')}\n"
            f"the vacation destination should be: {c_name}\n"
            f"the vacation season should be: {self.required_keys.get('season')}\n"
            f"the vacation budget should be: {self.required_keys.get('budget')}\n"
            f"the vacation participants are be: {self.required_keys.get('participants')}\n"
            f"the main interest points are: {self.required_keys.get('interest-points')}\n")
        # append the optional headers if they exist
        if self.optional_keys:
            if self.optional_keys.get('accommodation_type'):
                base_prompt += f"the accommodation type should be: {self.optional_keys.get('accommodation_type')}\n"
            if self.optional_keys.get('transportation_type'):
                base_prompt += f"the transportation type should be: {self.optional_keys.get('transportation_type')}\n"
            if self.optional_keys.get('area'):
                base_prompt += f"the area should be: {self.optional_keys.get('area')}\n"
            if self.optional_keys.get('city'):
                base_prompt += f"the city should be: {self.optional_keys.get('city')}\n"
        # append match business activities if they exist and match the interest points and the location
        if len(self.optional_business_recommendations) > 0:
            base_prompt += "the trip itinerary should include the following activities:\n"
            business_num = 1
            for business in self.optional_business_recommendations:
                base_prompt += (f"{business_num})    Business name: {business.get('business_name')}, "
                                f"Business type: {business.get('business_type')}, "
                                f"business country: {business.get('business_country')}")
                if business.get('business_description'):
                    base_prompt += f", Business description: {business.get('business_description')}\n"
                else:
                    base_prompt += "\n"
                business_num += 1
        # append the error identification if it exists
        if self.error_identification:
            base_prompt += f"the following errors were found: {self.error_identification}\n"
        # append the json model of the GeneratedTrip class
        response_jason_template = self.get_json_model()
        optimized_prompt = base_prompt + (f'Please provide a response in a structured JSON format that matches the '
                                          f'following model: {response_jason_template}\n')
        optimized_prompt += (f'Please pay attention to include only the specific site name in the '
                             f'"content_name", field. (e.g. "content_name": "Cinque Terre" instead of '
                             f'"a day trip to Cinque Terre" that should be a part of the '
                             f'"content_description" field).\n'
                             f'very important - each content must have longitudes and latitudes to '
                             f'validate the correctness of the data and all the requested fields must '
                             f'be completed.\n')
        return optimized_prompt
