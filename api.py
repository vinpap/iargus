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
        - 'year': the year the car was manufactures
        - 'mileage': the car mileage in kilometers."""

    return {"message": message}

@app.post("/predict")
async def predict(car_details: CarDetails):
    """
    Predicts the price of a second-hand car and returns the result.
    """
    # Commencer par vérifier la sécurité. Puis :
    # 1 - charger le modèle depuis MLflow
    # 2 - faire une prédiction
    # 3 - renvoyer la prédiction en JSON
    raise NotImplemented