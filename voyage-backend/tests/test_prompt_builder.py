import sys
sys.path.append("/voyage-backend")

from processors.prompt_builder import PromptBuilder
import json


def test_json_template():
    json_str = PromptBuilder.get_json_model()
    try:
        template_json = json.loads(json_str)
    except json.JSONDecodeError:
        template_json = None
    assert template_json is not None
    assert template_json["trip_itinerary"][0]["day"] == 1


def test_final_prompt():
    required_headers = {"country-code": "IT",
                        "budget": "Moderate",
                        "season": "summer",
                        "participants": "2",
                        "duration": "7 days",
                        "interest-points": "wineries, day trips"}
    optional_headers = {"area": "Aosta vally"}
    prompt_builder = ((PromptBuilder()
                       .with_required_keys(required_headers))
                      .with_optional_keys(optional_headers))
    prompt = prompt_builder.build()
    assert "Italy" in prompt
    assert "7 days" in prompt
