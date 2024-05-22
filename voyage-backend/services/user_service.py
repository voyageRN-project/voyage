import json
from enum import Enum
from typing import Any

from processors.data_validator import DataValidator
from processors.prompt_builder import PromptBuilder
from processors.response_builder import ResponseBuilder
from helpers.error_handling import (MissingExpectedKeyInRequestBodyError, CouldNotGetValidResponseFromThirdParty,
                                    CountryNameError, ConvertAIResponseToJsonError)
from helpers.constants import NEW_TRIP_EXPECTED_REQUEST_PROPERTIES, NEW_TRIP_OPTIONAL_REQUEST_PROPERTIES
from resources.generative_ai_resource import GenerativeAIResource
from resources.mongo_db_resource import MongoDBResource
from models.day_itinerary import DayItinerary
from models.generated_trip import GeneratedTrip
from pycountry_convert import country_alpha2_to_country_name


import logging as logger

logger.basicConfig(level=logger.INFO)

# service consts:
INVALID_JSON_STR = "The content of the previous response is not a Valid JSON. Trying again."


class ErrorType(Enum):
    INVALID_JSON = 1
    INVALID_RESPONSE = 2


class UserService:
    def __init__(self, request_body: dict[str, str]):
        self.request_body = request_body
        self.data_validator = DataValidator()
        self.response_builder = ResponseBuilder()
        self.prompt_builder = PromptBuilder()
        self.db_resource = MongoDBResource()
        self.required_request_keys = {}
        self.optional_request_keys = {}

    def verify_request_keys(self) -> None:
        """the function go over the expected headers,
        and verify the existence of each one of them in the request headers.
        if one of the headers is missing, the function will raise an error
        (that should trigger an 400 response code
        (for bad request (=missing headers))"""

        for expected_key in NEW_TRIP_EXPECTED_REQUEST_PROPERTIES:
            if expected_key not in self.request_body.keys():
                logger.error(f"UserService: missing expected key in request: {expected_key}")
                raise MissingExpectedKeyInRequestBodyError(f"Missing Header in Request: {expected_key}", 400)

    def get_required_properties_dict(self) -> dict[str, str]:
        """
        build the dict of the required headers,
        used after verification, known that all required headers exist.
        :return: the required headers dict
        """

        required_properties = {}
        for property_key in NEW_TRIP_EXPECTED_REQUEST_PROPERTIES:
            if property_key == "interest-points":
                required_properties[property_key] = self.request_body.get(property_key).split(",")
            else:
                required_properties[property_key] = self.request_body.get(property_key, None)

        return required_properties

    def get_optional_keys_dict(self) -> dict[str, str]:
        """
        build the dict of the optional headers,
        takes only the existed headers from the request headers.
        :return: the optional headers dict
        """
        optional_headers = {}
        for header in NEW_TRIP_OPTIONAL_REQUEST_PROPERTIES:
            if header in self.request_body:
                optional_headers[header] = self.request_body.get(header, None)

        return optional_headers

    def get_recommendations_from_db(self):
        """
        get the recommendations from the business DB according to the user search.
        return: the match lines recommendations from the business DB
        """

        try:  # try to get the country name from the country code
            c_name = country_alpha2_to_country_name(self.required_request_keys.get('country-code'),
                                                    cn_name_format="default")
        except Exception as e:
            raise CountryNameError(f"Could not get country name from country code: "
                                   f"{self.required_request_keys.get('country-code')}", 400)
        user_properties = {'country': c_name,
                           'interest-points': self.required_request_keys.get("interest-points")}
        if self.optional_request_keys.get('city'):
            user_properties['city'] = self.optional_request_keys.get('city')
        if self.optional_request_keys.get('area'):
            user_properties['area'] = self.optional_request_keys.get('area')
        if self.optional_request_keys.get('accommodation_type'):
            user_properties['accommodation_type'] = self.optional_request_keys.get('accommodation_type')
        lines = self.db_resource.get_match_business_to_user_search(user_properties)

        return lines

    @staticmethod
    def convert_ai_response_to_json(response) -> dict[str, any]:
        """ the function gets the raw response from the generative AI,
        and converts it to a JSON format.
        if the conversion fails, the function will raise an error.
        """

        response_text = response.text
        try:
            response_in_json = json.loads(response_text)
        except json.JSONDecodeError:
            raise ConvertAIResponseToJsonError(f"Could not convert AI response to JSON: {response_text}", 500)
        return response_in_json

    def perform_second_request_with_errors_identification(self, errors_identification: list[str],
                                                          error_type: ErrorType, c_name: str) -> dict[str, any]:
        """
        this function is called when the first response from the generative AI is not valid.
        it attaches the errors to the prompt and tries to get another response from the generative AI.
        :param c_name:
        :param error_type:
        :param errors_identification:
        :return: the new raw itinerary
        """

        # attach the errors to the prompt
        prompt_with_errors_identification = (self.prompt_builder
                                             .with_error_identification(errors_identification)
                                             .build())
        # get the response from the generative AI
        generative_ai_resource = GenerativeAIResource(prompt_with_errors_identification)
        raw_itinerary = generative_ai_resource.get_generative_ai_response()
        # try to convert to valid Json
        try:
            json_itinerary = self.convert_ai_response_to_json(raw_itinerary)
        # if conversion fails:
        except ConvertAIResponseToJsonError:
            logger.error(f"UsersService: second raw itinerary is not valid: {raw_itinerary},"
                         f" couldn't convert to valid JSON,\n")
            # if it's the second time that convertible's failed due to invalid JSON, return 500 error
            if error_type == ErrorType.INVALID_JSON:
                logger.error(f"second time of Json converting failure, return 500")
                raise CouldNotGetValidResponseFromThirdParty("Could not get a valid response from the generative AI",
                                                             500)
            # if it's the first time that convertible's failed due to invalid JSON, try again with invalid json error
            else:
                logger.info(f"trying to perform another request\n")
                return self.perform_second_request_with_errors_identification([INVALID_JSON_STR],
                                                                              ErrorType.INVALID_JSON, c_name)
        # validate the response from the generative AI
        try:
            if not self.data_validator.verify_valid_raw_itinerary(json_itinerary,
                                                                  self.required_request_keys.get('country-code')):
                logger.error(f"UsersService: second raw itinerary is not valid: {raw_itinerary},"
                             f" found errors:\n{self.data_validator.errors}\n")
                # if it's the second time of invalid data response, return 500 error
                if error_type == ErrorType.INVALID_RESPONSE:
                    logger.error(f"second time of invali data failure, return 500")
                    raise CouldNotGetValidResponseFromThirdParty(
                        "Could not get a valid response from the generative AI",
                        500)
                # if it's the first time of invalid data response, try again with invalid response error
                else:
                    logger.info(f"trying to perform another request\n")
                    return self.perform_second_request_with_errors_identification(
                        self.data_validator.errors, ErrorType.INVALID_JSON)
        except CouldNotGetValidResponseFromThirdParty as e:
            raise e
        return json_itinerary

    def get_published_business_ids_from_itinerary(self, trip_itinerary: GeneratedTrip, recommendations) -> list[str]:
        """ the function gets the itinerary that has been built and the recommendations that has been proposed to
        build it, and returns the IDs of the business that has been published in the itinerary
        """
        published_business_ids = []
        flag_line_found = False
        for line in recommendations:
            for day_itinerary in trip_itinerary.trip_itinerary:
                if self.check_if_business_exists_in_day_recommendations(line.get("business_name"), day_itinerary):
                    published_business_ids.append(line.get("_id"))
                    flag_line_found = True
                    break
                if flag_line_found:
                    break
        return published_business_ids

    def check_if_business_exists_in_day_recommendations(self, business_name, day_recommendations) -> bool:
        """
        the function checks if the business name exists in the day recommendations
        :param business_name: the name of the business
        :param day_recommendations: the recommendations of the day
        :return: True if the business name exists in the day recommendations, False otherwise
        """
        for content in day_recommendations.morning_activity:
            if content.content_name.lower() == business_name.lower():
                return True
        for content in day_recommendations.afternoon_activity:
            if content.content_name.lower() == business_name.lower():
                return True
        for content in day_recommendations.evening_activity:
            if content.content_name.lower() == business_name.lower():
                return True
        for restaurant in day_recommendations.restaurants_recommendations:
            if restaurant.restaurant_name.lower() == business_name.lower():
                return True
        for accommodation in day_recommendations.accommodation_recommendations:
            if accommodation.accommodation_name.lower() == business_name.lower():
                return True
        return False

    def update_db_regarding_itinerary(self, trip_itinerary: GeneratedTrip, json_itinerary: json, recommendations: Any) -> Any:
        """the function manages the update process i the different collection after a trip has been built.
            - the itinerary with hos properties will be saved to the generated-trips collection
            - the sites that have been published in the itinerary will be updated in the business DB
            - the sites that have been published in the itinerary will be updated in the clients DB
        :arg json_itinerary: the itinerary that has been built as the original json
        :arg trip_itinerary: the itinerary that has been built
        :arg recommendations: the recommendations that has been proposed to build the prompt
        {
            "destination": string, (concat the country, area and city if exist)
            "duration": String,
            "body": Json, (the AI response json model)
            "business_id": list[String] (the IDs of the business that has been published in the trip)
        }
        """
        # first - find the business that has been published in the itinerary
        published_business_ids = self.get_published_business_ids_from_itinerary(trip_itinerary, recommendations)
        try:  # try to get the country name from the country code
            c_name = country_alpha2_to_country_name(self.required_request_keys.get('country-code'),
                                                    cn_name_format="default")
        except Exception as e:
            raise CountryNameError(f"Could not get country name from country code: "
                                   f"{self.required_request_keys.get('country-code')}", 400)
        # save the itinerary to the generated-trips collection
        itinerary_data_dict = {"destination": c_name,
                               "duration": self.required_request_keys.get('duration'),
                               "body": trip_itinerary,
                               "business_id": published_business_ids
                               }
        trip_id = self.db_resource.add_new_generated_trip(json_itinerary)
        # update the business and clients DBs:
        for business_id in published_business_ids:
            self.db_resource.updates_credits_and_appearance_counter(business_id)
        return trip_id

    @staticmethod
    def build_trip_itinerary_response(response_json) -> 'GeneratedTrip':
        trip_days = []
        for day in response_json.get('trip_itinerary'):
            day_itinerary = DayItinerary(day=day.get('day'),
                                         morning_activity=day.get('morning_activity'),
                                         afternoon_activity=day.get('afternoon_activity'),
                                         evening_activity=day.get('evening_activity'),
                                         restaurants_recommendations=day.get('restaurants_recommendations'),
                                         accommodation_recommendations=day.get('accommodation_recommendations'))
            trip_days.append(day_itinerary)
        return GeneratedTrip(trip_itinerary=trip_days)

    def get_a_valid_itinerary(self, recommendations, c_name):
        """
        the function gets the raw itinerary from the generative AI,
        the function will perform the required validations:
        - verify Json format
        - verify that all expected fields exist in the response and contain data
        - verify that all the data is valid
        """
        attempt_counter = 0
        while attempt_counter < 7:
            # build the prompt
            ready_prompt = (self.prompt_builder
                            .with_required_keys(self.required_request_keys)
                            .with_optional_keys(self.optional_request_keys)
                            .with_optional_business_recommendations(recommendations))
            if len(self.data_validator.errors) > 0:
                ready_prompt = (self.prompt_builder
                                .with_error_identification(self.data_validator.errors))
            ready_prompt = ready_prompt.build()
            # generate response from the generative AI
            generative_ai_resource = GenerativeAIResource(ready_prompt)
            raw_itinerary = generative_ai_resource.get_generative_ai_response()
            logger.info(f"UsersService: got raw itinerary from generative AI: {raw_itinerary.text}\n")
            try:  # try to convert to valid Json
                json_itinerary = self.convert_ai_response_to_json(raw_itinerary)
            except ConvertAIResponseToJsonError:
                logger.info(f"UsersService: first raw itinerary is not valid: {raw_itinerary},"
                            f" couldn't convert to valid JSON,\n trying to perform another request\n")
                self.data_validator.errors[INVALID_JSON_STR] = ("The content of the previous response is not a Valid "
                                                                "JSON.")
                continue
            logger.info(f"UsersService: got raw itinerary from generative AI: {json_itinerary}\n")
            # exact the number of requested days from the request body
            num_days = int(list(filter(lambda x: x.isdigit(), self.required_request_keys.get('duration').split()))[0])
            if not self.data_validator.verify_all_fields_contain_data(json_itinerary, num_days) or \
                    not self.data_validator.verify_valid_raw_itinerary(json_itinerary, c_name):
                logger.info(f"UsersService: first raw itinerary is not valid: {raw_itinerary},"
                            f" found errors:\n{self.data_validator.errors}\n, trying to perform another request\n")
            else:
                return json_itinerary
            self.data_validator.errors = {}
            attempt_counter += 1
        raise CouldNotGetValidResponseFromThirdParty("Could not get a valid response from the generative AI", 500)

    def build_trip(self) -> 'ResponseBuilder':
        logger.info(f"UsersService: build_trip method called with headers: {self.request_body}\n")
        # first - validate that all the expected headers exist in the request
        try:
            self.verify_request_keys()
        except MissingExpectedKeyInRequestBodyError as e:
            raise e
        # build a dict of the relevant headers for the prompt
        self.required_request_keys = self.get_required_properties_dict()
        self.optional_request_keys = self.get_optional_keys_dict()
        try:  # try to get the country name from the country code
            c_name = country_alpha2_to_country_name(self.required_request_keys.get('country-code'),
                                                    cn_name_format="default")
        except CouldNotGetValidResponseFromThirdParty as e:
            raise e
        # get optional lines recommendations from the business DB
        recommendations = self.get_recommendations_from_db()
        try:
            json_itinerary = self.get_a_valid_itinerary(recommendations, c_name)
        except CouldNotGetValidResponseFromThirdParty as e:
            raise e
        # if the data is valid - first, trigger the required updates in the DBs,
        trip_itinerary = self.build_trip_itinerary_response(json_itinerary)
        self.update_db_regarding_itinerary(trip_itinerary, json_itinerary, recommendations)
        # and secondly - build the response and return it
        return self.response_builder.build_business_response(json_itinerary['trip_itinerary'], 200, "trip_itinerary")
