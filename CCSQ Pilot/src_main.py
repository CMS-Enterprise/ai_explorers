###################################################
# model_training
# conducts model training and hyperparameter tuning
# for all three models
###################################################

from .utils import set_user_settings
from .trainer.xgboost_regression_trainer import XGBRegressionTrainer
from .trainer.isolation_forest_trainer import IsolationForestTrainer


def get_model_trainer(settings):
    if settings is not None:
        set_user_settings(settings)

    model_type = settings.get("model_type")
    if model_type is None or len(model_type) == 0:
        raise Exception(
            'model_type is missing in settings or is blank; must be "XGBRegression", "Isolation Forest", or "Ensemble"'
        )

    if model_type == "XGBRegression":
        return XGBRegressionTrainer()
    elif model_type == "Isolation Forest":
        return IsolationForestTrainer()
    elif model_type == "Ensemble":
        raise Exception("Ensemble model selection not yet implemented")

    raise Exception(
        f'Unknown model_type {model_type}; model_type must be "XGBRegression", "Isolation Forest", or "Ensemble"'
    )


def main(settings):
    if settings is not None:
        set_user_settings(settings)

    raise Exception("""
        main(settings) is not applicable to model_selection

        expected settings:
            "model_type": STRING
                the type of model selector to create.
                REQUIRED: "XGBRegression", "Isolation Forest", "Ensemble"

            "model_dataset_path": FILEPATH/STRING
                the location of the modeling dataset (e.g. OP-10.csv)
                REQUIRED, will fail if not specified
                
            "xgbr_parameters": Dictionary
                used for XGBoost Regression training.
                
            "if_parameters": Dictionary
                used for Isolation Forest training.
                

        model_trainer usage:
            get_model_trainer(settings):
                returns a model_trainer based on the type of model in settings.
                MUST BE CALLED FIRST, everything else is off of the model_trainer returned here

            model_trainer.tune():
                returns candidate model 
    """)


if __name__ == '__main__':
    main(None)
