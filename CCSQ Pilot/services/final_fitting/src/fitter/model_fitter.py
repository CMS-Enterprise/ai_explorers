import pandas as pd
from abc import ABC, abstractmethod


class ModelFitter(ABC):
    def __init__(self):
        pd.set_option('display.max_columns', None)

    @abstractmethod
    def fit(self):
        pass

    @abstractmethod
    def save_pickle(self):
        pass
