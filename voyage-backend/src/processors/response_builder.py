class ResponseBuilder:
    @staticmethod
    def build_response(data, status_code):
        return {
            'data': data,
            'status_code': status_code
        }