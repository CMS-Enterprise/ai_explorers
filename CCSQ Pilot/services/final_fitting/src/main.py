###################################################
# final_fitting
# conducts final fitting for XGBoost and IF models
###################################################

from .fitter.xgboost_regression_fitter import XGBRegressionFitter
from .fitter.isolation_forest_fitter import IsolationForestFitter
from .utils import set_user_settings


def get_final_fitter(settings):
    if settings is not None:
        set_user_settings(settings)

    model_type = settings.get("model_type")
    if model_type is None or len(model_type) == 0:
        raise Exception(
            'model_type is missing in settings or is blank; must be "XGBRegression", "Isolation Forest", or "Ensemble"'
        )

    if model_type == "XGBRegression":
        return XGBRegressionFitter()
    elif model_type == "Isolation Forest":
        return IsolationForestFitter()
    elif model_type == "Ensemble":
        raise Exception("Ensemble model selection not yet implemented")

    raise Exception(
        f'Unknown model_type {model_type}; model_type must be "XGBRegression", "Isolation Forest", or "Ensemble"'
    )


def main(settings):
    if settings is not None:
        set_user_settings(settings)

    raise Exception("""
        main(settings) is not applicable

        expected settings:
            "model_type": STRING
                the type of model selector to create.
                REQUIRED: "XGBRegression", "Isolation Forest", "Ensemble"


        model_trainer usage:
            get_final_fitter(settings):
                returns a model_fitter based on the type of model in settings.
                MUST BE CALLED FIRST, everything else is off of the model_fitter returned here

            model_fitter.fit():
                returns candidate model 
    """)


if __name__ == '__main__':
    main(None)
