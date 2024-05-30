"""
Unit tests for model_monitoring.py. Note that a MLflow server needs to be active in
order for these tests to run.
"""

import sys
import pandas as pd
import numpy as np
import mlflow
from mlflow import MlflowClient

from model_monitoring import preprocess_features, test_model, train_model

sys.path.append(".")

def test_preprocessing():
    """
    Makes sure the preprocessing function works properly.

    Most importantly, checks that the categorical features encoding
    using one-hot vectors works well.
    """
    testing_data = pd.read_csv("./test/testing_data.csv")
    X_test = preprocess_features(testing_data)
    assert len(X_test) == len(testing_data)
    
    unique_makes_count = testing_data["make"].nunique()
    unique_models_count = testing_data["model"].nunique()
    unique_states_count = testing_data["state"].nunique()
    minimum_zeros_count = unique_makes_count + unique_models_count + unique_states_count - 3

    for row_index in range(len(X_test)):
        assert np.count_nonzero(X_test[row_index,:] == 0) >= minimum_zeros_count
        assert np.count_nonzero(X_test[row_index,:] == 1) <= 5

def test_test():
    """
    Test for the test_model function.
    """
    testing_data = pd.read_csv("./test/testing_data.csv")
    X_test = preprocess_features(testing_data)
    y_test = testing_data["price"].values
    mape = test_model(X_test, y_test)
    assert isinstance(mape, float) and 0 <= mape <=1
    
