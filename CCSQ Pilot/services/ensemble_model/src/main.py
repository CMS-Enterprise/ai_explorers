###################################################
# ensemble_model
# trains and fits ensemble model
###################################################

from final_fitting.src.fitter.xgboost_regression_fitter import XGBRegressionFitter
from model_dataset.src.main import load_dataframe
from model_training.src.trainer.xgboost_regression_trainer import XGBRegressionTrainer
from .utils import set_user_settings, get_config_settings


# ensemble_selected_features = ['iforest_score', 'lag1', 'prov_mean']


def get_ensemble_trainer(settings):
    if settings is not None:
        set_user_settings(settings)

    trainer = XGBRegressionTrainer(get_config_settings())
    trainer.modeling_df = setup_modeling_df_with_if_anomaly(get_config_settings())
    trainer.run_save_path = trainer.run_save_path.replace('/xgboost_regression', '/xgbr_ensemble')
    return trainer


def get_ensemble_final_fitter(settings):
    if settings is not None:
        set_user_settings(settings)

    fitter = XGBRegressionFitter(get_config_settings())
    fitter.modeling_df = setup_modeling_df_with_if_anomaly(get_config_settings())
    return fitter


def setup_modeling_df_with_if_anomaly(settings):
    model_dataset_path = settings.get('model_dataset_path')
    drop_cols = settings.get('drop_cols')
    modeling_df = load_dataframe(model_dataset_path, drop_cols)

    if_anomaly_scores = settings.get('if_anomaly_scores')
    modeling_df['iforest_score'] = if_anomaly_scores
    modeling_df = modeling_df.dropna()
    return modeling_df
