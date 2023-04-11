###################################################
# xgbr_test
# test run of XGBoost regression models
###################################################
import numpy as np
from sklearn.model_selection import RepeatedKFold
from sklearn.model_selection import cross_val_score
from xgboost import XGBRegressor

def test_xgbr(modeling_dataset):
    model = XGBRegressor()
    X = modeling_dataset.drop(columns='score')
    y = modeling_dataset[['score']]

    cv = RepeatedKFold(n_splits=5, n_repeats=10, random_state=42)
    scores = cross_val_score(
        model,
        X, y,
        scoring='neg_root_mean_squared_error',
        cv=cv,
        n_jobs=- 1,
        error_score="raise",
        verbose=True
    )

    model.fit(X, y)
    yhat = model.predict(X)

    diff = y['score'] - yhat
    cv_rmse = np.mean(-scores)

    return model, cv_rmse
