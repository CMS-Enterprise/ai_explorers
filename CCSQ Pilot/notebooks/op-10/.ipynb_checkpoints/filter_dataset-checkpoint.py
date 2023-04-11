import pandas as pd
import numpy as np

def filter_data(full_data_path):
        full_dataset = pd.read_csv(full_data_path)

        full_dataset['measureId'].unique().sort()
        full_dataset['measureId'].unique()

        measure_dataset = full_dataset[full_dataset['measureId'] == 'measure']
        #Drop ProviderId NA values
        measure_dataset = measure_dataset.dropna()
        measure_dataset['year'].value_counts()

        #Drop ProviderId NA values
        measure_dataset = measure_dataset.dropna()

        measure_dataset = measure_dataset.filter(items=['providerId', 'score','measureEndDate'])

        measure_dataset['y_quarter']=measure_dataset['measureEndDate'].str[0:10]
        measure_dataset['y_quarter']=pd.to_datetime(measure_dataset['y_quarter'])

        measure_dataset['y_quarter'] = measure_dataset['y_quarter'].dt.to_period('Q')
        measure_dataset = measure_dataset.drop_duplicates()

        measure_dataset = measure_dataset.sort_values(by=["providerId", "y_quarter"])

        measure_dataset['lag1'] = measure_dataset.groupby(['providerId'])['score'].shift(1)
        measure_dataset['lag2'] = measure_dataset.groupby(['providerId'])['score'].shift(2)

        measure_dataset = measure_dataset.drop(columns = ['measureEndDate'])
        measure_dataset['year'] = measure_dataset['y_quarter'].apply(lambda x : x.year)
        measure_dataset['quarter'] = measure_dataset['y_quarter'].apply(lambda x : x.quarter)
        measure_dataset

        measure_dataset.to_csv('../tmp/measure_dataset.csv', index = False)