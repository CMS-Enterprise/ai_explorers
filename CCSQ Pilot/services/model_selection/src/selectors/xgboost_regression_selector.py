import ast

from .model_selector import ModelSelector
from ..utils import get_config_settings


class XGBRegressionSelector(ModelSelector):
    def __init__(self):
        super().__init__()

        settings = get_config_settings()

        self.mean_test_score_column_name = settings.get('mean_test_score_column_name')
        if self.mean_test_score_column_name is None:
            raise Exception("could not find mean_test_score_column_name")

        self.std_test_score_column_name = settings.get('std_test_score_column_name')
        if self.std_test_score_column_name is None:
            raise Exception("could not find std_test_score_column_name")

        self.rank_test_score_column_name = settings.get('rank_test_score_column_name')
        if self.rank_test_score_column_name is None:
            raise Exception("could not find rank_test_score_column_name")

    def get_top_models(self):
        cols = [self.mean_test_score_column_name, self.std_test_score_column_name, self.rank_test_score_column_name]
        # TODO: Can param* come from config?
        cols.extend(list(filter(lambda col: 'param' in col, self.model_data.columns)))

        filtered_sorted = self.model_data[cols].sort_values(by=self.mean_test_score_column_name, ascending=False)
        return filtered_sorted.head(self.top_models)

    def get_candidate_model_by_index(self, index):
        return self.model_data.loc[index]

    def get_candidate_model_params_by_index(self, index):
        candidate_model = self.get_candidate_model_by_index(index)
        return ast.literal_eval(candidate_model['params'])
