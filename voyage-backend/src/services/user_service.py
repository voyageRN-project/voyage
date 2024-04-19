import json

from pycountry_convert import country_alpha2_to_country_name
from src.processors.data_validator import DataValidator
from src.processors.prompt_builder import PromptBuilder
from src.processors.response_builder import ResponseBuilder
from src.helpers.error_handling import MissingHeaderError, CouldNotGetValidResponseFromThirdParty, CountryNameError
from src.helpers.constants import EXPECTED_REQUEST_HEADERS, OPTIONAL_REQUEST_HEADERS
from src.resources.generative_ai_resource import GenerativeAIResource
from src.resources.mongo_db_resource import MongoDBResource

import logging as logger

logger.basicConfig(level=logger.INFO)


class UserService:
    def __init__(self, request_headers: dict[str, str]):
        self.request_headers = request_headers
        self.data_validator = DataValidator()
        self.response_builder = ResponseBuilder()
        self.prompt_builder = PromptBuilder()
        self.db_resource = MongoDBResource()

    def verify_request_headers(self):
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
        # EXPECTED_REQUEST_HEADERS = ['budget', 'season', 'participants', 'duration', 'country-code', 'interest-points']
        # OPTIONAL_REQUEST_HEADERS = ['accommodation_type', 'transportation_type', 'city', 'area']
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

def convert_ai_response_to_json(response):
    response_text = response.text
    try:
        response_in_json = json.loads(response_text)
    except json.JSONDecodeError:
        raise



    def build_trip(self):
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
        recommendations = self.get_recommendations_from_db(required_headers,optional_headers)
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
        json_itinerary =
        logger.info(f"UsersService: got raw itinerary from generative AI: {raw_itinerary}\n")
        # validate the response from the generative AI
        if not self.data_validator.verify_valid_raw_itinerary(raw_itinerary):
            logger.info(f"UsersService: first raw itinerary is not valid: {raw_itinerary},"
                        f" found errors:\n{self.data_validator.errors}\n, trying to perform another request\n")
            # if not valid, attach the errors to the prompt and try again
            prompt_with_errors_identification = (self.prompt_builder
                                                 .with_error_identification(self.data_validator.errors)
                                                 .build())
            raw_itinerary = GenerativeAIResource.get(prompt_with_errors_identification)
            if not self.data_validator.verify_valid_raw_itinerary(raw_itinerary):
                # if still not valid, raise an internal match error
                logger.error(f"UsersService: second raw itinerary is not valid: {raw_itinerary},"
                             f" found errors:\n{self.data_validator.errors}\n")
                raise CouldNotGetValidResponseFromThirdParty("Could not get a valid response from the generative AI",
                                                             500)
        # if the data is valid - build the response and return it
        return self.response_builder.build_response(raw_itinerary, 200)
