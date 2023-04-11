# **HAIP Code Repo**
Included is the cleaned code repository for the HAIP project. Developed by iAdeptive Technologies, 2023.

**Project Status:** Pilot is completed.

## **Tech / Frameworks used**

HAIP codebase primarily utilizes Python with AWS s3 storage. Exploratory Data Analysis notebooks are ran in R. The `xgboost`, `scikit-learn`, and `plotnine` Python libraries are used extensively.

## **Code Layout / Organization**

Code is organized in the structure below: 
```
/measures/
- op-21 
- op-22
- op-23
- pc-01
- sep-01

/notebooks/
- exploratory
- op-10

/services/
- artificial_anomaly_tests
- data_consolidation
- ensemble_model
- feature_engineering
- final_fitting
- model_dataset
- model_selection
- model_training
- outcome_analysis
- sharepoint_transfer
```

**Notebooks for individual measures**  are included in the  `/measures/` directory. The exception to this is OP-10 notebooks, included in `/notebooks/op-10`.

**Exploratory data analysis notebooks** are included in the `/notebooks/exploratory/` directory. 

**Data and modeling infrastructure** is included in the `/services/` directory. Services modules are organized in the following way:

**`/services/artificial_anomaly_tests`**
Conducts the artificial anomaly tests for both the xgboost and isolation forest models

**`/services/data_consolidation`**
Consolidates data from AWS S3 buckets

**`/services/ensemble_model`**
Trains and fits ensemble model

**`/services/feature_engineering`**
Adds feature engineering to create lags, differencing, and provider level means

**`/services/final_fitting`**
Conducts final fitting for XGBoost and Isolation Forest models

**`/services/model_dataset`**
Loads modeling dataset

**`/services/model_selection`**
conducts model selection

**`/services/model_training`**
Conducts model training and hyperparameter tuning for all three models

**`/services/outcome_analysis`**
generates a results summary notebook

**`/services/sharepoint_transfer`**
Transfers data from sharepoint

## **Usage**

Upon creating a measure directory, copy the two notebooks below from another measure. Change the applicable settings in the start of the notebook to load the correct measure.

**`explore_opXX_data[r].ipynb`**
This notebook runs in R and conducts the exploratory data analysis and time series analysis.

**`run_services_opXX.ipynb`**
This notebook runs in Python and executes the modeling pipeline. It will output `outcome_analysis_opXX.ipynb` as well as generate a `models` folder to store model run information. 