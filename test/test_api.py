"""
Tests for the API.
Note that the MLflow server needs to be running for these tests to work.
"""


from fastapi.testclient import TestClient

from api import app

client = TestClient(app)

def test_predict():
    """
    Test for /predict
    """
    response = client.post("/predict")
    # Envoyer des données de test et vérifier que le résultat est un float

def test_index():
    """
    Test for the index (/)
    """
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


    
