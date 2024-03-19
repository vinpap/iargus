import os

import mysql.connector
import mlflow
from mlflow.models import infer_signature
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.callbacks import EarlyStopping


mlflow.set_tracking_uri(uri="http://127.0.0.1:8080")

def get_data():
    """
    Retrieves car data from the database.
    """

    # MYSQL username and password need to be set as environment variables
    with mysql.connector.connect(
        host="localhost",
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PWD"],
        database=os.environ["MYSQL_DB_NAME"],
    ) as db:
        with db.cursor() as c:
            query = """SELECT * FROM Car_details"""
            c.execute(query)
            car_data = c.fetchall()

            # Ici, transformer les données en dataframe avant de les renvoyer

def train_model(X_train, y_train):
    """
    Creates a DNN and trains it using the data provided.

    MAPE is used to measure loss and accuracy.
    """
    callback = EarlyStopping(monitor='loss', patience=3)

    model = Sequential()
    model.add(Dense(100, input_shape=(X_train.shape[1],), activation='relu'))
    model.add(Dense(120, activation='relu'))
    model.add(Dense(1, activation='linear'))
    model.compile(loss='mean_absolute_percentage_error', optimizer='adam', metrics=['mean_absolute__percentage_error'])
    model.fit(X_train, y_train, epochs=150, batch_size=100, callbacks=[callback])

    mlflow.set_experiment("IArgus")
    with mlflow.start_run():
        params = model.get_params()
        mlflow.log_params(params)
        signature = infer_signature(X_train, y_train)
        model_info = mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="/IArgus",
            signature=signature,
            input_example=X_train,
            registered_model_name="/IArgus"
        )

def test_model():
    pass

if __name__ == "main":
    car_data = get_data()
    # 2 - On test le modèle existant avec ces données
    # 3 - Si la MAPE est inférieure au seuil prévu, on ne fait rien
    # 4 - Sinon, on réentraîne le modèle avec toutes les données (récentes et
    # anciennes), puis on test
    # 5 - Si la MAPE n'est toujours pas en-dessous du seuil, on envoie un mail

