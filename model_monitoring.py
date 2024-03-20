import os
import sys
import logging
import pickle
import yaml
import smtplib
from email.mime.text import MIMEText
from datetime import date

import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_percentage_error
import mysql
import mlflow
from mlflow.models import infer_signature
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.callbacks import EarlyStopping


mlflow.set_tracking_uri(uri="http://127.0.0.1:8080")
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', filename='monitoring.log', level=logging.INFO)
logger = logging.getLogger()


def get_data(most_recent_only: bool=False, last_training_date=date.today()):
    """
    Retrieves car data from the database.

    If most_recent_only is set to True, this function will return records
    added after the latest training only. The last training date is 
    specified by last_training_date.
    """
    logger.info("Retrieving data from database")
    # MYSQL username, password and database name need to be set as environment variables
    with mysql.connector.connect(
        host="localhost",
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PWD"],
        database=os.environ["MYSQL_DB_NAME"],
    ) as db:
        with db.cursor() as c:
            if most_recent_only:
                query = f"""SELECT * FROM car_details WHERE date_added > '{last_training_date.strftime("%Y-%m-%d")}'"""
            else:
                query = """SELECT * FROM car_details"""
            c.execute(query)
            car_data = c.fetchall()

            column_names = ["id", "state", "model", "make", "year", "mileage", "price", "date_added"]
            car_details_df = pd.DataFrame(car_data, columns=column_names)
            car_details_df.drop(columns=["id"], inplace=True)
            return car_details_df

def preprocess_data(raw_data: pd.DataFrame):
    """
    Preprocess raw data in order to turn in into features usable by
    the model.

    Preprocessing includes encoding categorical features using OHE.
    Returns a tuple (X, y) where X contains the features and y the target 
    value.
    """
    logger.info("Preprocessing data")
    try:
        with open("./features_encoder.pkl", "rb") as encoder_file:
            encoder = pickle.load(encoder_file)
    except FileNotFoundError:
        logger.error("No encoding model was found, please train the model to generate one")
        raise

    cat_values = raw_data[["state", "make", "model"]]
    one_hot_vec = encoder.transform(cat_values).toarray()
    X = np.hstack((one_hot_vec, raw_data["year"].values[:, None], raw_data["mileage"].values[:, None]))
    y = raw_data["price"].values
    return X, y

def send_email_alert(subject: str, email: str):
    """
    Sends an email to the admin in order to tell him the model still does not
    meet the performance criteria after retraining with new data.
    """
    sender = os.environ["SMTP_LOGIN"]
    recipient = os.environ["SMTP_RECIPIENT"]
    recipients = [recipient]
    password = os.environ["SMTP_PWD"]
    smtp_server = os.environ["SMTP_SERVER"]
    msg = MIMEText(email)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(sender, password)
       smtp_server.sendmail(sender, recipients, msg.as_string())
    logger.info(f"Email alert sent to {recipient}")

def train_model(X, y):
    """
    Creates a DNN and trains it using the data provided.

    MAPE is used to measure loss and accuracy.
    """

    logger.info("Training model")
    callback = EarlyStopping(monitor='val_loss', patience=3)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)

    model = Sequential()
    model.add(Dense(100, input_shape=(X_train.shape[1],), activation='relu'))
    model.add(Dense(120, activation='relu'))
    model.add(Dense(1, activation='linear'))
    model.compile(loss='mean_absolute_percentage_error', optimizer='adam', metrics=['mean_absolute_percentage_error'])
    mlflow.set_experiment("IArgus")
    #mlflow.keras.log_model(model, 'car_price_predictor')
    #mlflow.keras.autolog()
    
    with mlflow.start_run():
        signature = infer_signature(X_train, y_train)
        mlflow.keras.autolog()
        model.fit(X_train, y_train, validation_split=0.1, epochs=150, batch_size=100, callbacks=[callback])
        
        # A EXÉCUTER AVEC UN PC PLUS PUISSANT
        """model_info = mlflow.keras.log_model(
            model=model,
            artifact_path="/IArgus",
            signature=signature,
            input_example=X_train,
            registered_model_name="/IArgus"
        )"""
        

    logger.info("The model has been trained. Metrics related to it are available on MLflow")
    # We update the config file to change the last training date
    with open("./config.yml", "rw") as config_file:
        config = yaml.safe_load(config_file)
        config["monitoring"]["last_training"] = date.today()
        yaml.dump(config, config_file)
    
    return test_model(X_test, y_test)

def test_model(X_test, y_test):
    """
    Evaluates the model with the provided data and returns the 
    mean absolute percentage error.
    """
    logger.info("Testing model")
    mlflow.set_experiment("IArgus")
    # Chemin de modèle temporaire, remplacer par l'URI sur MLflow
    eval_results = mlflow.evaluate(
        model="/home/vincent/Development/iargus/mlartifacts/593420517438876381/6e9ba1a01edd459ebb88acdf3f3449d1/artifacts/model",
        data=X_test,
        targets=y_test,
        model_type='regressor'
        )
    print(eval_results)
    raise
    return 0.15

if __name__ == "__main__":

    """# TEMPORAIRE
    all_car_data = get_data()
    X, y = preprocess_data(all_car_data)
    train_model(X, y)
    raise"""

    # Retrieving all the records added after the last training
    with open("./config.yml") as config_file:
        config = yaml.safe_load(config_file)
        last_training_date = config["monitoring"]["last_training"]
        mape_threshold = config["monitoring"]["MAPE_threshold"]

    # Testing the model with these data
    car_data = get_data(most_recent_only=True, last_training_date=last_training_date)
    if len(car_data) == 0:
        logger.warning("No new data has been added since last training")
        logger.warning("Exiting")
        sys.exit(0)


    X_test, y_test = preprocess_data(car_data)
    mape = test_model(X_test, y_test)

    if mape > mape_threshold:
        logger.warning(f"Mean Absolute Percentage Error is too high after testing the model with new data. {mape} exceeds threshold of {mape_threshold}. Model will be retrained using the new data")
        # Retrieving ALL data in the database
        all_car_data = get_data()
        X, y = preprocess_data(all_car_data)
        new_mape = train_model(X, y)

        if new_mape > mape_threshold:
            subject = "Your model performance is getting low!"
            email = f"""This is an automatic message, please do not reply.\
                You are receiving this message because your model IArgus has\
                been tested with new data and its performance is getting low
                despite retraining it with new data.\
                On average, the model has a relative absolute error of {new_mape*100}%,\
                which is over the set threshold of {mape_threshold*100}%.
                Please get in touch with the IArgus data team for more information.
                """
            send_email_alert(subject=subject, email=email)
            logger.warning(f"Mean Absolute Percentage Error is too high after retraining. {mape} still exceeds threshold of {mape_threshold}. An alert has been sent by email to the application admin")
    
    else:
        logger.info(f"The model was tested with new data. Its mean absolute percentage error is still below the threshold ({mape} < {mape_threshold})")
        



