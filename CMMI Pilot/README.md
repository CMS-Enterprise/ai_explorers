# The CMMI AI Explorer Pilot Project

## **Project Objective**
The CMMI Artificial Intelligence Explorer Project is a proof-of-concept pipeline showcasing how AI/ML can be implemented at a large-scale in CMS systems to predict clinical outcomes. We used "unplanned inpatient admission" as a notional prediction target.

## **Organization of This GitHub Repository**
- The `sql_code` folder contains a csv file of SQL code used to query data in Snowflake
- The `notebooks` folder contains Jupyter Notebook versions of the core source code and provides step-by-step guidance through the modeling pipeline. 
- The `technical_setup` folder contains documentation on how to connect to the environment and access data and package installation language

    
## **Technical Set-up**
### Connecting to the EC2 instance and IDR Cloud:
The `end_user_connection.md` file provides options for how to obtain necessary access and connect to the environment and data
### Installing Specified Packages:
The `model_test_requirements.txt` and `snowflake_pull_requirements.txt` files list all required python libraries and can be installed using the following command: 
```
pip install -r requirements.txt
```

## **Overview of Notebooks**
- `cohort_outcome_clinical_element_selection.ipynb`
    - Prerequisites and accessing the data: necessary packages and connecting to the IDRC through a snowflake connector
    - Cohort selection: defines the relevant population for the analysis in terms of beneficiary characteristics (e.g., demographics or clinical characteristics) and time frame
    - Target outcome definition: defines the clinical outcome that will be predicted (that is, unplanned inpatient hospitalization occurring within 3 months)
    - Data extraction: extracts the relevant Medicare FFS claims data from the IDR Cloud (i.e., variables used to predict the target outcome, such as diagnoses, procedures, medications) and converts the data into tables of selected clinical elements
- `modeling_and_evaluation.ipynb`
    - Data analysis: exploratory analysis to understand data distributions, identify outliers, and aid in data cleaning
    - Feature engineering: reads in extracted data and condenses the demographic and clinical elements into a set of features to be used for prediction
    - Model selection and training: building, training, and fine-tuning of machine learning models to predict clinical outcomes
    - Model testing and evaluation: analysis of the resulting predictions 


