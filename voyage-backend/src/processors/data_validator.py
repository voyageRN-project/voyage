from enum import Enum
from typing import Union, Any
from ..helpers.error_handling import ThirdPartyDataValidatorError
from ..helpers.error_handling import CountryNameError
from geopy.geocoders import Nominatim
import requests
import json
import geopy
import logging as logger

from pycountry_convert import country_name_to_country_alpha2

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


class errorsType(Enum):
    INVALID_FORMAT = "invalid format"
    MISSING_REQUIRED_KEY = "missing required key"
    INVALID_LOCATION = "invalid location"


class DataValidator:
    def __init__(self):
        self.errors = {}
        self.geo_locator = Nominatim(user_agent="voyage_project")

    def verify_long_lat_in_country(self, longitude: str, latitude: str, c_name: str) -> bool:
        c_code = self.get_country_code(c_name)
        location = geopy.point.Point(float(latitude), float(longitude))
        res = self.geo_locator.reverse(location)
        if c_code.lower() not in res.raw['address']['country_code'].lower():
            return False
        return True

    def verify_valid_raw_itinerary(self, json_raw_itinerary: Any,
                                   requested_country_name: str,
                                   requested_city_name: str = None) -> bool:
        # first - validate the expected json header
        if not self.validate_required_data_in_structure('trip_itinerary', json_raw_itinerary.keys(),
                                                        validationErrors.TRIP_ITINERARY_MISSING.value):
            return False

        # verify that the trip itinerary is a list
        if type(json_raw_itinerary['trip_itinerary']) is not list:
            self.errors[validationErrors.TRIP_ITINERARY_NOT_LIST.value] = errorsType.INVALID_FORMAT.value
            return False

        # perform the next validation for each day in the list of trip_itinerary
        is_valid_data = True
        for day_itinerary in json_raw_itinerary['trip_itinerary']:
            # validate that all the expected keys are in the day itinerary - required to perform the next validation
            if not self.validate_require_keys_in_day_itinerary(day_itinerary):
                return False
            try:
                # validate the data in the day itinerary
                if not self.validate_data_in_day_itinerary(day_itinerary, requested_country_name, requested_city_name):
                    is_valid_data = False
            except ThirdPartyDataValidatorError as e:
                raise e

        return is_valid_data

    def validate_required_data_in_structure(self,
                                            data: str,
                                            structure_need_to_be_include_in: Any,
                                            error_message: str) -> bool:
        """the function will validate that the data is included in the structure
        :param error_message: the error message to be added to the errors list in case of failure
        :param structure_need_to_be_include_in: the structure that should include the data (can be lst, dict.keys(), dict.values())
        :param data: the data to be validated - need to be checked that included in the structure
        :return: True if the data is included in the structure, False otherwise"""

        if data not in structure_need_to_be_include_in:
            self.errors[error_message] = errorsType.MISSING_REQUIRED_KEY.value
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

    def validate_data_in_day_itinerary(self, day_itinerary: dict[str, any], requested_country_name: str,
                                       requested_city_name: str = None) -> bool:
        """The function will validate the data in the day itinerary.
        :param day_itinerary: The day itinerary to be validated.
        :param requested_country_name: The country name to be validated.
        :param requested_city_name: The city name to be validated.
        :return: True if the data in the day itinerary is valid, False otherwise."""

        part_keys = ['morning_activity', 'afternoon_activity', 'evening_activity', 'restaurants_recommendations',
                     'accommodation_recommendations']
        flag_res_validation = True
        # for each of the expected parts in the day itinerary, validate the content
        for part in part_keys:
            # get the match contents list for the match part if exists.
            content_lst = day_itinerary.get(part, None)
            if content_lst is not None:
                for content in content_lst:
                    try:
                        if not self.validate_content_data_by_name(content, requested_country_name):
                            # if it failed, validation through lang-lat will be performed,
                            if not self.validate_content_data_by_long_lat(content, requested_country_name):
                                # if the validation failed, add an error to the error list
                                self.errors[(f"found invalid location: {content} may not is not in the requested "
                                             f"location")] = errorsType.INVALID_LOCATION.value
                                flag_res_validation = False
                    except ThirdPartyDataValidatorError as e:
                        raise e
        return flag_res_validation

    def validate_content_data_by_name(self, content: dict[Any, Any], requested_country_name: str) -> bool:
        # if the content does not include the name key, add an error to the error list
        if ('content_name' not in content.keys() and 'restaurant_name' not in content.keys() and
                'accommodation_name' not in content.keys()):
            self.errors[(f"invalid json format: missing name for the content "
                         f"(could be content, restaurant or accommodation)")] = errorsType.MISSING_REQUIRED_KEY.value
            return False
        try:
            # get the match key - name
            key = 'content_name' if 'content_name' in content.keys() \
                else 'restaurant_name' if 'restaurant_name' in content.keys() \
                else 'accommodation_name'
            # validate the location of the content, using the third party location validator by the name of the content
            return self.validate_content_location(content[key], requested_country_name)
        except ThirdPartyDataValidatorError as e:
            raise e

    def validate_content_data_by_long_lat(self, content: dict[Any, Any], requested_country_name: str) -> bool:
        # first need to verify that the lang-lat exists
        if (('content_latitude' not in content.keys() or 'content_longitude' not in content.keys())
                and ('restaurant_latitude' not in content.keys() or 'restaurant_longitude' not in content.keys())
                and (
                        'accommodation_latitude' not in content.keys() or 'accommodation_longitude' not in content.keys())):
            self.errors[(f"invalid json format: missing name for the content "
                         f"(could be content, restaurant or accommodation)")] = errorsType.MISSING_REQUIRED_KEY.value
            return False
        key_lat = 'content_latitude' if 'content_latitude' in content.keys() \
            else 'restaurant_latitude' if 'restaurant_latitude' in content.keys() \
            else 'accommodation_latitude'
        key_long = 'content_longitude' if 'content_longitude' in content.keys() \
            else 'restaurant_longitude' if 'restaurant_longitude' in content.keys() \
            else 'accommodation_longitude'
        if not self.verify_long_lat_in_country(content[key_long], content[key_lat],
                                               requested_country_name):
            return False
        return True

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

    def verify_all_fields_contain_data(self, json_raw_itinerary: Any, requested_days: int) -> bool:
        """The function will verify that all the fields in the json raw itinerary contain data.
        :param json_raw_itinerary: The json raw itinerary to be validated.
        :return: True if all the fields in the json raw itinerary contain data, False otherwise."""

        if len(json_raw_itinerary['trip_itinerary']) != requested_days:
            self.errors[f"invalid json format: got incorrect number of itinerary days."] = errorsType.INVALID_FORMAT.value
            return False
        for day_itinerary in json_raw_itinerary['trip_itinerary']:
            if not self.verify_all_fields_contain_data_in_day_itinerary(day_itinerary):
                return False

        return True

    def verify_all_fields_contain_data_in_day_itinerary(self, day_itinerary: dict[str, any]) -> bool:
        """The function will verify that all the fields in the day itinerary contain data.
        :param day_itinerary: The day itinerary to be validated.
        :return: True if all the fields in the day itinerary contain data, False otherwise."""

        for part in day_itinerary.keys():
            if type(day_itinerary[part]) is not int:
                if len(day_itinerary[part]) == 0:
                    self.errors[
                        f"invalid json format: missing data in the content: {part}"] = errorsType.INVALID_FORMAT.value
                    return False

        return True

    @staticmethod
    def get_country_code(country_name: str):
        try:  # try to get the country code from the country name
            country_code = country_name_to_country_alpha2(country_name)
        except Exception as e:
            raise CountryNameError(f"Could not get country name from country code: "
                                   f"{country_name}", 400)
        return country_code
