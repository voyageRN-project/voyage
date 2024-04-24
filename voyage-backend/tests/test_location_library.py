import json
import requests


def test_validation_api_request():
    input = "The Eiffel Tower"
    data = requests.get(
        f"https://restaurant-api.wolt.com/v1/google/places/autocomplete/json?input={input}", verify=False)
    assert data.status_code == 200
    json_res = json.loads(data.text)
    location_optional_prediction = json_res['predictions']
    flag_location_found = False
    for prediction in location_optional_prediction:
        if 'Paris' in prediction['description']:
            flag_location_found = True
            break
    assert flag_location_found

