# OHC Time to Hire Calculator
This repository contains code, notebooks, and configurations used in the development and deployment of the OHC Time-to-Hire Calculator during the CMS AI Explorers OHC AI Pilot. For more information about this pilot, check out the [Confluence space](https://confluenceent.cms.gov/pages/viewpage.action?pageId=329228032).

The goal of this pilot was to explore the development of machine learning models using historical hiring data to make better decisions about hiring timelines and to find ways to operationalize these models and serve them in a user-friendly interface.

# Overview of the folder structure
This repository is organized as follows:

- ai-explorers-submission-deprecated: the original AI Explorers submission that lead to this pilot
- aws-deployment: code for AWS Lambda functions and scripts for creating IAM roles
- dashboard: the OHC Time-to-Hire Calculator user interface
- datasets: "raw" and "transformed" datsets used in model training and by the user interface
- etl: scripts used to transform datasets
- notebooks: Jupyter notebooks used for model training and evluation
- statistical-analysis: content about multimodal analysis

# Instructions on how to run the ETL

Prerequisites: Python 3.6 or greater

1. Clone this repository
2. In your terminal or IDE of choice, navigate to the cloned repository's folder
3. Navigate to the `etl/` folder
4. Open desired Python script or Notebook
5. Update paths to raw and clean files as needed and save
6. Execute script to process files
7. Review output

# Running the Dash App

Prerequisites: Python 3.6 or greater

1. Clone this repository
2. In your terminal or IDE of choice, navigate to the cloned repository's folder
3. (Recommended) Create and enter a [virtual environment](https://docs.python.org/3/library/venv.html)
4. Install the local dependencies with the following command (exact syntax may vary):

`pip install -r requirements.txt`

5. To start running the UI, enter the command (exact syntax may vary):

`python dashboard\app.py`

6. In your web browser, visit http://127.0.07:8050/ or http://localhost:8050/

# Model Notebooks

Each notebook provides a detailed walkthrough of the generation of models, model performance, logs, and model packaging. Run each cell in the notebook from top to bottom to follow the development workflow.

1. Clone this repository
2. Install dependencies

`pip install -r requirements.txt`

3. Navigate to the `notebooks/` folder

### Folder Contents

* `Certificate Hire Model Notebooks/` contains python notebooks for developing models retaining to the Certificate Data
  * To generate models, run the _**Deployment**_ cell block after all the cells above are ran.
* `Time to Hire Model Notebooks/` contains python notebooks for developing models retaining to predicting the hiring timeline
  * To generate models, run the _**Deployment**_ cell block after all the cells above are ran.
* `Exploratory Model Notebooks/` contains python notebooks each implementing different regression and classification models for model comparisons

**Output Locations**

* `Models/` contains packaged models that were trained
* `logs/` contains logs of model performance metrics
