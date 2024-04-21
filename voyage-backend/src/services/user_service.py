import json
from enum import Enum
from pycountry_convert import country_alpha2_to_country_name
from src.processors.data_validator import DataValidator
from src.processors.prompt_builder import PromptBuilder
from src.processors.response_builder import ResponseBuilder
from src.helpers.error_handling import (MissingHeaderError, CouldNotGetValidResponseFromThirdParty,
                                        CountryNameError, ConvertAIResponseToJsonError)
from src.helpers.constants import EXPECTED_REQUEST_HEADERS, OPTIONAL_REQUEST_HEADERS
from src.resources.generative_ai_resource import GenerativeAIResource
from src.resources.mongo_db_resource import MongoDBResource

import logging as logger
logger.basicConfig(level=logger.INFO)

# service consts:
INVALID_JSON_STR = "The content of the previous response is not a Valid JSON. Trying again."


class ErrorType(Enum):
    INVALID_JSON = 1
    INVALID_RESPONSE = 2


class UserService:
    def __init__(self, request_headers: dict[str, str]):
        self.request_headers = request_headers
        self.data_validator = DataValidator()
        self.response_builder = ResponseBuilder()
        self.prompt_builder = PromptBuilder()
        self.db_resource = MongoDBResource()

    def verify_request_headers(self) -> None:
        """the function go over the expected headers,
        and verify the existence of each one of them in the request headers.
        if one of the headers is missing, the function will raise an error
        (that should trigger an 400 response code
        (for bad request (=missing headers))"""

        for header in EXPECTED_REQUEST_HEADERS:
            if header not in self.request_headers:
                logger.error(f"UserService: missing header in request: {header}")
                raise MissingHeaderError(f"Missing Header in Request: {header}", 400)

    def get_required_headers_dict(self) -> dict[str, str]:
        """
        build the dict of the required headers,
        used after verification, known that all required headers exist.
        :return: the required headers dict
        """

        required_headers = {}
        for header in EXPECTED_REQUEST_HEADERS:
            required_headers[header] = self.request_headers.get(header, None)

        return required_headers

    def get_optional_headers_dict(self) -> dict[str, str]:
        """
        build the dict of the optional headers,
        takes only the existed headers from the request headers.
        :return: the optional headers dict
        """
        optional_headers = {}
        for header in OPTIONAL_REQUEST_HEADERS:
            if header in self.request_headers:
                optional_headers[header] = self.request_headers.get(header, None)

        return optional_headers

    def get_recommendations_from_db(self, required_headers: dict[str, str], optional_headers: dict[str, str]):
        """
        get the recommendations from the business DB according to the user search.
        return: the match lines recommendations from the business DB
        """

        try:
            c_name = country_alpha2_to_country_name(required_headers.get('country-code'), cn_name_format="default")
        except Exception as e:
            raise CountryNameError(f"Could not get country name from country code: "
                                   f"{required_headers.get('country-code')}", 400)
        user_properties = {"business_country": c_name, "interest-points": required_headers.get("interest-points")}
        if optional_headers.get('city'):
            user_properties["city"] = optional_headers.get('city')
        if optional_headers.get('area'):
            user_properties["area"] = optional_headers.get('area')
        if optional_headers.get('accommodation_type'):
            user_properties["accommodation_type"] = optional_headers.get('accommodation_type')
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
                                                          error_type: ErrorType) -> dict[str, any]:
        """
        this function is called when the first response from the generative AI is not valid.
        it attaches the errors to the prompt and tries to get another response from the generative AI.
        :param error_type:
        :param errors_identification:
        :return: the new raw itinerary
        """

        # attach the errors to the prompt
        prompt_with_errors_identification = (self.prompt_builder
                                             .with_error_identification(errors_identification)
                                             .build())
        # get the response from the generative AI
        raw_itinerary = GenerativeAIResource.get(prompt_with_errors_identification)
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
                                                                              ErrorType.INVALID_JSON)
        # validate the response from the generative AI
        try:
            if not self.data_validator.verify_valid_raw_itinerary(json_itinerary):
                logger.error(f"UsersService: second raw itinerary is not valid: {raw_itinerary},"
                             f" found errors:\n{self.data_validator.errors}\n")
                # if it's the second time of invalid data response, return 500 error
                if error_type == ErrorType.INVALID_RESPONSE:
                    logger.error(f"second time of invali data failure, return 500")
                    raise CouldNotGetValidResponseFromThirdParty("Could not get a valid response from the generative AI",
                                                                 500)
                # if it's the first time of invalid data response, try again with invalid response error
                else:
                    logger.info(f"trying to perform another request\n")
                    return self.perform_second_request_with_errors_identification(
                        self.data_validator.errors, ErrorType.INVALID_JSON)
        except CouldNotGetValidResponseFromThirdParty as e:
            raise e
        return json_itinerary

    def build_trip(self) -> 'ResponseBuilder':
        logger.info(f"UsersService: build_trip method called with headers: {self.request_headers}\n")
        # first - validate that all the expected headers exist in the request
        try:
            self.verify_request_headers()
        except MissingHeaderError as e:
            raise e
        # build a dict of the relevant headers for the prompt
        required_headers = self.get_required_headers_dict()
        optional_headers = self.get_optional_headers_dict()
        # get optional lines recommendations from the business DB
        recommendations = self.get_recommendations_from_db(required_headers, optional_headers)
        # build the prompt
        ready_prompt = (self.prompt_builder
                        .with_required_headers(required_headers)
                        .with_optional_headers(optional_headers)
                        .with_optional_business_recommendations(recommendations)
                        .build())
        logger.info(f"UsersService: prompt built: {ready_prompt}\n")
        # get the response from the generative AI
        generative_ai_resource = GenerativeAIResource(ready_prompt)
        raw_itinerary = generative_ai_resource.get_generative_ai_response()
        try:
            json_itinerary = self.convert_ai_response_to_json(raw_itinerary)
        except ConvertAIResponseToJsonError:
            logger.info(f"UsersService: first raw itinerary is not valid: {raw_itinerary},"
                        f" couldn't convert to valid JSON,\n trying to perform another request\n")
            try:
                json_itinerary = self.perform_second_request_with_errors_identification(
                    [INVALID_JSON_STR], ErrorType.INVALID_JSON)
            except CouldNotGetValidResponseFromThirdParty as e:
                raise e
        logger.info(f"UsersService: got raw itinerary from generative AI: {json_itinerary}\n")
        # validate the response from the generative AI
        try:
            if not self.data_validator.verify_valid_raw_itinerary(json_itinerary):
                logger.info(f"UsersService: first raw itinerary is not valid: {raw_itinerary},"
                            f" found errors:\n{self.data_validator.errors}\n, trying to perform another request\n")
                try:
                    json_itinerary = self.perform_second_request_with_errors_identification(
                        self.data_validator.errors, ErrorType.INVALID_RESPONSE)
                except CouldNotGetValidResponseFromThirdParty as e:
                    raise e
        except CouldNotGetValidResponseFromThirdParty as e:
            raise e
        # if the data is valid - build the response and return it
        return self.response_builder.build_response(json_itinerary, 200)
