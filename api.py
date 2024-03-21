"""
Un seul endpoint : /predict, pour faire une prédiction à partir des infos données par l'utilisateur
Bien sécuriser l'API avec quelque chose de mieux qu'un token unique

Fonctionnement :
Le modèle est entraîné avec des données stockées dans une base de données et stocké à l'aide de MLflow. 
On check les performances du modèles à intervalles réguliers. Le seuil de performances acceptable
est défini à l'avance en MAPE (e.g. pas plus de 15% d'erreur sur le prix en moyenne, fixé par les dirigeants 
de l'Argus dans le scénario). Ce monitoring est réalisé à l'aide d'un script exécuté à intervalles
réguliers. Le réentraînement est automatisé si le seuil n'est pas respecté. Si le seuil n'est toujours
pas respecté après le réentraînement, on en alerte les gestionnaires de l'Argus par email.

"""

from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import mlflow
from mlflow import MlflowClient

from model_monitoring import preprocess_features

class CarDetails(BaseModel):
    """
    Data structure that stores information about an used car.
    """
    state: str
    make: str
    model: str
    year: int
    mileage: float

app = FastAPI()

@app.get("/")
async def root():
    """
    Returns a help message.
    """
    message = """Welcome to the IArgus prediction model API.\
        In order to use the model, send a request to the /predict endpoint
        with the following parameters in a JSON:
        - 'state': the two letters that reference the US state where the car was sold
        - 'make': the make of the car
        - 'model': the model of the car
        - 'year': the year the car was manufactured
        - 'mileage': the car mileage in kilometers."""

    return {"message": message}

@app.post("/predict")
async def predict(car_details: CarDetails):
    """
    Predicts the price of a second-hand car and returns the result.
    """

    # Loading the model from MLflow
    client = MlflowClient()
    model_versions = client.search_model_versions(f"name='iargus'")
    if len(model_versions) == 0:
        message = "No model has been trained yet for IArgus. Please try again later."
        return {"message": message}

    last_version = model_versions[0].version
    model_uri = f"models:/iargus/{last_version}"
    model = mlflow.keras.load_model(model_uri)

    # Preparing the data
    # Convertir en df et appeler preprocess_data
    # PENSER À AJOUTER UN CONTRÔLE DES VALEURS ICI
    car_data_dict = {
        "state": [car_details.state],
        "make": [car_details.make],
        "model": [car_details.model],
        "year": [car_details.year],
        "mileage": [car_details.mileage]
    }
    features = preprocess_features(pd.DataFrame(car_data_dict))
    pred = model.predict(features)
    print(pred)

    return {"predicted_price": float(pred)}