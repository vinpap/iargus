"""
This script set ups everything needed to run the tests.
"""
import pandas as pd
from mlflow import MlflowClient

from model_monitoring import preprocess_features, train_model


testing_data = pd.read_csv("./test/testing_data.csv")
X = preprocess_features(testing_data)
y = testing_data["price"].values

# If no model has been trained, we train one quickly.
client = MlflowClient()
model_versions = client.search_model_versions(f"name='iargus'")
if len(model_versions) == 0:
    train_model(X, y)