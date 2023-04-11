import pandas as pd
from sklearn.model_selection import RepeatedKFold
from sklearn.model_selection import ParameterGrid
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
import os
from xgboost import XGBRegressor


def tune_xgbr(
        modeling_data,
        target_var,
        parameters,
        save_path,
        run_date,
        rng_number=42
):
    X = modeling_data.drop(columns=[target_var])
    y = modeling_data[target_var]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=rng_number)
    parameters_grid = ParameterGrid(parameters)
    xgb = XGBRegressor(n_estimators=3000, early_stopping_rounds=20, random_state=rng_number)
    cv = RepeatedKFold(n_splits=5, n_repeats=10, random_state=42)
    grid_search = GridSearchCV(
        xgb,
        parameters_grid,
        cv=cv,
        scoring='neg_root_mean_squared_error',
        verbose=3,
        n_jobs=-1
    )

    grid_search.fit(X_train, y_train, eval_set=[(X_test, y_test)])
    results = grid_search.cv_results_
    results_df = pd.DataFrame(results)
    csv_path = os.path.join(save_path, "tuning_results_run_" + run_date + ".csv")
    results_df.to_csv(csv_path, index=False, float_format='%.4f')

    return results_df
