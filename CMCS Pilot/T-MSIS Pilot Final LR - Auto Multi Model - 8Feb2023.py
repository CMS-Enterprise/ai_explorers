# Databricks notebook source
import pyspark
from pyspark.sql.functions import col
from pyspark.sql.functions import count
import sklearn
import databricks.automl
import logging
from databricks import automl
import mlflow
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
# To supress warnings
import warnings
warnings.filterwarnings("ignore")
logging.getLogger("py4j").setLevel(logging.WARNING)
logging.getLogger("py4j").setLevel(logging.WARNING)

def get_experiment_name(expr_string):
    experiment_list = str(expr_string).replace('\n',' ').split(',')
    for name in experiment_list:
        if 'mlflow.experiment.sourceName' in name:
            #print(name)
            experiment_name = name.split(":",1)[1]
            return experiment_name

def get_date_int(in_date):
    return int(str(in_date).split('-')[2])
  

def get_date_text(in_date):
    return str(in_date)

def run_multi_liner_regression(train_pdf,train_pdf_work,test_pdf,process_type,state_numeric,state_alpha,file,run_nbr):
    
    test_pdf['date_int'] = test_pdf.daily_rep_pd_date.apply(get_date_int)
    train_pdf['date_int'] = train_pdf.daily_rep_pd_date.apply(get_date_int)
    train_pdf_work['date_int'] = train_pdf_work.daily_rep_pd_date.apply(get_date_int)
    summary = automl.regress(train_pdf_work, time_col="daily_rep_pd_date", target_col="errs", timeout_minutes=120)
    best_model = summary.best_trial.model_description
    training_score = summary.best_trial.metrics['training_r2_score']
    validation_score = summary.best_trial.metrics['val_r2_score']
    test_score = summary.best_trial.metrics['test_r2_score']

    model_uri = summary.best_trial.model_path

    # Prepare test dataset
    y_test = test_pdf["errs"]
    X_test = test_pdf.drop("errs", axis=1)

    # Run inference using the best model
    model = mlflow.pyfunc.load_model(model_uri)
    predictions = model.predict(X_test)
    

    test_pdf["errs_predict"] = predictions
    test_pdf['errs_predict'] = test_pdf['errs_predict'].astype('int64')
    
    test_pdf['file_type'] = file
    test_pdf['state_code_numeric'] = state_numeric
    test_pdf['state_code_alpha'] = state_alpha
    test_pdf['date_text'] = test_pdf.daily_rep_pd_date.apply(get_date_text)

    test_pdf['model_score_train'] = training_score
    test_pdf['model_score_validate'] = validation_score 
    test_pdf['model_score_test'] = test_score

    test_pdf['model_parent_process'] = 'AutoML-Regress ML'
    test_pdf['model_name'] = best_model
    test_pdf['score_type'] = 'r2'
    test_pdf['errs_predict'] = test_pdf['errs_predict'].astype('int64')

    test_pdf["best_model_url"] = summary.best_trial.notebook_url
    test_pdf["experimant_info"] = get_experiment_name(str(summary.experiment))
    test_pdf["model_run_num"] = run_nbr
    test_pdf['model_run_type'] = 'D - LR - Auto Multi-Model'
    test_pdf['comments'] = process_type
    test_pdf['source_data_table_name'] = ' '
    
    test_pdf['errors_actual_previous_mo'] = 0
    test_pdf['mo_to_mo_difference'] = 0
    
    test_pdf['errors_actual_previous_mo'] = 0
    test_pdf['errors_actual_previous_mo'] = test_pdf['errors_actual_previous_mo'].astype('int64')
    test_pdf['actual_to_predicted_difference'] = 0
    test_pdf['source_notebook_url'] = ' '
    test_pdf['actual_to_predicted_pct'] = 0
    test_pdf['experiment_info'] = ' '
    test_pdf['mo_to_mo_pct'] = 0
    
    test_pdf.rename(columns={'errs': 'errors_actual_current_mo', 'errs_predict': 'errors_predicted_current_mo'}, inplace=True)
    test_pdf['model_score_forecast'] = 0
    test_pdf['absolute_difference'] = 0
    
    return_df=test_pdf[['model_run_type','model_run_num','state_code_numeric','state_code_alpha','daily_rep_pd_date','date_text','date_int','file_type','errors_actual_previous_mo','errors_actual_current_mo','mo_to_mo_difference',	'mo_to_mo_pct','errors_predicted_current_mo','actual_to_predicted_difference','absolute_difference','actual_to_predicted_pct','model_parent_process','model_name','score_type','model_score_forecast','model_score_train','model_score_validate','model_score_test','source_notebook_url','best_model_url','experiment_info','source_data_table_name','comments']]
    
    spark_return_df = spark.createDataFrame(return_df) 
    spark_return_df.write.saveAsTable("datalab_scratch.lr_multi_test_forecast_1_kv",mode="append")
    
    train_pdf['model_run_type'] = 'D - LR - Auto Multi-Model'
    train_pdf['file_type'] = file
    train_pdf['state_code_numeric'] = state_numeric
    train_pdf['state_code_alpha'] = state_alpha
    train_pdf['comments'] = process_type
    train_pdf['model_run_num'] = run_nbr
    train_pdf['errs'] = train_pdf['errs'].astype('int64')
    
    return_train_pdf = train_pdf[['model_run_type','model_run_num','state_code_numeric','state_code_alpha','daily_rep_pd_date','date_int','file_type','comments','errs']]
    spark_train_pdf = spark.createDataFrame(return_train_pdf) 
    spark_train_pdf.write.saveAsTable("datalab_scratch.lr_multi_train_forecast_1_kv",mode="append")
    
    
def get_train_and_test_df(table_name):
    query_1 = "select * from " + table_name + " where daily_rep_pd_date >= '2022-01-01' AND daily_rep_pd_date <= '2022-01-18'"
    query_2 = "select * from " + table_name + " where daily_rep_pd_date >= '2022-01-19'"
    
    train_df = spark.sql(query_1)
    train_pdf = train_df.select("*").toPandas()
    
    test_df = spark.sql(query_2)
    test_pdf = test_df.select("*").toPandas()
    
    return train_pdf, test_pdf

def treat_outliers(df, col):
    """
    treats outliers in a variable
    col: str, name of the numerical variable
    df: dataframe
    col: name of the column
    """
    Q1 = df[col].quantile(0.25)  # 25th quantile
    Q3 = df[col].quantile(0.75)  # 75th quantile
    IQR = Q3 - Q1                # Inter Quantile Range (75th perentile - 25th percentile)
    lower_whisker = Q1 - 1.5 * IQR
    upper_whisker = Q3 + 1.5 * IQR

    # all the values smaller than lower_whisker will be assigned the value of lower_whisker
    # all the values greater than upper_whisker will be assigned the value of upper_whisker
    # the assignment will be done by using the clip function of NumPy
    df[col] = np.clip(df[col], lower_whisker, upper_whisker)

    return df

#drop result table
try:
  spark.sql("drop table datalab_scratch.lr_multi_train_forecast_1_kv ")
except Exception as e:
  print(f"Table does not esist")
  print(e) 

try:
  spark.sql("drop table datalab_scratch.lr_multi_test_forecast_1_kv ")
except Exception as e:
#except:
  print(f"Table does not esist")
  print(e) 

state_df_spark = spark.sql("select * from datalab_scratch.state_codes where state_code_numeric in ('29', '44') order by State_Code_Numeric")
state_df = state_df_spark.toPandas()
file_list = ['ELG','PRV','MCR','TPL','CIP','COT','CLT','CRX']
process_type_list = ['Features/Processing: submission_methods','Features/Processing: submission_methods_with_outlier_treatment','Features/Processing: error_category','Features/Processing: error_category_with_outlier_treatment']
run_nbr = 0

      
for process_type in process_type_list:
    print(process_type)
    run_nbr = run_nbr + 1
    for index, row in state_df.iterrows():
        state_numeric = row.State_Code_Numeric
        state_alpha = row.State_Code_Alpha
        print(state_numeric)
        print(state_alpha)
        for file in file_list:
            print(file)
            if 'submission_methods' in process_type:
               table_name = "datalab_scratch.daily_" + state_numeric + "_" + state_alpha + "_" + file + "_ready_ml_input_df_ss"
            else:
               table_name = "datalab_scratch.daily_" + state_numeric + "_" + state_alpha + "_" + file + "_ready_ml_input_df"
            
            train_pdf, test_pdf = get_train_and_test_df(table_name)
            train_pdf_work = train_pdf.copy()
            
            if 'outlier' in process_type:
               train_pdf_work = treat_outliers(train_pdf_work,'errs')
              
            if train_pdf.empty or test_pdf.empty:
               print("No Data for the state " + state_alpha + " and file type " + file )
            else:
               run_multi_liner_regression(train_pdf,train_pdf_work,test_pdf,process_type,state_numeric,state_alpha,file,run_nbr)

                




# COMMAND ----------

# MAGIC %sql
# MAGIC select * from datalab_scratch.lr_multi_train_forecast_1_kv;

# COMMAND ----------

# MAGIC %sql
# MAGIC create or replace table datalab_scratch.lr_multi_test_forecast_2_kv using delta
# MAGIC as
# MAGIC select model_run_type
# MAGIC      , model_run_num
# MAGIC      , state_code_numeric
# MAGIC      , state_code_alpha
# MAGIC      , daily_rep_pd_date
# MAGIC      , date_text
# MAGIC      , date_int
# MAGIC      , file_type
# MAGIC      , sum(errors_actual_previous_mo) as errors_actual_previous_mo
# MAGIC      , sum(errors_actual_current_mo) as errors_actual_current_mo
# MAGIC      , sum(mo_to_mo_difference) as mo_to_mo_difference
# MAGIC      , sum(mo_to_mo_pct) as mo_to_mo_pct
# MAGIC      , sum(errors_predicted_current_mo) as errors_predicted_current_mo
# MAGIC      , sum(actual_to_predicted_difference) as actual_to_predicted_difference
# MAGIC      , sum(absolute_difference) as absolute_difference
# MAGIC      , sum(actual_to_predicted_pct) as actual_to_predicted_pct
# MAGIC      , model_parent_process
# MAGIC      , model_name
# MAGIC      , score_type
# MAGIC      , model_score_forecast
# MAGIC      , model_score_train
# MAGIC      , model_score_validate
# MAGIC      , model_score_test
# MAGIC      , source_notebook_url
# MAGIC      , best_model_url
# MAGIC      , experiment_info
# MAGIC      , source_data_table_name
# MAGIC      , comments
# MAGIC   from datalab_scratch.lr_multi_test_forecast_1_kv
# MAGIC -- where model_run_num = 3
# MAGIC --   and state_code_numeric = '44'
# MAGIC --   and file_type = 'COT'
# MAGIC  --  and date_int = 19
# MAGIC  group by model_run_type
# MAGIC         , model_run_num
# MAGIC         , state_code_numeric
# MAGIC         , state_code_alpha
# MAGIC         , daily_rep_pd_date
# MAGIC         , date_text
# MAGIC         , date_int
# MAGIC         , file_type
# MAGIC         , model_parent_process
# MAGIC         , model_name
# MAGIC         , score_type
# MAGIC         , model_score_forecast
# MAGIC         , model_score_train
# MAGIC         , model_score_validate
# MAGIC         , model_score_test
# MAGIC         , source_notebook_url
# MAGIC         , best_model_url
# MAGIC         , experiment_info
# MAGIC         , source_data_table_name
# MAGIC         , comments
# MAGIC  order by model_run_num
# MAGIC         , state_code_numeric
# MAGIC         , state_code_alpha
# MAGIC         , file_type
# MAGIC         , date_int

# COMMAND ----------

# MAGIC %sql
# MAGIC create or replace table datalab_scratch.lr_multi_train_forecast_2_kv using delta
# MAGIC as
# MAGIC select model_run_type
# MAGIC      , model_run_num
# MAGIC      , state_code_numeric
# MAGIC      , state_code_alpha
# MAGIC      , daily_rep_pd_date
# MAGIC      , date_int
# MAGIC      , file_type
# MAGIC      , comments
# MAGIC      , sum(errs) as errs
# MAGIC   from datalab_scratch.lr_multi_train_forecast_1_kv
# MAGIC -- where model_run_num = 3
# MAGIC --   and state_code_numeric = '44'
# MAGIC --   and file_type = 'COT'
# MAGIC --   and date_int = 18
# MAGIC  group by model_run_type
# MAGIC         , model_run_num
# MAGIC         , state_code_numeric
# MAGIC         , state_code_alpha
# MAGIC         , daily_rep_pd_date
# MAGIC         , date_int
# MAGIC         , file_type
# MAGIC         , comments
# MAGIC   order by model_run_num
# MAGIC         , state_code_numeric
# MAGIC         , state_code_alpha
# MAGIC         , file_type
# MAGIC         , date_int

# COMMAND ----------

import pandas as pd
import numpy as np

final_df = pd.DataFrame(columns=['model_run_type','model_run_num','state_code_numeric','state_code_alpha','daily_rep_pd_date','date_text','date_int','file_type','errors_actual_previous_mo','errors_actual_current_mo','mo_to_mo_difference',	'mo_to_mo_pct','errors_predicted_current_mo','actual_to_predicted_difference','absolute_difference','actual_to_predicted_pct','model_parent_process','model_name','score_type','model_score_forecast','model_score_train','model_score_validate','model_score_test','source_notebook_url','best_model_url','experiment_info','source_data_table_name','comments'])


try:
  spark.sql("drop table datalab_scratch.lr_multi_final_forecast_kv ")
except Exception as e:
#except:
  print(f"Table does not esist")
  print(e) 

test_df_spark = spark.sql("select * from datalab_scratch.lr_multi_test_forecast_2_kv ")
test_df = test_df_spark.toPandas()

train_df_spark = spark.sql("select * from datalab_scratch.lr_multi_train_forecast_2_kv ")
train_df = train_df_spark.toPandas()


for index, row in test_df.iterrows():
    previous_month = row.date_int - 1
    #print(previous_month)
    if row.date_int == 19:
       get_previous_month_errors = train_df.loc[(train_df['state_code_numeric'] == row.state_code_numeric) & (train_df['model_run_num'] == row.model_run_num) & (train_df['file_type'] == row.file_type) & (train_df['date_int'] == 18) ]['errs'].values[0]
    else:
       get_previous_month_errors = test_df.loc[(test_df['state_code_numeric'] == row.state_code_numeric) & (test_df['model_run_num'] == row.model_run_num) & (test_df['file_type'] == row.file_type) & (test_df['date_int'] == previous_month) ]['errors_actual_current_mo'].values[0]
    #print(get_previous_month_errors)
    
    month_to_month_difference = row.errors_actual_current_mo - get_previous_month_errors
    month_to_month_pct = float(month_to_month_difference/get_previous_month_errors)
    
    actual_to_predicted_difference_errors = row.errors_predicted_current_mo - row.errors_actual_current_mo
    absolute_diff = abs(actual_to_predicted_difference_errors)
    actual_to_predic_pct = float(actual_to_predicted_difference_errors/row.errors_actual_current_mo)
    
    
    final_df = final_df.append({'model_run_type':row.model_run_type,'model_run_num':row.model_run_num,'state_code_numeric':row.state_code_numeric,'state_code_alpha':row.state_code_alpha,'daily_rep_pd_date':row.daily_rep_pd_date,'date_text':row.date_text,'date_int':row.date_int,'file_type':row.file_type,'errors_actual_previous_mo':get_previous_month_errors,'errors_actual_current_mo':row.errors_actual_current_mo,'mo_to_mo_difference':month_to_month_difference,	'mo_to_mo_pct':month_to_month_pct,'errors_predicted_current_mo':row.errors_predicted_current_mo,'actual_to_predicted_difference':actual_to_predicted_difference_errors,'absolute_difference':absolute_diff,'actual_to_predicted_pct':actual_to_predic_pct,'model_parent_process':row.model_parent_process,'model_name':row.model_name,'score_type':row.score_type,'model_score_forecast':row.model_score_forecast,'model_score_train':row.model_score_train,'model_score_validate':row.model_score_validate,'model_score_test':row.model_score_test,'source_notebook_url':row.source_notebook_url,'best_model_url':row.best_model_url,'experiment_info':row.experiment_info,'source_data_table_name':row.source_data_table_name,'comments':row.comments},ignore_index=True)

print(final_df)
spark_final_df = spark.createDataFrame(final_df) 
spark_final_df.write.saveAsTable("datalab_scratch.lr_multi_final_forecast_kv",mode="overwrite")
    


# COMMAND ----------

# MAGIC %sql
# MAGIC select * from datalab_scratch.lr_multi_final_forecast_kv

# COMMAND ----------

# MAGIC %sql
# MAGIC update datalab_scratch.lr_multi_final_forecast_kv
# MAGIC    set source_data_table_name = 'datalab_scratch.lr_multi_final_forecast_kv'
# MAGIC    

# COMMAND ----------

# MAGIC %sql
# MAGIC update datalab_scratch.lr_multi_final_forecast_kv
# MAGIC    set source_notebook_url = 'https://databricks-val-data.macbisdw.cmscloud.local/#notebook/2831216/command/2831222'

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from datalab_scratch.lr_multi_final_forecast_kv
# MAGIC  where model_run_num = 1
# MAGIC    and state_code_numeric = 44
# MAGIC  order by file_type,date_int

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from datalab_scratch.lr_multi_final_forecast_kv
# MAGIC  where state_code_numeric = 29
# MAGIC  order by file_type,date_int

# COMMAND ----------

# MAGIC %sql select state_code_numeric, file_type, model_run_num, max(model_score_validate)
# MAGIC from datalab_scratch.lr_multi_final_forecast_kv
# MAGIC group by state_code_numeric, file_type, model_run_num
# MAGIC order by 4 desc

# COMMAND ----------

# MAGIC %sql --Avg validation score by state, file type, and model feature type (IE all months for this combo)
# MAGIC select state_code_numeric, file_type, model_run_num, avg(model_score_validate)
# MAGIC from datalab_scratch.lr_multi_final_forecast_kv
# MAGIC group by state_code_numeric, file_type, model_run_num
# MAGIC --having avg(model_score_validate) < .5
# MAGIC order by 4 desc

# COMMAND ----------

# MAGIC %sql -- Feature generation types with models performing worse than a constant model
# MAGIC -- IE feature generation types 3 and 4 where always better than a constant function
# MAGIC select model_run_num, count(*) from (
# MAGIC select state_code_numeric, file_type, model_run_num, avg(model_score_validate)
# MAGIC from datalab_scratch.lr_multi_final_forecast_kv
# MAGIC group by state_code_numeric, file_type, model_run_num
# MAGIC having avg(model_score_validate) < 0)
# MAGIC group by model_run_num
# MAGIC order by 2 desc

# COMMAND ----------

# MAGIC %sql -- The best model generated with feature set 4 ('Features/Processing: error_category_with_outlier_treatment') always had a .4 r2 score or better
# MAGIC select model_run_num, count(*) from (
# MAGIC select state_code_numeric, file_type, model_run_num, avg(model_score_validate)
# MAGIC from datalab_scratch.lr_multi_final_forecast_kv
# MAGIC group by state_code_numeric, file_type, model_run_num
# MAGIC having avg(model_score_validate) > .4)
# MAGIC group by model_run_num
# MAGIC order by 2 desc
