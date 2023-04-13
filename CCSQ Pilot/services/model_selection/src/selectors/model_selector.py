import pandas as pd

from abc import ABC, abstractmethod
from ..utils import get_config_settings


class ModelSelector(ABC):
    def __init__(self):
        settings = get_config_settings()

        pd.set_option('display.max_columns', None)

        self.top_models = settings.get('top_models')
        if self.top_models is None or self.top_models == 0:
            raise Exception("could not find top_models or it's 0")

        self.model_run_data_path = settings.get('model_run_data_path')
        if self.model_run_data_path is None or len(self.model_run_data_path) == 0:
            raise Exception("could not find model_run_data_path or it's blank")

        self.model_data = pd.read_csv(self.model_run_data_path)

    @abstractmethod
    def get_top_models(self):
        pass

    @abstractmethod
    def get_candidate_model_by_index(self, index):
        pass

    @abstractmethod
    def get_candidate_model_params_by_index(self, index):
        pass
