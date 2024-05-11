from typing import Any
from models.generated_trip import GeneratedTrip


class ResponseBuilder:
    @staticmethod
    def build_business_response(data: Any, status_code: int, data_title: str = 'data') -> dict[str, any]:
        return {
            data_title: data,
            'status_code': status_code
        }

    @staticmethod
    def build_error_response(error_string, error_status_code):
        return {
            'error': error_string,
            'status_code': error_status_code
        }