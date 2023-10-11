# RDS AI Explore Initiative - CM Pilot
This repository contains codes, notebooks and configurations used in the development of the RDS AI Explore Initiative, CM Pilot. For more information about this pilot, check out the [confluence space](https://confluenceent.cms.gov/display/APP/CM+Pilot).

The goal of CM Pilot is to develop a POC that can identify topics, analyze sentiments and identify trends.

- `.gitignore` - This file contains a list of patterns and rules that specify which files and directories should be ignored by GIT when tracking changes or from version control and making commits.

- `buildTrainData.ipynb` - This script builds data to train custom classification model in comprehend. The training files are picked in such a way that they represent the topics accurately.The messages with the highest confidence (probability) values and more number of keywords (topic-terms) are selected. The confidence and terms are obtained from previous unsupervised model run. Also, the messages which were originated from CMS RDS Center are not considered.

    Prerequisites: Run/root/comp_predictions/training_data.sh first (This script collects messages with highest confidence scores).

- `emailClean.ipynb` - This script contains codes for processing, analyzing and cleaning up email messages.

- `realTime.ipynb` - This script predicts the topic **category** and **sentiment** in real time for the latest email message received in S3. The script uses the trained custom classification model, `Topic ClassifierSept7` for the predictions.
The follopwing are the steps in detail:
    - Step 1: Retrieve the latest message posted on S3 in "pro-rds-emails" bucket under Inquiry/THOR/or thor/foldres.
    - Step 2: Extract body, subject and fromEmailId and strip the html tags off the body.
    - Step 3: Find out if the email is one of the types: 
        (a) Out Of Office (OOO),
        (b) Undeliverable,
        (c) Volunteer messages.
    If so, update the email_type as 'OOO', 'VOLUNTEER' or "UNDELIVERABLE', and email_status as 'P' in the PostgreSQL database table and exit the loop.
    - Step 4: Run cleanup functions to remove name signature organizations, locations, phone numbers, URLs, punctuations, salutations etc.

- `timeseriesProjection.ipynb` - This script contains the codes for time series analysis.

- `TopicSentiPlot.ipynb` - This script contains the codes for topic sentiment analysis.

- `wordcloud_all.ipynb` - This script contains the codes for topic analysis.