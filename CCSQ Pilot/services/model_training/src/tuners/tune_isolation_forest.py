import os
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import ParameterGrid

from artificial_anomaly_tests.aa_tests import artificial_anomaly_test_iforest as aat_iforest


def build_iforest(
        data,
        params,
        rng_number=42
):
    rng = np.random.RandomState(rng_number)

    # Isolation Forest Model
    iforest_model = IsolationForest(
        random_state=rng,
        n_estimators=params['n_estimators'],
        max_samples=params['max_samples'],
        max_features=params['max_features'],
        bootstrap=params['bootstrap'],
        n_jobs=-1
    )

    # Fit and Predict
    iforest_model.fit(data)

    results = iforest_model.predict(data)

    output_df = data.copy()
    output_df['pred'] = results
    output_df['outlier'] = (output_df['pred'] == -1)

    return output_df, iforest_model


def tune_iforest(
        modeling_data,
        parameters,
        save_path,
        run_date,
        rng_number,
        shift_range
):
    search_grid = ParameterGrid(parameters)
    id_num = 1
    combined_results = []
    scores = modeling_data['score']

    print(f"Testing {len(search_grid)} models")
    
    for params in search_grid:
        # Build Model
        if (id_num % 5 == 0):
            print("Testing Model #" + str(id_num))
        prov_means = modeling_data['prov_mean']
        lag1s = modeling_data['lag1']
        filtered_modeling_data = modeling_data[params['features_included']].dropna(how="all")
        model_output, model = build_iforest(filtered_modeling_data, params)

        output_dict = {
            "model_id": id_num,
            "features": str(params['features_included']),
            "model_params": str(params)
        }

        ### NEED TO PUT SHIFT RANGE IN
        aat_results = aat_iforest(
            model,
            filtered_modeling_data.assign(
                score=scores,
                prov_mean=prov_means,
                lag1=lag1s
            ),
            shift_range
        )
        output_dict.update(aat_results)
        combined_results.append(output_dict)

        id_num += 1

    print("Model tuning complete!")
    results_df = pd.DataFrame(combined_results)
    csv_path = os.path.join(save_path, "tuning_results_run_" + run_date + ".csv")
    results_df.to_csv(csv_path, index=False, float_format='%.4f')

    return results_df
