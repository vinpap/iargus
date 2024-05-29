"""
Un seul endpoint : /predict, pour faire une prédiction à partir des infos données par l'utilisateur
Bien sécuriser l'API avec quelque chose de mieux qu'un token unique

Fonctionnement :
Le modèle est entraîné avec des données stockées dans une base de données et stocké à l'aide de MLflow. 
On check les performances du modèles à intervalles réguliers. Le seuil de performances acceptable
est défini à l'avance en MAPE (e.g. pas plus de 20% d'erreur sur le prix en moyenne, fixé par les dirigeants 
de l'Argus dans le scénario). Ce monitoring est réalisé à l'aide d'un script exécuté à intervalles
réguliers. Le réentraînement est automatisé si le seuil n'est pas respecté. Si le seuil n'est toujours
pas respecté après le réentraînement, on en alerte les gestionnaires de l'Argus par email.

"""

import yaml
import os
import re
import ssl
from secrets import token_hex
from datetime import date
from dateutil.relativedelta import relativedelta 

from fastapi import FastAPI, Request
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from pydantic import BaseModel
import pandas as pd
import mlflow
import mysql.connector
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
    security_token: str

class UserDetails(BaseModel):
    """
    Stores information about a user.
    """
    first_name: str
    surname: str
    email: str


def generate_token() -> str:
    """
    Generates a random token.
    """
    return str(token_hex(32))

def email_format_is_right(email_address: str) -> bool:
    """
    Checks if the provided email address follows the right format.
    """
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

    # pass the regular expression
    # and the string into the fullmatch() method
    if(re.fullmatch(regex, email_address)):
        return True
 
    else:
        return False


def check_token(token: str) -> bool:
    """
    Looks up the provided token in the database to make sure it is valid.
    """
    with mysql.connector.connect(user=os.environ["MYSQL_USER"], 
                            password=os.environ["MYSQL_PWD"], 
                            host=os.environ["MYSQL_HOST"], 
                            database="iargus_api") as db:
        with db.cursor() as c:
            query = """SELECT creation_date FROM tokens WHERE token=%s""" 
            vars = (token,)
            c.execute(query, vars)
            results = c.fetchall()

            print(results)
            if len(results) == 0:
                # The token does not exist in the database
                return False
            

            current_date = date.today()
            days_elapsed = current_date - results[0][-1]
            if days_elapsed.days > 180:
                return False
        
        return True



app = FastAPI()
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.on_event("startup")
async def startup():
    """
    Gets the API ready.

    Includes security measures such as token management, HTTPS, rate limiting...
    """
    with open("./config.yml", "r") as config_file:
        config = yaml.safe_load(config_file)
        ssl_cert_filepath = config["security"]["ssl_certificate_path"]
        ssl_key_filepath = config["security"]["ssl_key_path"]

    # Making sure the database that stores the tokens is available
    # (an exception will be raised otherwise)
    db = mysql.connector.connect(user=os.environ["MYSQL_USER"], 
                            password=os.environ["MYSQL_PWD"], 
                            host=os.environ["MYSQL_HOST"], 
                            database="iargus_api")

    

    # Loading the SSL certificate and key
    # WARNING: this is a certificate for testing purpose only. In production,
    # get a certificate from a trusted source instead.
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(ssl_cert_filepath, keyfile=ssl_key_filepath)



@app.get("/")
async def root(security_token: str):
    """
    Returns a help message.
    """

    if not check_token(security_token):
        message = """The provided token does not exist or has expired. Please get a new one using the /get_token endpoint"""

    else:
        message = """Welcome to the IArgus prediction model API.\
            In order to use the model, send a request to the /predict endpoint
            with the following parameters in a JSON:
            - 'state': the two letters that reference the US state where the car was sold
            - 'make': the make of the car
            - 'model': the model of the car
            - 'year': the year the car was manufactured
            - 'mileage': the car mileage in kilometers."""

    return {"message": message}

@app.post("/get_token")
@limiter.limit("10/minute")
async def get_token(request: Request, user_details: UserDetails):
    """
    Generates a random token for the user whom information was
    provided and stores these information plus the token in the
    database.
    """
    
    if not email_format_is_right(user_details.email):
        return {"message": "The provided email address must follow the right format"}
    
    token = generate_token()
    with mysql.connector.connect(user=os.environ["MYSQL_USER"], 
                            password=os.environ["MYSQL_PWD"], 
                            host=os.environ["MYSQL_HOST"], 
                            database="iargus_api") as db:
        with db.cursor() as c:
            current_date = date.today()
            expiration_date = current_date + relativedelta(months=6)
            expiration_date = expiration_date.strftime("%Y-%m-%d")
            query = """INSERT INTO tokens (first_name, surname, email, token, creation_date) VALUES (%s, %s, %s, %s, %s)""" 
            query_vars = (user_details.first_name,
                          user_details.surname,
                          user_details.email,
                          token,
                          expiration_date)
            c.execute(query, query_vars)
            db.commit()
    
    return {"message": "Here is your access token",
            "token": token}



@app.post("/predict")
@limiter.limit("10/minute")
async def predict(request: Request, car_details: CarDetails):
    """
    Predicts the price of a second-hand car and returns the result.
    """
    if not check_token(car_details.security_token):
        message = """The provided token does not exist or has expired. Please get a new one using the /get_token endpoint"""
        return {"message": message}

    # Loading the model from MLflow
    client = MlflowClient(tracking_uri=os.environ["MLFLOW_HOST"])
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