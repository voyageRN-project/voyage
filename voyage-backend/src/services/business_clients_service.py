
from typing import Any
from resources.mongo_db_resource import MongoDBResource
from processors.response_builder import ResponseBuilder
from helpers.constants import NEW_BUSINESS_EXPECTED_REQUEST_HEADERS, NEW_BUSINESS_OPTIONAL_REQUEST_HEADERS
from helpers.error_handling import MissingHeaderError

import logging as logger

from traitlets import Long

logger.basicConfig(level=logger.INFO)


# service consts:


class BusinessService:
    def __init__(self, request_headers: dict[str, str]):
        self.request_headers = request_headers
        self.response_builder = ResponseBuilder()
        self.db_resource = MongoDBResource()

    def verify_request_headers(self) -> None:
        """the function go over the expected headers,
        and verify the existence of each one of them in the request headers.
        if one of the headers is missing, the function will raise an error
        (that should trigger an 400 response code
        (for bad request (=missing headers))"""

        for header in NEW_BUSINESS_EXPECTED_REQUEST_HEADERS:
            if header not in self.request_headers:
                logger.error(f"BusinessService: missing header in request: {header}")
                raise MissingHeaderError(f"Missing Header in Request: {header}", 400)

    def add_new_business_to_db(self) -> Any:
        """the function adds the new business to the DB
        and returns the new business ID"""

        # build the new business dictionary
        business_data = {
            "business_name": self.request_headers["business_name"],
            "business_type": self.request_headers["business_type"],
            "business_phone": self.request_headers["business_phone"],
            "business_email": self.request_headers["business_email"],
            "business_match_interest_points": self.request_headers["business_match_interest_points"],
            "business_country": self.request_headers["business_country"],
            "business_opening_hours": self.request_headers["business_opening_hours"],
            "appearance_counter": 0

        }
        if "business_description" in self.request_headers:
            business_data["business_description"] = self.request_headers["business_description"]

        # add the new business to the DB
        return self.db_resource.add_new_business(business_data)

    def add_new_client_to_db(self, business_id: Any) -> Any:
        """the function adds a new client to the business clients DB
        and returns the new client ID"""
        client_data = {
            "business_id": business_id,
            "business_contact_person": self.request_headers["business_contact_person"],
            "business_contact_person_phone": self.request_headers["business_contact_person_phone"],
            "credits_bought": self.request_headers["credits_bought"],
            "credits_spent": 0
        }
        return self.db_resource.add_new_business_client(client_data)

    def add_new_business(self) -> 'ResponseBuilder':
        logger.info(f"BusinessService: add new business method called with headers: {self.request_headers}\n")
        # first - validate that all the expected headers exist in the request
        try:
            self.verify_request_headers()
        except MissingHeaderError as e:
            raise e

        # add the new business to the DB
        new_business_id = self.add_new_business_to_db()
        logger.info(f"BusinessService: new business added to the DB with ID: {new_business_id}\n")

        # add a new client to the business clients DB
        self.add_new_client_to_db(new_business_id)
        return self.response_builder.build_response(self.db_resource.get_business_from_db(new_business_id), 200)
