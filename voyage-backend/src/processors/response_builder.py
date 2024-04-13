class ResponseBuilder:
    @staticmethod
    def build_response(data, status_code):
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