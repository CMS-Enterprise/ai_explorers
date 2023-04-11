###################################################
# outcome_analysis
# generates a results summary notebook
###################################################
import pandas as pd

from model_dataset.src.main import load_dataframe
from .utils import set_user_settings, get_config_settings


def isolation_forest():
    settings = get_config_settings()
    score_column_name = settings.get('score_column_name')
    provider_id_column_name = settings.get('provider_id_column_name')
    model_type = 'Isolation Forest'

    model_dataset_path = settings.get('model_dataset_path')
    modeling_dataset = load_dataframe(model_dataset_path, None, keep_lag1=True)

    if_model = settings.get('if_model')
    if if_model is None:
        raise Exception('Could not find if_model')

    if_outlier_prediction = if_model.score_samples(
        modeling_dataset.drop(columns=['year', 'quarter', provider_id_column_name, 'lag1'])
    ) * -1

    if_outlier_prediction_threshold = settings.get('if_outlier_prediction_threshold')

    if_modeling_dataset = modeling_dataset.copy()[
        [score_column_name, 'lag1', 'year', 'quarter', provider_id_column_name]
    ]
    if_modeling_dataset['outlier'] = if_outlier_prediction > if_outlier_prediction_threshold
    if_modeling_dataset['lag1_diff'] = if_modeling_dataset[score_column_name] - if_modeling_dataset['lag1']
    if_modeling_dataset['model'] = model_type

    return if_modeling_dataset


def xgboost_regression():
    settings = get_config_settings()
    score_column_name = settings.get('score_column_name')
    provider_id_column_name = settings.get('provider_id_column_name')
    model_type = "XGBoost Regression"

    model_dataset_path = settings.get('model_dataset_path')
    modeling_dataset = load_dataframe(model_dataset_path, None, keep_lag1=True)

    model = settings.get('xgbr_model')
    if model is None:
        raise Exception("Missing xgbr_model in settings")

    xgbr_x_cols = settings.get('xgbr_x_cols')
    xgbr_y_cols = settings.get('xgbr_y_cols')
    x, y = modeling_dataset[xgbr_x_cols], modeling_dataset[xgbr_y_cols]

    xgb_predicted_score = model.predict(x)

    outlier_prediction_threshold = settings.get('xgbr_outlier_prediction_threshold')
    xgb_outlier_prediction = (abs(y[score_column_name] - xgb_predicted_score) > outlier_prediction_threshold)

    xgb_modeling_dataset = modeling_dataset.copy()[
        [score_column_name, 'lag1', 'year', 'quarter', provider_id_column_name]
    ]
    xgb_modeling_dataset['outlier'] = xgb_outlier_prediction
    xgb_modeling_dataset['predicted_score'] = xgb_predicted_score
    xgb_modeling_dataset['lag1_diff'] = xgb_modeling_dataset[score_column_name] - xgb_modeling_dataset['lag1']
    xgb_modeling_dataset['model'] = model_type

    return xgb_modeling_dataset


def get_comparison(xgb_modeling_dataset, if_modeling_dataset):
    settings = get_config_settings()
    score_column_name = settings.get('score_column_name')
    provider_id_column_name = settings.get('provider_id_column_name')

    modeling_dataset_path = settings.get('modeling_dataset_path')
    modeling_dataset = pd.read_csv(modeling_dataset_path)

    comparison_df = pd.concat([xgb_modeling_dataset, if_modeling_dataset], axis=0)

    provider_means = modeling_dataset \
        .groupby(provider_id_column_name)[score_column_name] \
        .mean() \
        .reset_index() \
        .rename(columns={score_column_name: 'provider_mean_score'})

    return comparison_df.merge(provider_means, how='left', on=provider_id_column_name)


def main(settings):
    if settings is not None:
        set_user_settings(settings)

    xgbr_dataset = xgboost_regression()
    if_dataset = isolation_forest()

    comp = get_comparison(xgbr_dataset, if_dataset)

    return comp, xgbr_dataset, if_dataset


if __name__ == '__main__':
    main(None)
