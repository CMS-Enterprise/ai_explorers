import pandas as pd
from abc import ABC, abstractmethod


class ModelTrainer(ABC):
    def __init__(self):
        pd.set_option('display.max_columns', None)

    @abstractmethod
    def tune(self):
        pass

    @abstractmethod
    def get_model_for_feature_importance(self):
        pass

    @abstractmethod
    def plot_feature_importance(self):
        pass
