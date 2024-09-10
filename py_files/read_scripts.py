from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import os


# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2023, 9, 9),
}

# Define the DAG
dag = DAG(
    'run_python_scripts',
    default_args=default_args,
    description='A DAG to run four Python scripts end to end',
    schedule_interval=timedelta(days=1),
    catchup=False,
)


# Define Python functions that correspond to your scripts
def script_1():
    exec(open('/Users/ilaydabekircan/Documents/Vision_Bridge/DS_Assignment/py_files/DataIngestion.py').read())

def script_2():
    exec(open('/Users/ilaydabekircan/Documents/Vision_Bridge/DS_Assignment/py_files/Clustering.py').read())

def script_3():
    exec(open('/Users/ilaydabekircan/Documents/Vision_Bridge/DS_Assignment/py_files/analyzeaudiencesllm_openai.py').read())

# Define tasks using PythonOperator
task_1 = PythonOperator(
    task_id='run_script_1',
    python_callable=script_1,
    dag=dag,
)

task_2 = PythonOperator(
    task_id='run_script_2',
    python_callable=script_2,
    dag=dag,
)

task_3 = PythonOperator(
    task_id='run_script_3',
    python_callable=script_3,
    dag=dag,
)

# Set the task dependencies to run the scripts end to end
task_1 >> task_2 >> task_3 