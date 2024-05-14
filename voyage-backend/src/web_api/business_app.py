# import traceback
# from flask import Flask, request, Response
# from waitress import serve
# from flask_cors import CORS
# from services.business_clients_service import BusinessService
# from helpers.error_handling import MissingExpectedKeyInRequestBodyError
# import logging as logger
# logger.basicConfig(level=logger.INFO)
#
# business_app = Flask(__name__)
# CORS(business_app)
#
#
# @business_app.route("/add_business", methods=['POST'])
# def add_business():
#     request_body = dict(request.form)
#     logger.info(f"business_app perform post request for assign new business to the DB's with the requested headers: {str(request_body)}")
#     service = BusinessService(request_body)
#     try:
#         return service.add_new_business()
#     except MissingExpectedKeyInRequestBodyError as e:
#         return Response(e.error_string, 400)
#     except Exception as e:
#         logger.error(f"got unexpected error:\n{str(e)}\n{str(traceback.format_exc())}\n")
#         return Response("unknown error", 500)
#
#
# def run():
#     serve(business_app, host="0.0.0.0", port=8080)
