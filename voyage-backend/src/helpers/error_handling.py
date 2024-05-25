import json
import logging as logger

logger.basicConfig(level=logger.INFO)


class MissingExpectedKeyInRequestBodyError(Exception):
    def __init__(self, error_string, error_status_code):
        self.error_string = error_string
        self.error_status_code = error_status_code


class CountryNameError(Exception):
    def __init__(self, error_string, error_status_code):
        self.error_string = error_string
        self.error_status_code = error_status_code


class MongoConnectionError(Exception):
    def __init__(self, error_string, error_status_code):
        self.error_string = error_string
        self.error_status_code = error_status_code


class ThirdPartyDataValidatorError(Exception):
    def __init__(self, error_string, error_status_code):
        self.error_string = error_string
        self.error_status_code = error_status_code


class ConvertAIResponseToJsonError(Exception):
    def __init__(self, error_string, error_status_code):
        self.error_string = error_string
        self.error_status_code = error_status_code


class CouldNotGetValidResponseFromThirdParty(Exception):
    def __init__(self, error_string, error_status_code):
        self.error_string = error_string
        self.error_status_code = error_status_code


def error(error_string, error_status_code):
    error_json = json.dumps({"status": "error", "reason": "%s" % error_string}, indent=4)
    logger.info(f'Returned Error {error_status_code} With Content:\n{error_json}')
    return error_json, error_status_code
