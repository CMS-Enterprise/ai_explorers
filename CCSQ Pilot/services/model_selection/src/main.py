###################################################
# model_selection
# conducts model selection
###################################################
from .selectors.xgboost_regression_selector import XGBRegressionSelector
from .selectors.isolation_forest_selector import IsolationForestSelector
from .utils import set_user_settings


def get_model_selector(settings):
    if settings is not None:
        set_user_settings(settings)

    model_type = settings.get("model_type")
    if model_type is None or len(model_type) == 0:
        raise Exception(
            'model_type is missing in settings or is blank; must be "XGBRegression", "Isolation Forest", or "Ensemble"'
        )

    if model_type == "XGBRegression":
        return XGBRegressionSelector()
    elif model_type == "Isolation Forest":
        return IsolationForestSelector()
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
                
            "model_run_data_path": FILEPATH/STRING
                the location of the tuning results (e.g. tuning_results_final.csv)
                REQUIRED, will fail if not specified
                
            "top_models": INT
                the number of models to return from get_top_models(settings)
                OPTIONAL, defaults to the value in config.json if not specified
                
            
        
        model_selection usage:
            get_model_selector(settings):
                returns a model_selector based on the type of model in settings.
                MUST BE CALLED FIRST, everything else is off of the model_selector returned here
        
            model_selector.get_top_models():
                returns the top X models where X comes from "top_models" in settings.
                "top_models" defaults to the value in config.json if not specified 
                
            model_selector.get_candidate_model_by_index(index):
                returns the model from get_top_models() where the index matches the index.
                
            model_selector.get_candidate_model_params_by_index(index):
                returns the model params from get_top_models() where the index matches the index.
    """)


if __name__ == '__main__':
    main(None)
