import pandas as pd
import numpy as np

from model_monitoring import preprocess_data

def test_preprocessing():
    """
    Makes sure the preprocessing function works properly.

    Most importantly, checks that the categorical features encoding
    using one-hot vectors works well.
    """
    testing_data = pd.read_csv("./test/testing_data.csv")
    X_test, y_test = preprocess_data(testing_data)
    assert len(X_test) == len(testing_data)
    assert len(y_test) == len(testing_data)
    
    unique_makes_count = testing_data["make"].nunique()
    unique_models_count = testing_data["model"].nunique()
    unique_states_count = testing_data["state"].nunique()
    minimum_zeros_count = unique_makes_count + unique_models_count + unique_states_count - 3

    for row_index in range(len(X_test)):
        assert np.count_nonzero(X_test[row_index,:] == 0) >= minimum_zeros_count
        assert np.count_nonzero(X_test[row_index,:] == 1) <= 5
