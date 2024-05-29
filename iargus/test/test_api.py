"""
Tests for the API.
Note that the MLflow server needs to be running for these tests to work.
"""

from datetime import date

import pandas as pd
from fastapi.testclient import TestClient

from api import app

client = TestClient(app)

def test_predict():
    """
    Test for /predict
    """

    # Without a valid token
    testing_data = pd.read_csv("./test/testing_data.csv")
    testing_json = testing_data.iloc[0].to_dict()
    response = client.post("/predict", json=testing_json)
    assert response.status_code == 422

    # With a valid token
    test_user_details = {
        "first_name": "test_" + date.today().strftime("%Y-%m-%d"),
        "surname": "test_" + date.today().strftime("%Y-%m-%d"),
        "email": "test@mail.com"
    }
    token_response = client.post("/get_token", json=test_user_details)
    token = response.json()["token"]
    testing_json["security_token"] = token

    response = client.post("/predict", json=testing_json)
    assert response.status_code == 200
    assert "predicted_price" in response.json()
    assert isinstance(response.json()["predicted_price"], float)

    # Envoyer des données de test et vérifier que le résultat est un float

def test_get_token():
    """
    Test for /get_token
    """
    user_data = {
        "first_name": "test",
        "surname": "test",
        "email": "not an email address"
    }
    response = client.post("/get_token", json=user_data)

    assert response.status_code == 200
    # Making sure that no token was given back as the email address wasn't
    # valid
    assert "token" not in response.json()


    
