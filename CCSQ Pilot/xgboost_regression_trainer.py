from matplotlib import pyplot
from xgboost import XGBRegressor, plot_importance
from datetime import datetime
from pathlib import Path

from model_dataset.src.main import load_dataframe
from .model_trainer import ModelTrainer
from ..utils import get_config_settings
from ..tuners.tune_xgboost_regression import tune_xgbr


class XGBRegressionTrainer(ModelTrainer):
    def __init__(self, settings=None):
        super().__init__()

        if settings is None:
            settings = get_config_settings()

        self.model_dataset_path = settings.get('model_dataset_path')
        if self.model_dataset_path is None:
            raise Exception("could not find model_dataset_path")

        self.run_save_path = settings.get('run_save_path')
        if self.run_save_path is None:
            raise Exception("could not find run_save_path")
        self.run_save_path += "/xgboost_regression"

        self.drop_cols = settings.get('drop_cols')
        if self.drop_cols is None:
            self.drop_cols = []

        self.xgbr_parameters = settings.get('xgbr_parameters')

        self.score_column_name = settings.get('score_column_name')
        if self.score_column_name is None:
            raise Exception("could not find score_column_name")

        self.modeling_df = load_dataframe(self.model_dataset_path, self.drop_cols)

    def tune(self):
        if self.xgbr_parameters is None:
            raise Exception("could not find xgbr_parameters")

        current_date = datetime.now().strftime("%Y-%m-%d-%Hh%Mm")
        Path(self.run_save_path).mkdir(parents=True, exist_ok=True)

        return tune_xgbr(
            self.modeling_df,
            self.score_column_name,
            self.xgbr_parameters,
            self.run_save_path,
            current_date
        )

    def get_model_for_feature_importance(self):
        model = XGBRegressor()
        x = self.modeling_df.drop(columns=[self.score_column_name])
        y = self.modeling_df[[self.score_column_name]]
        model.fit(x, y)

        return model

    def plot_feature_importance(self):
        model = self.get_model_for_feature_importance()
        plot_importance(model)
        pyplot.show()
