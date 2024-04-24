from enum import Enum
from typing import Union, Any
from helpers.error_handling import ThirdPartyDataValidatorError
import requests
import json
import logging as logger

logger.basicConfig(level=logger.INFO)


class validationErrors(Enum):
    TRIP_ITINERARY_MISSING = "invalid json format: missing 'trip_itinerary' as main key in the json"
    TRIP_ITINERARY_NOT_LIST = "invalid json format: 'trip_itinerary' value, should be a list of days in the itinerary"
    MORNING_ACTIVITY_MISSING = ("invalid json format: missing 'morning_activity in the json, require key for each day "
                                "in the itinerary")
    AFTERNOON_ACTIVITY_MISSING = ("invalid json format: missing 'afternoon_activity' in the json, require key for "
                                  "each day in the itinerary")
    EVENING_ACTIVITY_MISSING = ("invalid json format: missing 'evening_activity' in the json, require key for each day "
                                "in the itinerary")
    RESTAURANT_RECOMMENDATIONS_MISSING = ("invalid json format: missing 'restaurants_recommendations' in the json, "
                                          "require key for each day in the itinerary")
    ACCOMMODATION_RECOMMENDATIONS_MISSING = ("invalid json format: missing 'accommodation_recommendations' in the json,"
                                             "require key for each day in the itinerary")


class DataValidator:
    def __init__(self):
        self.errors = []

    def verify_valid_raw_itinerary(self, json_raw_itinerary: Any,
                                   requested_country_name: str,
                                   requested_city_name: str = None) -> bool:
        if not self.validate_required_data_in_structure('trip_itinerary', json_raw_itinerary.keys(),
                                                        validationErrors.TRIP_ITINERARY_MISSING.value):
            return False
        if json_raw_itinerary['trip_itinerary'].type() != list:
            self.errors.append(validationErrors.TRIP_ITINERARY_NOT_LIST.value)
            return False
        is_valid_data = True
        # perform the next validation for each day in the list of trip_itinerary
        for day_itinerary in json_raw_itinerary['trip_itinerary']:
            if not self.validate_require_keys_in_day_itinerary(day_itinerary):
                return False
            try:
                if not self.validate_data_in_day_itinerary(day_itinerary, requested_country_name, requested_city_name):
                    is_valid_data = False
            except ThirdPartyDataValidatorError as e:
                raise e

        return is_valid_data

    def validate_required_data_in_structure(self,
                                            data:str,
                                            structure_need_to_be_include_in: Any,
                                            error_message: str) -> bool:
        """the function will validate that the data is included in the structure
        :param error_message: the error message to be added to the errors list in case of failure
        :param structure_need_to_be_include_in: the structure that should include the data (can be lst, dict.keys(), dict.values())
        :param data: the data to be validated - need to be checked that included in the structure
        :return: True if the data is included in the structure, False otherwise"""

        if data not in structure_need_to_be_include_in:
            self.errors.append(error_message)
            return False

        return True

    def validate_require_keys_in_day_itinerary(self, day_itinerary: dict[str, any]) -> bool:
        """the function will validate that the required keys are included in the day itinerary.
        :param day_itinerary: the day itinerary to be validated.
        :return: True if the required keys are included in the day itinerary, False otherwise."""

        if ((not self.validate_required_data_in_structure('morning_activity', day_itinerary.keys(),
                                                          validationErrors.MORNING_ACTIVITY_MISSING.value))
                or (not self.validate_required_data_in_structure('afternoon_activity', day_itinerary.keys(),
                                                                 validationErrors.AFTERNOON_ACTIVITY_MISSING.value))
                or (not self.validate_required_data_in_structure('afternoon_activity', day_itinerary.keys(),
                                                                 validationErrors.AFTERNOON_ACTIVITY_MISSING.value))
                or (not self.validate_required_data_in_structure('restaurants_recommendations', day_itinerary.keys(),
                                                                 validationErrors.RESTAURANT_RECOMMENDATIONS_MISSING.value))
                or (not self.validate_required_data_in_structure('accommodation_recommendations', day_itinerary.keys(),
                                                                 validationErrors.ACCOMMODATION_RECOMMENDATIONS_MISSING.value))):
            return False

        return True

    def validate_data_in_day_itinerary(self, day_itinerary:dict[str, any], requested_country_name: str,
                                       requested_city_name: str = None) -> bool:
        """The function will validate the data in the day itinerary.
        :param day_itinerary: The day itinerary to be validated.
        :param requested_country_name: The country name to be validated.
        :param requested_city_name: The city name to be validated.
        :return: True if the data in the day itinerary is valid, False otherwise."""

        part_keys = ['morning_activity', 'afternoon_activity', 'evening_activity', 'restaurants_recommendations',
                     'accommodation_recommendations']
        flag_res_validation = True
        for part in part_keys:
            for content in day_itinerary[part]:
                if 'content_name' not in content.keys():
                    self.errors.append(f"invalid json format: missing 'content_name' that should be included in each "
                                       f"part of the day itinerary")
                    return False
                try:
                    if not self.validate_content_location(content['content_name'], requested_country_name,
                                                          requested_city_name):
                        self.errors.append(
                            f"found invalid location: {content['content_name']} is not in the requested location")
                        flag_res_validation = False
                except ThirdPartyDataValidatorError as e:
                    raise e
        return flag_res_validation

    @staticmethod
    def validate_content_location(content_name, requested_country_name: str, requested_city_name: str = None) -> bool:
        """The function will validate the content location.
        :param content_name: The content name to be validated.
        :param requested_country_name: The country name to be validated.
        :param requested_city_name: The city name to be validated.
        :return: True if the content location is valid, False otherwise."""

        logger.info(f"Validating content location: {content_name}")
        # perform get request to get the location prediction
        data = requests.get(
            f"https://restaurant-api.wolt.com/v1/google/places/autocomplete/json?input={content_name}", verify=False)
        # check if the request status code is 200, if not raise an error
        if data.status_code != 200:
            logger.error(f"Could not get response from third party location validator, status code: {data.status_code}")
            raise ThirdPartyDataValidatorError("Could not get response from third party location validator", 500)
        try:
            json_res = json.loads(data.text)
        except json.JSONDecodeError:
            logger.error(f"Could not convert response to json")
            raise ThirdPartyDataValidatorError("Could not convert response to json", 500)
        # check if the location is found in the prediction
        location_optional_predictions = json_res['predictions']
        flag_location_found = False
        for prediction in location_optional_predictions:
            # if requested city name is not None, check if the city name and the country name are in the prediction
            if (requested_city_name and requested_city_name.lower() in prediction['description'].lower() and
                    requested_country_name.lower() in prediction['description'].lower()):
                flag_location_found = True
                break
            # else, check if the country name is in the prediction
            elif requested_country_name.lower() in prediction['description'].lower():
                flag_location_found = True
                break
        return flag_location_found
