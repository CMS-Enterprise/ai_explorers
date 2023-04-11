from datetime import datetime
from pathlib import Path

from model_dataset.src.main import load_dataframe
from .model_trainer import ModelTrainer
from ..utils import get_config_settings
from ..tuners.tune_isolation_forest import tune_iforest


class IsolationForestTrainer(ModelTrainer):
    def __init__(self):
        super().__init__()

        settings = get_config_settings()

        self.model_dataset_path = settings.get('model_dataset_path')
        if self.model_dataset_path is None:
            raise Exception("could not find model_dataset_path")

        self.run_save_path = settings.get('run_save_path')
        if self.run_save_path is None:
            raise Exception("could not find run_save_path")
        self.run_save_path += "/isolation_forest"

        self.rng_number = settings.get('rng_number')
        if self.rng_number is None:
            self.rng_number = 42

        self.drop_cols = settings.get('drop_cols')
        if self.drop_cols is None:
            self.drop_cols = []

        self.if_parameters = settings.get('if_parameters')

        self.shift_range = settings.get('shift_range')
        if self.shift_range is None:
            raise Exception("could not find shift_range")

        self.score_column_name = settings.get('score_column_name')
        if self.score_column_name is None:
            raise Exception("could not find score_column_name")

        self.modeling_df = load_dataframe(self.model_dataset_path, self.drop_cols)

    def tune(self):
        if self.if_parameters is None:
            raise Exception("could not find if_parameters")
        
        current_date = datetime.now().strftime("%Y-%m-%d-%Hh%Mm")
        Path(self.run_save_path).mkdir(parents=True, exist_ok=True)

        return tune_iforest(
            self.modeling_df,
            self.if_parameters,
            self.run_save_path,
            current_date,
            rng_number=self.rng_number,
            shift_range=self.shift_range
        )

    def get_model_for_feature_importance(self):
        raise Exception("Cannot get model for feature importance for Isolation Forest")

    def plot_feature_importance(self):
        raise Exception("Cannot plot feature importance for Isolation Forest")
