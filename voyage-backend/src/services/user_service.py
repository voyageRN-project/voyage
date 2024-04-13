from ...src.processors.data_validator import DataValidator
from ...src.processors.prompt_builder import PromptBuilder
from ...src.processors.response_builder import ResponseBuilder

import logging as logger
logger.basicConfig(level=logger.INFO)


class UserService:
    def __init__(self, request_headers):
        self.request_headers = request_headers
        self.data_validator = DataValidator()
        self.response_builder = ResponseBuilder()
        self.prompt_builder = PromptBuilder()


    def build_trip(self):
        logger.info(f"UsersService: build_trip method called with headers: {self.request_headers}")
        raw_itinerary = self.prompt_builder.build()
        if not self.data_validator.verify_valid_raw_itinerary(raw_itinerary):
            return None
        else:
            return self.response_builder.build_response(raw_itinerary)

