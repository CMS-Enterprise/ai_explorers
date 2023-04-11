# Steps to generate OIE model

1. `01-combine-oie-dataset.flow` imports all oie csv datasets in s3.
    Run the flow and export the data to s3.
    Download (or move) the csv, reupload to `haip-dev-training-dataset` in s3, and rename the file to `oie_historical_dataset.csv`.
    
2. 