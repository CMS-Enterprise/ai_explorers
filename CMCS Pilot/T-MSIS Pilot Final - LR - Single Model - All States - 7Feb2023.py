# Databricks notebook source
from pyspark.sql.functions import col
from pyspark.sql.functions import count
import pandas as pd
import numpy as np

import matplotlib.pylab as plt
%matplotlib inline

import seaborn as sns
from sklearn.model_selection  import train_test_split
from sklearn.cluster import KMeans

from scipy.stats import zscore
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
#from pyspark.sql.functions import col

def get_date_int(in_date):
    return int(str(in_date).split('-')[2])
  

def get_date_text(in_date):
    return str(in_date)

def run_liner_regression(train_pdf,train_pdf_work,test_pdf,process_type,state_numeric,state_alpha,file,run_nbr):
    train_pdf['date_int'] = train_pdf.daily_rep_pd_date.apply(get_date_int)
    test_pdf['date_int'] = test_pdf.daily_rep_pd_date.apply(get_date_int)
    train_pdf_work['date_int'] = train_pdf_work.daily_rep_pd_date.apply(get_date_int)

    x_train = train_pdf_work.copy()
    x_test = test_pdf.copy()
    y_train = x_train[['errs']]
    y_test = x_test[['errs']]

    #Drop errors from the x dataset
    x_train=x_train.drop('errs',axis=1)
    x_test=x_test.drop('errs',axis=1)
    x_train=x_train.drop('daily_rep_pd_date',axis=1)
    x_test=x_test.drop('daily_rep_pd_date',axis=1)

    #Fit Linear model
    regression_model = LinearRegression()
    regression_model.fit(x_train,y_train)

    #Model Scores
    model_score_train = regression_model.score(x_train,y_train)
    #print("Model Score on Train set : " + str(model_score_train) )

    model_score_test = regression_model.score(x_test,y_test)
    #print("Model Score on Test set : " + str(model_score_test) )

    y_predict = pd.DataFrame(regression_model.predict(x_test))
    y_predict.rename(columns = {0:'errs_predict'}, inplace = True)

    lr_df = pd.concat([test_pdf,y_predict], axis=1, join='inner')
    
    lr_df['file_type'] = file
    lr_df['state_code_numeric'] = state_numeric
    lr_df['state_code_alpha'] = state_alpha
    lr_df['date_text'] = lr_df.daily_rep_pd_date.apply(get_date_text)

    lr_df['model_score_train'] = str(model_score_train)[:4]
    lr_df['model_score_validate'] = ' ' 
    lr_df['model_score_test'] = str(model_score_test)[:4]

    lr_df['model_parent_process'] = 'Python ML'
    lr_df['model_name'] = 'Linear regression'
    lr_df['score_type'] = 'R2'
    lr_df['errs_predict'] = lr_df['errs_predict'].astype('int64')

    lr_df["best_model_url"] = ''
    lr_df["experimant_info"] = ''
    lr_df["model_run_num"] = run_nbr
    lr_df['model_run_type'] = 'C - LR - Single Model'
    lr_df['comments'] = process_type
    lr_df['source_data_table_name'] = ' '
    
    lr_df['errors_actual_previous_mo'] = 0
    lr_df['mo_to_mo_difference'] = 0
    #lr_df['errors_predicted_current_mo'] = 0
    lr_df['errors_actual_previous_mo'] = 0
    lr_df['errors_actual_previous_mo'] = lr_df['errors_actual_previous_mo'].astype('int64')
    lr_df['actual_to_predicted_difference'] = 0
    lr_df['source_notebook_url'] = ' '
    lr_df['actual_to_predicted_pct'] = 0
    lr_df['experiment_info'] = ' '
    lr_df['mo_to_mo_pct'] = 0
    #lr_df['errors_actual_current_mo'] = 0
    lr_df.rename(columns={'errs': 'errors_actual_current_mo', 'errs_predict': 'errors_predicted_current_mo'}, inplace=True)
    lr_df['model_score_forecast'] = 0
    lr_df['absolute_difference'] = 0
    
    return_df=lr_df[['model_run_type','model_run_num','state_code_numeric','state_code_alpha','daily_rep_pd_date','date_text','date_int','file_type','errors_actual_previous_mo','errors_actual_current_mo','mo_to_mo_difference',	'mo_to_mo_pct','errors_predicted_current_mo','actual_to_predicted_difference','absolute_difference','actual_to_predicted_pct','model_parent_process','model_name','score_type','model_score_forecast','model_score_train','model_score_validate','model_score_test','source_notebook_url','best_model_url','experiment_info','source_data_table_name','comments']]
    
    spark_return_df = spark.createDataFrame(return_df) 
    spark_return_df.write.saveAsTable("datalab_scratch.lr_test_forecast_1_all_kv",mode="append")
    
    train_pdf['model_run_type'] = 'C - LR - Single Model'
    train_pdf['file_type'] = file
    train_pdf['state_code_numeric'] = state_numeric
    train_pdf['state_code_alpha'] = state_alpha
    train_pdf['comments'] = process_type
    train_pdf['model_run_num'] = run_nbr
    train_pdf['errs'] = train_pdf['errs'].astype('int64')
    
    return_train_pdf = train_pdf[['model_run_type','model_run_num','state_code_numeric','state_code_alpha','daily_rep_pd_date','date_int','file_type','comments','errs']]
    spark_train_pdf = spark.createDataFrame(return_train_pdf) 
    spark_train_pdf.write.saveAsTable("datalab_scratch.lr_train_forecast_1_all_kv",mode="append")
    
    
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
  spark.sql("drop table datalab_scratch.lr_train_forecast_1_all_kv ")
except Exception as e:

  print(f"Table does not esist")
  print(e) 

try:
  spark.sql("drop table datalab_scratch.lr_test_forecast_1_all_kv ")
except Exception as e:

  print(f"Table does not esist")
  print(e) 

state_df_spark = spark.sql("select * from datalab_scratch.state_codes where state_code_numeric in ('01','02','04','05','06','08','09','10','11','12','13','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32','33','34','35','36','37','38','39','40','41','42','44','45','46','47','48','49','50','51','53','54','55','56','60','64','66','68','69','70','72','74','78','93','94','96','97') order by State_Code_Numeric")

state_df = state_df_spark.toPandas()

file_list = ['CIP','CLT','COT','CRX','ELG','MCR','PRV','TPL']

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
            #train_pdf['errs_orig'] = train_pdf['errs']
            
            if 'outlier' in process_type:
               train_pdf_work = treat_outliers(train_pdf_work,'errs')
              
            if train_pdf.empty or test_pdf.empty:
               print("No Data for the state " + state_alpha + " and file type " + file )
            else:
               run_liner_regression(train_pdf,train_pdf_work,test_pdf,process_type,state_numeric,state_alpha,file,run_nbr)
   



# COMMAND ----------

# MAGIC %sql
# MAGIC create or replace table datalab_scratch.lr_test_forecast_2_all_kv using delta
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
# MAGIC   from datalab_scratch.lr_test_forecast_1_all_kv
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
# MAGIC create or replace table datalab_scratch.lr_train_forecast_2_all_kv using delta
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
# MAGIC   from datalab_scratch.lr_train_forecast_1_all_kv
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
  spark.sql("drop table datalab_scratch.lr_final_forecast_all_kv")
except Exception as e:
#except:
  print(f"Table does not esist")
  print(e) 

test_df_spark = spark.sql("select * from datalab_scratch.lr_test_forecast_2_all_kv ")
test_df = test_df_spark.toPandas()

train_df_spark = spark.sql("select * from datalab_scratch.lr_train_forecast_2_all_kv ")
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
spark_final_df.write.saveAsTable("datalab_scratch.lr_final_forecast_all_kv",mode="overwrite")
    


# COMMAND ----------

# MAGIC %sql
# MAGIC select * from datalab_scratch.lr_final_forecast_all_kv
# MAGIC  where state_code_numeric = '29' 
# MAGIC  order by file_type,date_int, model_run_num

# COMMAND ----------

# MAGIC %sql
# MAGIC update datalab_scratch.lr_final_forecast_all_kv
# MAGIC    set source_data_table_name = 'datalab_scratch.lr_final_forecast_all_kv'
# MAGIC    

# COMMAND ----------

# MAGIC %sql
# MAGIC update datalab_scratch.lr_final_forecast_all_kv
# MAGIC    set source_notebook_url = 'https://databricks-val-data.macbisdw.cmscloud.local/#notebook/3091693/command/3104235'

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from datalab_scratch.lr_final_forecast_all_kv

# COMMAND ----------

# MAGIC %sql
# MAGIC select state_code_alpha, state_code_numeric, file_type, date_text, model_run_num, errors_actual_current_mo, actual_to_predicted_difference, actual_to_predicted_pct, comments
# MAGIC from datalab_scratch.lr_final_forecast_all_kv
# MAGIC where date_text = "2022-01-19"
# MAGIC order by state_code_alpha, state_code_numeric, file_type, date_text, model_run_num

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from datalab_scratch.lr_final_forecast_all_kv
# MAGIC  where model_run_num = 1
# MAGIC    and state_code_numeric = 44
# MAGIC  order by file_type,date_int

# COMMAND ----------

# MAGIC %sql select avg(float(model_score_test)) from datalab_scratch.lr_final_forecast_all_kv
# MAGIC  where model_run_num = 1 and model_score_test<>'nan'

# COMMAND ----------

# MAGIC %sql select * from datalab_scratch.lr_final_forecast_all_kv
# MAGIC where model_run_num=1
# MAGIC order by model_score_test

# COMMAND ----------

# MAGIC %sql --unique combos
# MAGIC select count(*) from
# MAGIC (select distinct state_code_numeric, file_type from datalab_scratch.lr_final_forecast_all_kv) 

# COMMAND ----------

# MAGIC %sql -- All variations of feature generation had a significant number of models that scored worse than a constant function for a simple linear regression
# MAGIC select model_run_num, count(*) from (
# MAGIC select state_code_numeric, file_type, model_run_num, avg(model_score_test)
# MAGIC from datalab_scratch.lr_final_forecast_all_kv
# MAGIC group by state_code_numeric, file_type, model_run_num
# MAGIC having avg(model_score_test) < 0)
# MAGIC group by model_run_num
# MAGIC order by 2 desc
