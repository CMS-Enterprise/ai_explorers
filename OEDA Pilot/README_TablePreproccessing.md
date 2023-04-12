# Table Preprocessing

This README file describes the data preprocessing performed
as part of the OEDA AI Explorers pilot project, and is intended to
accompany the tables_preprocess_updated notebook 
originally developed in the CCW VRDC environment. It depends on 
the data tables and resources deployed there.

## Preprocessing Overview

Preprocessing consists of several steps:
- One-hot encoding categorical variables (see the one_hot_encoder notebook) -- these tables are also saved for use as non-resampled inputs
- SMOTE oversampling
- (optionally) Undersampling using either the SMOTEENN (edited nearest neighbor) or Tomek methods.
- Writing the resampled data frames to tables for reuse.

Each of these steps is described in more detail below.

## One-hot encoding

The first cells run (import) the one_hot_encoder notebook to use a
consistent one-hot encoding method and ordering of fields. The details
of that encoder are described with it. In this notebook we use a modified
version of the `CMSPyTorchDataset` class used by the experimental model;
its main variation is that it produces a Pandas DataFrame instead of
a PyTorch vector dataset. This simplifies the remaining preprocessing
steps in this notebook.

After defining the encoder class, we apply it to our two input datasets
(the "TSFRESH" and "Abbridged TS Features" datasets) to produce one-hot
encoded DataFrames, which are then saved as Databricks tables. 

## SMOTE Oversampling / ENN and Tomek Undersampling

To correct for class imbalance, we apply SMOTE. Because our dataset includes many categorical variables, we can't apply plain SMOTE (or Approx-SMOTE, in its current implementation). We use SMOTENC from the `imbalanced-learn` library, which is designed to handle a mix of categorical and numeric variables.

We also optionally apply the Tomek's Links or ENN (Edited Nearest Neighbor) 
undersampling methods to remove samples from the majority class. They have 
slightly different strategies for removing samples, which can result in 
slightly different boundary tradeoffs in models trained from them.

More details of the SMOTE/SMOTE-NC, Tomek's Links, and ENN methods can
be found in the project technical report.

Note that `imblearn` is not Spark-aware, so the actual fit/resample step will run on the driver node, not the cluster worker nodes. This is extremely
compute-intensive and will take many hours to complete.

The bulk of the work in this notebook is done in this final cell, which
applies SMOTE-NC, and optionally one of ENN or Tomek's Links, to the training split of both of the one-hot encoded input tables. It then saves the resulting
resampled data to a new table, appending descriptive suffix to identify which
preprocessing was applied. To produce the resampled tables used in the model
development, this cell was run three times (each possible combination of
SMOTE-NC and undersampling) to produce six tables (TSFRESH and Abridged 
features for each combination).  The table names with their configurations
are summarized in the project technical report, as well as in a table
in the DistXGBoost notebook (which itself was not used in the final 
model runs).

One variation that was not tested due to time constraints is undersampling
 _without_ oversampling -- that is, only applying ENN or Tomek's Links
 editing. This could be done by modifying the processing code notionally
 as follows:
 ```
 from imblearn.under_sampling import EditedNearestNeighbors
 from imblearn.under_sampling import TomekLinks
   .
   .
   . 
   # omit SMOTE
   # smote = SMOTENC(random_state=2143, categorical_features=cat_cols)
   sme = TomekLinks() # or EditedNearestNeighbors()
   print('Starting resample...')
   start = time.time()
   X_res, y_res = sme.fit_resample(X, y)
   .
   .
   .
```
