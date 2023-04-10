# WETG-AI Exploration Pilot Introduction
This pilot was introduced to explore AI and Maching Learning capabilities in the automation of bug identification across the software development lifecycle. This pilot was then executed by training models utilizing natural language processing on the description of closed jira tickets that identified as bugs and have corresponding GitHub commits.

## WETG AI Architecture Diagram
<img src="0_images/WETG-architecture-diagram.PNG" alt="WETG-AI Infrastructure" width="500" height="400">

## Prerequisites
- Sufficient Jira stories for bugs that are well-documented with abundant information
- GitHub commits linked to those Jira stories
- An environment where we can train, run, and test ML models
- Several advances in pretrained models for natural language processing

## Pilot Scope
- [X] Set up infrastructure in the PWSS AWS account (ec2, s3, RDS, EBS)
- [X] Use open-source machine learning libraries to train the models (TF/IDF, SimpleTransformers, JupyterHub)
- [X] Extract and analyze data from the Jira and GitHub projects of CCXP/MCT
- [X] Train, evaluate, and refine machine learning models

<!-- Getting Started-->
# Getting Started
Instructions on running code locally <strong>or</strong> in AWS instance

## Setup Guide
![Python](https://img.shields.io/badge/-Python-black?style=flat-square&logo=Python)
![Amazon AWS](https://img.shields.io/badge/Amazon%20AWS-232F3E?style=flat-square&logo=amazon-aws)
![GitHub](https://img.shields.io/badge/-GitHub-181717?style=flat-square&logo=github)

### 1. Running WETG-AI Code on an AWS Instance
Reference the Input data section below for detail on running the code on an AWS instance.

### 2. Running WETG-AI Code Locally
##### Python / Anaconda Setup
  1. Download latest version of python from [here](https://www.python.org/downloads/)
<strong>or</strong>
  2. Download the latest version of [Anaconda](https://www.anaconda.com/)
###### Library Installation </strong>
Below shows the code to install required libraries through your command line. 
- Note: As a form of best practices, activate a [virtual environment](https://docs.python.org/3/tutorial/venv.html)

- Create Virtual Environment
  ```sh
  conda create -n st python pandas tqdm
  conda activate st
  
- PyTorch (CPU Only)
  ```sh
  conda install pytorch -c cpuonly 
  
- PyTorch (GPU- recommended) Note: verify cuda usage when the model is created.
  ```sh
  conda install pytorch>=1.6 cudatoolkit=11.0 -c pytorch
  
- Transformers
  ```sh
  conda install Transformers 
  
- Simple Transformers
  ```sh
  conda install simpletransformers
  
##### Local Git Setup
###### Git Setup 
  - Download and install the latest version of [Git](https://git-scm.com/downloads)
  - [Git Setup](https://docs.github.com/en/get-started/quickstart/set-up-git)

###### (Alternative) GitHub Desktop
  - Download GitHub Desktop if you do not want to use command line.
  - [GitHub Desktop Guide](https://docs.github.com/en/desktop/installing-and-configuring-github-desktop)
  - Note: You must have Git installed before using GitHub Desktop
    - [Configuring Git for GitHub Desktop](https://docs.github.com/en/desktop/installing-and-configuring-github-desktop/configuring-and-customizing-github-desktop/configuring-git-for-github-desktop) 
 
#### Git Clone and Fork
- You can clone or fork a repository with GitHub Desktop to create a local repository on your computer. 
  - [Clone and Fork GitHub Desktop](https://docs.github.com/en/desktop/contributing-and-collaborating-using-github-desktop/adding-and-cloning-repositories/cloning-and-forking-repositories-from-github-desktop)

# Prototype Guidelines
## Script Usage and Replicability Guidelines
These scripts should be used to run the WETG Multilabel Classification Models on CCXP and MCT. This process should not be replicated for the purpose of implementation but to validate the results of the WETG AI Exploration Pilot. Requirements for implementation are based on the determination of acceptable MLOps maturity, system security and enclosure, setup and configuration within the CMS Github Enterprise.

This code should not be replicated based on an assumption not explicitly stated or utilized for any purpose outside of the intent of the research defined by the scope of this pilot's purpose or a purpose which has not been explicitly identified as an official policy and/or authorization by CMS, HHS, or an auditing body for official or unofficial use.

## Standard File and Script Naming Conventions:
- Current Script Naming Standards: [Project]_[Model Version/Type]_[WETG_ML_BUG_AUTO]_[Pretained Model Name]_MODEL
- Mature and Scalable Naming Standards (Future Reference): Each classification component, version, and date within the filing naming convention will become a numerical identifier and tracked in a centralized file or database at the point these operations are determined well-documented, repeatable and optimized. 

# Input Data
## Type of input data
- Export of Jira tickets from search result using criteria "project = CCXP AND issuetype = Bug", or "project = MCT AND issuetype = Bug", respectively
- Assessment for completeness of required information in exported Jira tickets
- List of files changed in commits of CMS Github associated with each exported Jira ticket (when applicable)
## Location of Input Files
- AWS S3 Bucket: gov-cms-ai-dev/
- [CMS WETG-AI-ML Input Data- CCXP and MCT](https://github.cms.gov/CVPWQC/WETG-AI-ML/tree/main/1_data/1a_github_commit_input)
  - [Quality Assurance Input Data](https://github.cms.gov/CVPWQC/WETG-AI-ML/tree/main/1_data/1b_quality_assurance_input)
- RDS MySQL Database <br />
&nbsp; &nbsp; &nbsp; HOST: ai-dev-db.cnpvesc495sx.us-east-1.rds.amazonaws.com <br />
&nbsp; &nbsp; &nbsp; DB Name: aidevdb

# Model Analysis
## Historical Experimentation
- TF/IDF (term frequency–inverse document frequency) to classify the repo/path to files referenced
- TF/IDF to classify the repo/path to files referenced with the non-core repos (e.g., QA) removed
- Use RoBERTa modify to generate embedding from issue description, then classify filepath and name
- Use RoBERTa modify to generate embedding from issue description, then classify filepath with only folders (no file name)
- Cluster the files into ones modified together, then try one of the above strategies to predict the cluster

## Pilot Findings
- The WETG Team trained and test dozens of ML models using data from CCXP and MCT.
- The models can predict the folders that contain the files with bugs based on text from Jira.
- The models have good results but a strong bias. The LRAP (Label ranking average precision) for the models was 0.8 for the MCT repo and 0.5 for the CCXP repo.
- The confusion matrices show that while the LRAP value is high, the model bias is also significant. The model leans towards predicting that bugs are in popular folders. 
- The model bias likely originates from not enough Jira tickets (small training set) and the description of the JIRA tickets not written with enough details (inconsistent / low quality data/ not explicit).

### Model Capabilities
These models are capable of classifying the bug issues to the corresponding file folders on previously closed jira instances for the following directories:
CCXP:
  1. 'server': ccxp-server/src
  2. 'data' ccxp-data/src
  3. etl': ccxp-etl/src
  4. 'pcompare':ccxp-client/libs/features/provider-compare/
  5. 'pdetails':ccxp-client/libs/features/provider-details/
  6. 'psearch': ccxp-client/libs/features/provider-search/
  7. 'pmeasures': ccxp-client/libs/features/provider-measures/
  8. 'apps': ccxp-client/apps
  9. 'cl_core': ccxp-client/libs/core

MCT:
  1. 'otherpages': src/pages/
  2. 'enrollmentformpage': src/pages/EnrollmentFormPage/
  3. 'manageprescriptionspage': src/pages/ManagePrescriptionsPage/
  4. 'pharmacyselectionpage': src/pages/PharmacySelectionPage/
  5. 'plancomparisonpage':  src/pages/PlanComparisonPage/
  5. 'plandetailspage': src/pages/PlanDetailsPage/
  6. 'questionroutingpage': src/pages/QuestionRoutingPage/
  7. 'searchresultspage': src/pages/SearchResultsPage/
  8. 'styles': src/styles
  9. 'components': src/components/
  10. 'app': src/app/
  11. 'types': src/types/
  12. 'translations': src/translations/
 
 Please reference models results below to further assess model capabilities.

### Model Limitations
1. These models do not utilize multilingual nlp pretrained models and require multilingual-base to accomodate data in non-English languages
    such as Spanish.
3. There has not been a risk assessment performed around the utilization of open-source Machine Learning libraries (Hugging Face).
4. These models account only for algorithmic bias and do not account for racial or regional bias.
5. These models do not account for security protocols required for implementation to ensure the full protection of pii/phi, and system 
   viability to support an agile model.
7. These models did not incorporate machine learning predictability on the entire dataset and require assumptions to be validated by the
    DevOps team.
9. These models are further limited by the quality of data and required improvements in data quality. Please reference quality assurance models
    to analyze the differences between actual models and models with quality improvements.

### Evaluation
#### Evaluation Definitions:
- LRAP: Label ranking average precision (LRAP) is the average over each ground truth label assigned to each sample, of the ratio of true vs. total labels with lower score.This metric is used in multilabel ranking problem, where the goal is to give better rank to the labels associated to each sample.
- Evaluation Loss: Evaluation loss (also called validation loss) is the loss calculated between the true labels and the predicted labels for the evaluation.
- Bias: Bias describes how well the model matches the training dataset. A model with high bias won’t match the data set closely, while a model with low bias will match the data set very closely.The model bias is calculated and evaluated through the incorporation of confusion matrices.
  - Confusion Matrices: A performance measurement for machine learning classification which is a table that consists of 4 different combinations of predicted and   actual values.
- Quality assurance indicator:
  WETG's QA Team devised seven QA indicators to quantify the quality of bug tickets to be filtered, utilized, and compared with the original model 
  results and bias.The WETG QA Team measured the quality by calculating the sum of each QA Indicator for CCXP and MCT by creating columns for each 
  QA Indicator across Jira bug ticket data and calculated indicator presence by utilizing binary numbers (1= Present & 0= Not Present). These QA 
  indicators allowed room for variation as the WETG QA team noticed differences in terminology across timelines and project teams when populating
  Jira bug tickets.
  QA Indicators:
  - Steps to Reproduce
  - Expected Outcome (Results, Behavior, Functionality)
  - Actual Outcome
  - Source URLs
  - Browsers
  - Development Environments (Custom Field)
  - Images/videos in description (Custom Field)

#### Final Model Results and Bias Assessment
#### 1. CCXP
- [CCXP Model](https://github.cms.gov/CVPWQC/WETG-AI-ML/blob/main/2_model/CCXP_FINAL_WETG_AI_ML_BUG_AUTO_RoBERTa_MODEL.ipynb)
- Model Results
  - a. LRAP: 43.38%
  - b. Evaluation loss: 46.84%
  - c. Bias: High
 
-  [CCXP Quality Assurance Models](https://github.cms.gov/CVPWQC/WETG-AI-ML/tree/main/2_model)
    1. [CCXP Model which utilizes data (jira tickets with commits) with >1 quality assurance indicator](https://github.cms.gov/CVPWQC/WETG-AI-ML/blob/main/2_model/CCXP_QA1_WETG_AI_ML_BUG_AUTO_RoBERTA_MODEL.ipynb)
      - LRAP: 53.16%
      - Evaluation Loss: 45.62%
    2.  [CCXP Model which utilizes data (jira tickets with commits) with >2 quality assurance indicator](https://github.cms.gov/CVPWQC/WETG-AI-ML/blob/main/2_model/CCXP_QA2_WETG_AI_ML_BUG_AUTO_RoBERTa_MODEL.ipynb)
      - LRAP: 59.65%
      - Evaluation Loss: 48.50%
    3.  [CCXP Model which utilizes data (jira tickets with commits) with >3 quality assurance indicator](https://github.cms.gov/CVPWQC/WETG-AI-ML/blob/main/2_model/CCXP_QA3_WETG_AI_ML_BUG_AUTO_RoBERTa_MODEL.ipynb)
      - LRAP: 42.38%
      - Evaluation Loss: 53.57%
    4. [CCXP Model which utilizes data (jira tickets with commits) with >4 quality assurance indicator](https://github.cms.gov/CVPWQC/WETG-AI-ML/blob/main/2_model/CCXP_QA4_WETG_AI_ML_BUG_AUTO_RoBERTA_MODEL.ipynb)
      - LRAP: 46.66%
      - Evaluation Loss: 52.96%

#### 2. MCT
- [MCT MODEL](https://github.cms.gov/CVPWQC/WETG-AI-ML/blob/main/2_model/MCT_FINAL_WETG_AI_ML_BUG_AUTO_RoBERTa_MODEL.ipynb)
  - a. LRAP: 59.52%
  - b. Evaluation Loss: 47.98%
  - c. Bias: High
 
- [MCT Quality Assurance (This model utilizes tickets with >2 QA indicators)](https://github.cms.gov/CVPWQC/WETG-AI-ML/blob/main/2_model/MCT_QA2_WETG_AI_ML_BUG_AUTO_RoBERTa_MODEL.ipynb) 
  -   LRAP: 59.517%
  -   Evaluation Loss: 47.98%

# Action Items
## Next Steps
- Acquire more data

## Implementation Requirements
- Run environmental scans and enable code scanning 
- Ensure PII/PHI is not in GitHub Environment.

### Considerations
- Consider separating bug tickets related to software development and design vs. data handling/ databases/ ETL to minimize the risk of sensitive data exposure or database exposure to malicious code/software.
- Develop environmental and sustainability considerations

## Machine Learning Operations (MLOps) Maturity Model
0. Level Zero: No Operations <- We are here
1. Level 1: Manual ML pipeline 
2. Level 2: Automated Training
3. Level 3: Automated Model Deployment
4. Level 4: Full MLOps Automated Training

# References
<strong> DevOps References </strong>
- [WQC Confluence Page](https://confluence.cms.gov/display/CLDBEESJENKINS/WQC+DevOps)
- [WETG Points of Contact Information](https://confluence.cms.gov/display/WETGA/WETG+Accounts)
- [CCXP Points of Contact Information](https://confluence.cms.gov/display/CCXP/Team+Roster)
- [MCT Product Team Contact Information]

<strong> Reference for this Pilot </strong>
- [Simple Transformers.ai](https://simpletransformers.ai/)
- [Hugging Face Models](https://huggingface.co/models)
- [CCXP- Care Choice Experience Confluence Page](https://confluence.cms.gov/display/CCXP/Care+Choice+Experience++Home)

<strong> Infrastructure, System Security, Compliance References </strong> 
- [GitHub Code Scanning](https://docs.github.com/en/code-security/code-scanning)
- [GitHub Code Security Guide](https://docs.github.com/en/code-security/guides)
- [White House Blue Print AI Bill of Rights](https://www.whitehouse.gov/ostp/ai-bill-of-rights/)
