import sys
sys.path.append("/voyage-backend")

from resources.mongo_db_resource import MongoDBResource
import logging as logger



def test_mongo_connection():
    mongo_db_resource = MongoDBResource()
    assert mongo_db_resource.client is not None

    # Send a ping to confirm a successful connection
    try:
        mongo_db_resource.client.admin.command('ping')
        logger.info("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
