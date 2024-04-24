import google.generativeai as genai
import os
from dotenv import load_dotenv

# define google model properties: API key through the environment variable and the required model
load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=google_api_key)
model = genai.GenerativeModel('gemini-pro')


class GenerativeAIResource:

    def __init__(self, message):
        self.message = message
        self._finish_reason = None
        self._total_tokens = None

    def get_generative_ai_response(self):
        res = model.generate_content(self.message)
        return res

