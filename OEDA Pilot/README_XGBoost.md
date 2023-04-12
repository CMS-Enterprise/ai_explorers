# XGBoost Models

This README file describes the contents and use of the XGBoost
models developed as part of the OEDA AI Explorers pilot project. 
These models are contained in the MLFlow_Py_XGBoost notebook
originally developed in the CCW VRDC environment and depend on 
the data tables and resources deployed there.

## Loading Data

The cells under the "Load Data" heading import a Spark table from the
Databricks system and, if necessary, apply a train/test split. The `train`
variable holds the training split, and to use one of the preprocessed
tables __with resampling__ applied, then the appropriate table name
should simply be used as an argument. (For example, in the current version, 
the source table selected has TSFRESH features, SMOTE-NC oversampling, and 
Tomek's Links undersampling). Because resampling was applied only to the
training data, these tables have already been split.

By contrast, to use only the one-hot encoded data, the call needs to apply
the training split, like this:

```
train = spark.table("eldb.opioid_SA_LA_hosp_final_tsfresh_and_demos_ohe") \
  .where(train_split_sql).drop("bene_id")
```

The `input_data_descriptor` string and `run_tags` dictionary are only used
to name and tag the run in MLflow, and don't affect the processing whatsoever.

## Hyperparameter Search

In the next set of cells, we set up our `hyperflow` for searching the
"hyperparameter" space. For this set of experiments, we sweep over five
parameters that control the XGBoost algorithm:
* learning rate (aka eta) - controls the rate at which the feature weights are shrunk at each boosting step
* gamma - minimum loss reduction needed to split a leaf node
* max_depth - maximum depth of a tree
* regularization alpha - L1 regularization term for weights
* regularization lambda - L2 regularization term for weights

These cells work by setting up an `objective_function` that fits a model
using supplied parameters drawn from the search space and returns an objective
metric. In this case we use the area under the ROC curve; since we are trying
to _minimize_ loss the objective function returns (1 - roc_auc).

The `search_space` dictionary establishes the space to search for each
parameter of interest, using the `hyperopt` sampling methods. A `hp.quniform`
sample is uniformly drawn from the given min and max, quantized to the `q`
parameter: `hp.quniform('max_depth', 4, 100, 1)` returns a sample drawn
uniformly from the range \[4, 100\] and rounded to the nearest integer.
The `hp.loguniform` samples are drawn such that the _log_ of the return
value is uniformly distributed. This has the effect of sweeping across
multiple orders of magnitude, e.g., `hp.loguniform('gamma', -3, 0)`
samples from [0.001, 0] such that exp(val) is uniformly distributed.
 
## Run hyperparameter search and train "best" model

Note that the previous cell merely defined the `hyperopt` objective function
and search space, but did not perform the search. In this cell we do so, 
following a two-phase process. In the first phase, we run 100 iterations
of the `hyperopt` search. At the conclusion of this phase, the variable
`best_hyperparam` is a dictionary with the parameters for the "best"
performing model, according to our evaluation metric (here, area under ROC curve). 

In the second phase, we use those parameters to train a cross-validated model
using a 5-fold split and area under P-R curve as our evaluation metric. This
final model is then evaluated on the test data split and all the evaluation
metrics are computed and saved.

NB. There is a potential error in the parameter calculations in the current 
version of this notebook (which were copied from the Logistic Regression 
notebook). Specifically, accuracy, precision, recall, F1 and F2 scores are 
guarded by a catch-all `except` clause; the intention is primarily
to trap cases where a divide-by-zero would occur, but it will also trap
*any* error and silently return a 0 for that value. (This was noticed
after the runs were complete in MLflow, and so those runs were saved
with zeroes for F1 and F2, due to a silently-missing definition for
`Fbeta`. The correct scores were computed post-hoc and are found on
the model card.)

As part of the evaluation, this cell also computed and saves the Brier scores
(both overall and by subgroup), the SHAP summary plot, and SHAP
interaction plots for the top three interacting SHAP features. (The
specific plots shown in the worksheet will vary based on the most recent
run.) 

## Additional SHAP Plots

Two additional SHAP plots are also included at the bottom of this worksheet,
to illustrate some ways in which the SHAP tools can help explore the model's
output.

The first plot, a force plot, shows the relative impact of each feature
on a particular example's classification. Blue chevrons indicate where lower
values of features push the model output, and red chevrons indicate the impact
of higher-valued features.

The second plot, a decision plot, is a different visualization of the same
information; it presents the highest impact features as a "path" followed to the final model output value.

CAUTION: These plots are derived from a single instance in the input data
and so the CMS Cell Size Policy _may_ apply for uses outside model development in the VRDC.

