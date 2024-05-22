from services.user_service import UserService
from services.business_clients_service import BusinessService
import traceback
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from helpers.error_handling import MissingExpectedKeyInRequestBodyError, CouldNotGetValidResponseFromThirdParty, ConvertAIResponseToJsonError
import logging as logger

logger.basicConfig(level=logger.INFO)


app = Flask(__name__)
CORS(app)


@app.route("/api/v1/business_app/add_business", methods=['POST'])
def add_business():
    request_body = dict(request.form)
    logger.info(
        f"business_app perform post request for assign new business to the DB's with the requested headers: {str(request_body)}")
    service = BusinessService(request_body)
    try:
        return service.add_new_business()
    except MissingExpectedKeyInRequestBodyError as e:
        return Response(e.error_string, 400)
    except Exception as e:
        logger.error(f"got unexpected error:\n{str(e)}\n{str(traceback.format_exc())}\n")
        return Response(f"unknown error: {e}", 500)


@app.route('/api/v1/users_app/build_trip', methods=['POST'])
def users_handler():
    request_body = dict(request.form)
    logger.info(f"user_app perform get request for building a new trip with the requested headers: {str(request_body)}")
    service = UserService(request_body)
    try:
        return service.build_trip()
    except MissingExpectedKeyInRequestBodyError as e:
        return Response(e.error_string, e.error_status_code)
    except CouldNotGetValidResponseFromThirdParty as e:
        return Response(e.error_string, e.error_status_code)
    except ConvertAIResponseToJsonError as e:
        return Response(e.error_string, e.error_status_code)
    except Exception as e:
        logger.error(f"got unexpected error:\n{str(e)}\n{str(traceback.format_exc())}\n")
        return Response("unknown error", 500)


@app.route('/api/v1/management/health')
def get_health():
    logger.debug("management perform get request for health check")
    return jsonify({"status": "ok"})



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True, use_reloader=False, threaded=True)
