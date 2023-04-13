import pickle

from xgboost import XGBRegressor

from model_dataset.src.main import load_dataframe
from ..utils import get_config_settings
from .model_fitter import ModelFitter


class XGBRegressionFitter(ModelFitter):
    model = None

    def __init__(self, settings=None):
        super().__init__()

        if settings is None:
            settings = get_config_settings()

        self.model_dataset_path = settings.get('model_dataset_path')
        if self.model_dataset_path is None:
            raise Exception("could not find model_dataset_path")

        self.final_fit_save_path = settings.get('final_fit_save_path')

        self.random_seed = settings.get('random_seed')
        if self.random_seed is None:
            self.random_seed = 42

        self.drop_cols = settings.get('drop_cols')
        if self.drop_cols is None:
            self.drop_cols = []

        self.xgbr_final_params = settings.get('xgbr_final_params')
        if self.xgbr_final_params is None:
            raise Exception("could not find xgbr_final_params")

        self.score_column_name = settings.get('score_column_name')
        if self.score_column_name is None:
            raise Exception("could not find score_column_name")

        self.modeling_df = load_dataframe(self.model_dataset_path, self.drop_cols)

    def fit(self):
        self.model = XGBRegressor(
            **self.xgbr_final_params,
            random_state=self.random_seed,
        )

        x = self.modeling_df.drop(columns=self.score_column_name)
        y = self.modeling_df[[self.score_column_name]]

        self.model.fit(x, y)

        return self.model

    def save_pickle(self):
        if self.final_fit_save_path is None:
            raise Exception("could not find final_fit_save_path")

        with open(self.final_fit_save_path, 'wb') as f:
            pickle.dump(self.model, f)
