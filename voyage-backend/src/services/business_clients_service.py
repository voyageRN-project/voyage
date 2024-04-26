from typing import Any
from resources.mongo_db_resource import MongoDBResource
from processors.response_builder import ResponseBuilder
from helpers.constants import NEW_BUSINESS_EXPECTED_REQUEST_PROPERTIES, NEW_BUSINESS_OPTIONAL_REQUEST_PROPERTIES
from helpers.error_handling import MissingExpectedKeyInRequestBodyError

import logging as logger

logger.basicConfig(level=logger.INFO)


# service consts:


class BusinessService:
    def __init__(self, request_body: dict[str, str]):
        self.request_body = request_body
        self.response_builder = ResponseBuilder()
        self.db_resource = MongoDBResource()

    def verify_request_headers(self) -> None:
        """the function go over the expected headers,
        and verify the existence of each one of them in the request headers.
        if one of the headers is missing, the function will raise an error
        (that should trigger an 400 response code
        (for bad request (=missing headers))"""

        for header in NEW_BUSINESS_EXPECTED_REQUEST_PROPERTIES:
            if header not in self.request_body:
                logger.error(f"BusinessService: missing header in request: {header}")
                raise MissingExpectedKeyInRequestBodyError(f"Missing Header in Request: {header}", 400)

    def add_new_business_to_db(self, new_client_id: Any) -> Any:
        """the function adds the new business to the DB
        and returns the new business ID"""

        # build the new business dictionary
        # todo: need to update the db and verify - the business should point to the client and not the opposite.
        business_data = {
            "business_client_id": new_client_id,
            "business_name": self.request_body["business_name"],
            "business_type": self.request_body["business_type"],
            "business_phone": self.request_body["business_phone"],
            "business_email": self.request_body["business_email"],
            "business_match_interest_points": self.request_body["business_match_interest_points"].split(","),
            "business_country": self.request_body["business_country"],
            "appearance_counter": 0

        }
        if "business_description" in self.request_body:
            business_data["business_description"] = self.request_body["business_description"]

        # add the new business to the DB
        return self.db_resource.add_new_business(business_data)

    def add_new_client_to_db(self) -> Any:
        """the function adds a new client to the business clients DB
        and returns the new client ID"""
        client_data = {
            "business_contact_person": self.request_body["business_contact_person"],
            "business_contact_person_phone": self.request_body["business_contact_person_phone"],
            "credits_bought": int(self.request_body["credits_bought"]),
            "credits_spent": 0
        }
        return self.db_resource.add_new_business_client(client_data)

    def add_new_business(self) -> 'ResponseBuilder':
        logger.info(f"BusinessService: add new business method called with headers: {self.request_body}\n")
        # first - validate that all the expected headers exist in the request
        try:
            self.verify_request_headers()
        except MissingExpectedKeyInRequestBodyError as e:
            raise e

        # add a new client to the business clients DB
        new_client_id = self.add_new_client_to_db()

        # add the new business to the DB
        new_business_id = self.add_new_business_to_db(new_client_id)
        logger.info(f"BusinessService: new business added to the DB with ID: {new_business_id}\n")



        return self.response_builder.build_business_response(self.db_resource.get_business_from_db(
            new_business_id), 200, 'new-business')
