from models.generated_trip import GeneratedTrip


class ResponseBuilder:
    @staticmethod
    def build_response(data: GeneratedTrip, status_code: int) -> dict[str, any]:
        return {
            'data': data,
            'status_code': status_code
        }

    @staticmethod
    def build_error_response(error_string, error_status_code):
        return {
            'error': error_string,
            'status_code': error_status_code
        }