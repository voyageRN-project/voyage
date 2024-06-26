from typing import Any

from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv
from ..helpers.error_handling import MongoConnectionError
import os
import logging as logger

from traitlets import Long

load_dotenv()
mongo_secret = os.getenv("MONGO_PASSWORD")
uri = (f"mongodb+srv://netawerner:{mongo_secret}@voyagecluster.j9rcyj3.mongodb.net/?retryWrites=true&w=majority"
       f"&appName=VoyageCluster")
connection_string = "mongodb+srv://netawerner:<password>@voyagecluster.j9rcyj3.mongodb.net/"


class MongoDBResource:
    def __init__(self):
        # Create a new client and connect to the server
        try:
            self.client = MongoClient(uri)
            self.client.admin.command('ping')
            logger.info("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            logger.error(f"Could not connect to MongoDB: {e}")
            raise MongoConnectionError(f"Could not connect to MongoDB", 500)
        self.business_db = self.client["business_db"]
        self.business_clients_collection = self.business_db["business-clients"]
        self.business_collection = self.business_db["businesses"]
        self.generated_trip_collection = self.business_db["generated-trips"]

    def get_client(self):
        return self.client

    def get_database(self, db_name: str):
        return self.business_db

    def get_business_from_db(self, business_id: int):
        business_object = self.business_collection.find_one({"_id": business_id})
        tmp_dict = business_object
        tmp_dict["_id"] = str(tmp_dict["_id"])
        tmp_dict["business_client_id"] = str(tmp_dict["business_client_id"])
        return tmp_dict

    def get_generated_trip_from_db(self, trip_id: int):
        trip_object = self.generated_trip_collection.find_one({"_id": trip_id})
        return trip_object["body"]

    def add_new_business_client(self, client_data: dict):
        """ input: a dictionary with the client data:
        {
            "business_contact_person": string,
            "business_contact_person_phone": string,
            "credits_bought": int,
            "credits_spent": int
        }
        """
        return self.business_clients_collection.insert_one(client_data).inserted_id

    def add_new_business(self, business_data: dict):
        """ input: a dictionary with the business data:
        {
            "business_name": String,
            "business_client_id": id
            "business_type": String,
            "business_phone": String,
            "business_email": String,
            "business_match_interest_points": List of Strings,
            "business_description": String,
            "business_country": String,
            "appearance_counter": integer,
        }
        """
        return self.business_collection.insert_one(business_data).inserted_id

    def add_new_generated_trip(self, trip_data: dict):
        """ input: a dictionary with the itinerary data:
        {
            "destination": string, (concat the country, area and city if exist)
            "duration": String,
            "body": Json, (the AI response json model)
            "business_id": list[String] (the IDs of the business that has been published in the trip)
        }
        """
        return self.generated_trip_collection.insert_one(trip_data).inserted_id

    def get_match_business_to_user_search(self, user_search: dict[str, Any]):

        """the function gets the properties that the user searched for as a dictionary,
        and return all the businesses that match the search from the business collection.
        the return value is the DB data - the relevant data for the prompt still need to be extracted.
        :arg user_search: a dictionary with the properties that the user searched for.
            format:
            {
                "country": String,
                "interest_points": List[Strings],

                optional fields:
                "city": String,
                "area": String,
                "accommodation_type": String
            }
        :return: a list of dictionaries with the match business data."""
        # get the lines that match to the requested country
        query = {"business_country": user_search.get("country")}
        relevant_country_lines = self.business_collection.find(query)
        relevant_lines = []

        # for each of the relevant lines, check if the interest points match
        for line in relevant_country_lines:
            for interest_point in user_search.get('interest-points'):
                if interest_point in line["business_match_interest_points"]:
                    relevant_lines.append(line)
                break

        returned_data = []
        for line in relevant_lines:
            # get the match client data
            match_client = self.business_clients_collection.find_one({"_id": line["business_client_id"]})
            # if the match client has more credit than he spent, add the business to the returned data
            if match_client["credits_bought"] - match_client["credits_spent"] > 0:
                returned_data.append(line)
        return returned_data

    def updates_credits_and_appearance_counter(self, business_id: int) -> None:
        """the function gets a business id to update,
        find the match line in the business table and update the "appearance_counter" field.
        then, it will get the match client data from the business clients table,
        and update the "credit_spent" field."""

        # update the appearance counter in the business table
        query = {"_id": business_id}
        business = self.business_collection.find_one(query)
        new_value = {"$set": {"appearance_counter": business["appearance_counter"] + 1}}
        self.business_collection.update_one(query, new_value)

        # update the credit spent in the business clients table
        query = {"_id": business["business_client_id"]}
        client = self.business_clients_collection.find_one(query)
        new_value = {"$set": {"credits_spent": client["credits_spent"] + 1}}
        self.business_clients_collection.update_one(query, new_value)
