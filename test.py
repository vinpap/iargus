"""
Unit tests to make sure the API works properly.

TESTS À RÉALISER :
- test du endpoint /predict : on lui envoie des valeurs et on vérifie que la
valeur retournée est bien un float
- test de la fonction de monitoring pour vérifier qu'elle déclenche le réentraînmenet
uniquement quand les conditions sont vérifiées
- test de la fonction de réentraînement pour vérifier qu'elle a bien réentraîné
le modèle (on pourra aller le chercher sur MLflow par exemple)
- 
"""

import requests

def test_predict_endpoint():
    """
    Tests the API /predict endpoint by making sure it returns a float given the
    right features.
    """

    url = "http://127.0.0.1:8000/predict"
    features = {
        "State": "AL",
        "Make": "Acura",
        "Model": "TSX5-Speed",
        "Year": 2015,
        "Mileage": 35000
    }
    response = requests.post(url, json=features)
    # Checker le type de la valeur de retour ici

