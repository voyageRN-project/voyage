from flask import Flask, request, Response
from waitress import serve
import logging as logger

logger.basicConfig(level=logger.INFO)

users_app = Flask(__name__)


@users_app.route("/build_trip", methods=['GET'])
def build_trip():
    headers = dict(request.headers)
    logger.info(f"user_app perform get request for building a new trip with the requested headers: {str(headers)}")


    return "Trip Built Successfully"


def run():
    serve(users_app, host="0.0.0.0", port=8081)
