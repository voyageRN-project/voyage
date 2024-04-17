import traceback

from flask import Flask, request, Response
from waitress import serve
from services.user_service import UserService
from helpers.error_handling import MissingHeaderError, CouldNotGetValidResponseFromThirdParty
import logging as logger

logger.basicConfig(level=logger.INFO)

users_app = Flask(__name__)


@users_app.route("/build_trip", methods=['GET'])
def build_trip():
    headers = dict(request.headers)
    logger.info(f"user_app perform get request for building a new trip with the requested headers: {str(headers)}")
    service = UserService(headers)
    try:
        return service.build_trip()
    except MissingHeaderError as e:
        return Response(e.error_string, e.error_status_code)
    except CouldNotGetValidResponseFromThirdParty as e:
        return Response(e.error_string, e.error_status_code)
    except Exception as e:
        logger.error(f"got unexpected error:\n{str(e)}\n{str(traceback.format_exc())}\n")
        return Response("unknown error", 500)


def run():
    serve(users_app, host="0.0.0.0", port=8081)
