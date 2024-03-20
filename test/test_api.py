"""
Unit tests to make sure the API works properly.
"""

import requests

def test_predict_endpoint():
    """
    Tests the API /predict endpoint by making sure it returns a float given the
    right features.
    """

    # Penser à remplacer le endpoint pour mettre le bon
    url = "http://127.0.0.1:8000/predict"
    features = {
        "State": "AL",
        "Make": "Acura",
        "Model": "TSX5-Speed",
        "Year": 2015,
        "Mileage": 35000
    }
    response = requests.post(url, json=features)
    assert isinstance(response.content["price"], float)

def test_security():
    """
    Makes sure no one can use the endpoint without a valid token.
    """
    raise NotImplemented

