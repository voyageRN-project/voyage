import google.generativeai as genai
genai.configure(api_key="AIzaSyAQP4QC0fJJB6tOmjZ-FV4YPSTR11rbJdQ")
model = genai.GenerativeModel('gemini-pro')


class GenerativeAIResource:

    def __init__(self, message):
        self.message = message
        self._finish_reason = None
        self._total_tokens = None

    def get_generative_ai_response(self):
        res = model.generate_content(self.message)
        return res

