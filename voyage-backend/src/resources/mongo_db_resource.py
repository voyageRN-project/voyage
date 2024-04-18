from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv

load_dotenv()
mongo_secret = os.getenv("MONGO_PASSWORD")
uri = (f"mongodb+srv://netawerner:{mongo_secret}@voyagecluster.j9rcyj3.mongodb.net/?retryWrites=true&w=majority"
       f"&appName=VoyageCluster")
connection_string = "mongodb+srv://netawerner:<password>@voyagecluster.j9rcyj3.mongodb.net/"


class MongoDBResource:
    def __init__(self):
        # Create a new client and connect to the server
        self.client = MongoClient(uri)



