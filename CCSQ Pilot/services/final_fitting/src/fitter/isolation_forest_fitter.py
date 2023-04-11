import pickle
import numpy as np
from sklearn.ensemble import IsolationForest

from model_dataset.src.main import load_dataframe
from ..utils import get_config_settings
from .model_fitter import ModelFitter


class IsolationForestFitter(ModelFitter):
    model = None
    anomaly_scores = None

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

        self.if_final_params = settings.get('if_final_params')
        if self.if_final_params is None:
            raise Exception("could not find if_final_params")

        self.score_column_name = settings.get('score_column_name')
        if self.score_column_name is None:
            raise Exception("could not find score_column_name")

        self.modeling_df = load_dataframe(self.model_dataset_path, self.drop_cols)

    def fit(self):
        self.model = IsolationForest(
            **self.if_final_params,
            random_state=np.random.RandomState(self.random_seed),
            n_jobs=-1
        )

        self.model.fit(self.modeling_df)
        return self.model

    def save_pickle(self):
        if self.final_fit_save_path is None:
            raise Exception("could not find final_fit_save_path")

        with open(self.final_fit_save_path, 'wb') as f:
            pickle.dump(self.model, f)

    def get_anomaly_scores(self, model=None):
        if model is None:
            if self.model is None:
                raise Exception("Must call fit() before get_anomaly_scores(model) or pass in model")
            model = self.model

        self.anomaly_scores = model.score_samples(self.modeling_df) * -1
        return self.anomaly_scores

    def get_value_counts(self):
        if self.anomaly_scores is None:
            raise Exception("Must call get_anomaly_scores() before get_value_counts()")

        df = self.modeling_df
        df['iforest_score'] = self.anomaly_scores
        df['iforest_pred'] = self.anomaly_scores > 0.5

        return df['iforest_pred'].value_counts()
