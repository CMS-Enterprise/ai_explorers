###################################################
# aa_tests.py
# conducts the artifical anomaly tests for both 
# the xgboost and isolation forest models
###################################################


import pandas as pd
import numpy as np
from sklearn.metrics import roc_auc_score


def get_bootstrap_sample(
    model_data,
    scatter,
    shift_n,
    shift_range,
    rng=42,
    threshold_low=0,
    threshold_high=100):
    if rng is None:
        rng = 42

    np.random.seed(rng)

    shift_values = np.repeat(shift_range, shift_n)
    bootstrap_sample = model_data.sample(len(shift_values), replace=True)
    bootstrap_sample['shift'] = shift_values

    bootstrap_sample['mock_score'] = (
            bootstrap_sample['score']
            + bootstrap_sample['shift']
            * np.random.choice([-1, 1], len(bootstrap_sample))
            * np.random.uniform(0, 1, len(bootstrap_sample))
    )

    if scatter == False:
        bootstrap_sample.loc[bootstrap_sample['mock_score'] < threshold_low, 'mock_score'] = threshold_low
        bootstrap_sample.loc[bootstrap_sample['mock_score'] > threshold_high, 'mock_score'] = threshold_high
    elif scatter == True:
        bootstrap_sample.loc[bootstrap_sample['mock_score'] > threshold_high, 'mock_score'] = (
                bootstrap_sample.loc[bootstrap_sample['mock_score'] > threshold_high, 'score']
                - bootstrap_sample.loc[bootstrap_sample['mock_score'] > threshold_high, 'shift']
                * np.random.uniform(0, 1, len(bootstrap_sample))[bootstrap_sample['mock_score'] > threshold_high]
        )
        bootstrap_sample.loc[bootstrap_sample['mock_score'] < threshold_low, 'mock_score'] = (
                bootstrap_sample.loc[bootstrap_sample['mock_score'] < threshold_low, 'score']
                + bootstrap_sample.loc[bootstrap_sample['mock_score'] < threshold_low, 'shift']
                * np.random.uniform(0, 1, len(bootstrap_sample))[bootstrap_sample['mock_score'] < threshold_low]
        )
        bootstrap_sample.loc[bootstrap_sample['mock_score'] < threshold_low, 'mock_score'] = threshold_low
        bootstrap_sample.loc[bootstrap_sample['mock_score'] > threshold_high, 'mock_score'] = threshold_high
    return bootstrap_sample


def artificial_anomaly_test_iforest(model,
                                    model_data,
                                    shift_range,
                                    shift_n=10000,
                                    scatter=True):
    bootstrap_sample = get_bootstrap_sample(model_data, scatter, shift_n, shift_range)

    ## need to generalize
    pred_data = bootstrap_sample.drop(columns=['shift', 'mock_score', 'score', 'prov_mean', 'lag1'])
    score_sample_control = model.score_samples(pred_data)

    pred_data = bootstrap_sample.drop(columns=['shift', 'score'])
    pred_data['prov_mean_diff'] = pred_data['mock_score'] - pred_data['prov_mean']
    pred_data['lag_diff'] = pred_data['mock_score'] - pred_data['lag1']
    pred_data = pred_data.drop(columns=['mock_score', 'prov_mean', 'lag1'])
    # pred_data = pred_data.rename(columns = {"mock_score": "score"})
    score_sample_test = model.score_samples(pred_data)

    results_df = bootstrap_sample.copy()
    results_df['o_score_control'] = score_sample_control * -1
    results_df['o_score_test'] = score_sample_test * -1

    scores_dict = {}

    outlier_range = np.arange(.5, .65, .01)
    roc_df = pd.concat([
        pd.DataFrame({'score': results_df['o_score_control'], 'test_group': False}),
        pd.DataFrame({'score': results_df['o_score_test'], 'test_group': True})],
        axis=0)
    auroc_total = roc_auc_score(y_true=roc_df['test_group'], y_score=roc_df['score'])
    scores_dict['auroc_total'] = auroc_total

    for o in outlier_range:
        roc_df = pd.concat([
            pd.DataFrame({'score': results_df['o_score_control'], 'test_group': False}),
            pd.DataFrame({'score': results_df['o_score_test'], 'test_group': True})],
            axis=0)

        comparison_df = results_df.copy()
        o_label = str(round(o, 3))
        comparison_df['outlier'] = comparison_df['o_score_test'] > o
        comparison_df = (
                comparison_df
                .groupby('shift')[['shift', 'outlier']]
                .transform(lambda x: x.sum())
                / shift_n
        )
        comparison_df = (
            comparison_df
                .rename(columns={'outlier': 'success_rate'})
                .drop_duplicates()
        )

        unweighted_aat_score = np.mean(comparison_df['success_rate'])
        # Weighted Score (higher shifts receive more weight)
        weighted_aat_score = (
            sum(comparison_df['success_rate']
                * (comparison_df['shift']
                   / sum(comparison_df['shift']))
                ))

        roc_df['score'] = roc_df['score'] > o
        auroc_threshold = roc_auc_score(y_true=roc_df['test_group'], y_score=roc_df['score'])

        scores_dict["unweighted_aat_score_" + o_label] = unweighted_aat_score
        scores_dict["weighted_aat_score_" + o_label] = weighted_aat_score
        scores_dict["auroc_threshold_" + o_label] = auroc_threshold

    return scores_dict


def artificial_anomaly_test_xgb(
        model,
        model_data,
        selected_features,
        shift_range,
        threshold_range=range(1, 40),
        shift_n=1000,
        scatter=True,
        rng=42
):
    bootstrap_sample = get_bootstrap_sample(
        model_data, scatter, shift_n, shift_range, rng
    )

    pred_data = bootstrap_sample[selected_features]
    score_sample_control = model.predict(pred_data)
    score_sample_test = model.predict(pred_data)

    # results_df = bootstrap_sample.copy()

    roc_df = pd.concat([
        pd.DataFrame({'score': score_sample_control, 'test_group': False}),
        pd.DataFrame({'score': score_sample_test, 'test_group': True})
    ], axis=0)

    actuals = (
        bootstrap_sample['score']
            .reset_index(drop=True)
            .append(bootstrap_sample['mock_score']
                    .reset_index(drop=True))
    )

    roc_df['actual_score'] = actuals
    scores_dict = {}

    for t in threshold_range:
        roc_df['outlier'] = abs(roc_df['score'] - roc_df['actual_score']) > t
        auroc = roc_auc_score(y_true=roc_df['test_group'], y_score=roc_df['outlier'])
        scores_dict[t] = auroc
    threshold_df = pd.DataFrame()
    threshold_df['Threshold'] = scores_dict.keys()
    threshold_df['AUROC'] = scores_dict.values()
    threshold_df = threshold_df.sort_values("AUROC", ascending=False)

    return threshold_df
