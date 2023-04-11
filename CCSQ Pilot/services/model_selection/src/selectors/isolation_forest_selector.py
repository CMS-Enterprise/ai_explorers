import ast

import pandas as pd
from .model_selector import ModelSelector


class IsolationForestSelector(ModelSelector):
    def __init__(self):
        super().__init__()

    def get_top_models(self):
        params = self.model_data['model_params'].map(eval).apply(pd.Series)
        filtered = self.model_data.filter(regex='model_id|^outliers_score_diff|^normals_score_diff|^auroc', axis=1)
        filtered = pd.concat([params, filtered], axis=1)

        top_model_ids = filtered \
            .sort_values(by='auroc_total', ascending=False)['model_id'] \
            .head(self.top_models)

        top_models = filtered[
            filtered['model_id'].isin(top_model_ids)
        ].sort_values(by='auroc_total', ascending=False)

        return top_models[top_models.columns.drop(list(top_models.filter(regex='outliers|normals')))]

    def get_candidate_model_by_index(self, index):
        top_models = self.get_top_models()
        return top_models[top_models['model_id'] == index]

    def get_candidate_model_params_by_index(self, index):
        candidate_model = self.model_data.loc[self.model_data['model_id'] == index]
        return ast.literal_eval(candidate_model['model_params'].values[0])
