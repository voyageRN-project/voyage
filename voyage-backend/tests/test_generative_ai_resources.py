import pytest
import sys
sys.path.append("../src")

from resources.generative_ai_resource import GenerativeAIResource
from processors.prompt_builder import PromptBuilder
import json


def test_generative_ai(prompt):
    generative_ai = GenerativeAIResource(prompt)
    response = generative_ai.get_generative_ai_response()
    assert response is not None
    response_text = response.text
    assert response_text is not None
    try:
        response_in_json = json.loads(response_text)
    except json.JSONDecodeError:
        response_in_json = None
    assert response_in_json is not None



@pytest.fixture
def prompt():
    required_headers = {"country-code": "US",
                        "budget": "Moderate",
                        "season": "summer",
                        "participants": "2",
                        "duration": "3 days",
                        "interest-points": "wineries, day trips"}
    optional_headers = {"area": "west coast"}
    prompt_builder = ((PromptBuilder()
                       .with_required_headers(required_headers))
                      .with_optional_headers(optional_headers))
    prompt = prompt_builder.build()
    return prompt

