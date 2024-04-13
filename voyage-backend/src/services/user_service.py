from ...src.processors.data_validator import DataValidator
from ...src.processors.prompt_builder import PromptBuilder
from ...src.processors.response_builder import ResponseBuilder
from ...src.helpers.error_handling import MissingHeaderError, CouldNotGetValidResponseFromThirdParty
from ...src.helpers.constants import EXPECTED_REQUEST_HEADERS, OPTIONAL_REQUEST_HEADERS
from ...src.resources.generative_ai_resource import GenerativeAIResource

import logging as logger

logger.basicConfig(level=logger.INFO)


class UserService:
    def __init__(self, request_headers: dict[str, str]):
        self.request_headers = request_headers
        self.data_validator = DataValidator()
        self.response_builder = ResponseBuilder()
        self.prompt_builder = PromptBuilder()

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
        used after verification, known that all required headers are exist.
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
        # build the prompt
        ready_prompt = (self.prompt_builder
                        .with_required_headers(required_headers)
                        .with_optional_headers(optional_headers)
                        .build())
        logger.info(f"UsersService: prompt built: {ready_prompt}\n")
        # get the response from the generative AI
        raw_itinerary = GenerativeAIResource.get(ready_prompt)
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
