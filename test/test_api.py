"""
Tests for the API.
Note that the MLflow server needs to be running for these tests to work.
"""

import pandas as pd
from fastapi.testclient import TestClient

from api import app

client = TestClient(app)

def test_predict():
    """
    Test for /predict
    """
    testing_data = pd.read_csv("./test/testing_data.csv")
    testing_json = testing_data.iloc[0].to_dict()
    response = client.post("/predict", json=testing_json)
    assert response.status_code == 200
    assert "predicted_price" in response.json()
    assert isinstance(response.json()["predicted_price"], float)

    # Envoyer des données de test et vérifier que le résultat est un float

def test_index():
    """
    Test for the index (/)
    """
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


    
