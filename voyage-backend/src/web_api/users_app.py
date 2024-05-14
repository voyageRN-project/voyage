# import traceback
# from flask_cors import CORS
# from flask import Flask, request, Response
# from waitress import serve
# from services.user_service import UserService
# from helpers.error_handling import  MissingExpectedKeyInRequestBodyError, CouldNotGetValidResponseFromThirdParty, ConvertAIResponseToJsonError
# import logging as logger
#
# logger.basicConfig(level=logger.INFO)
#
# users_app = Flask(__name__)
# CORS(users_app)
#
#
# @users_app.route("/build_trip", methods=['POST'])
# def build_trip():
#     request_body = dict(request.form)
#     logger.info(f"user_app perform get request for building a new trip with the requested headers: {str(request_body)}")
#     service = UserService(request_body)
#     try:
#         return service.build_trip()
#     except MissingExpectedKeyInRequestBodyError as e:
#         return Response(e.error_string, e.error_status_code)
#     except CouldNotGetValidResponseFromThirdParty as e:
#         return Response(e.error_string, e.error_status_code)
#     except ConvertAIResponseToJsonError as e:
#         return Response(e.error_string, e.error_status_code)
#     except Exception as e:
#         logger.error(f"got unexpected error:\n{str(e)}\n{str(traceback.format_exc())}\n")
#         return Response("unknown error", 500)
#
#
# def run():
#     serve(users_app, host="0.0.0.0", port=8081)
