"""
Module for audit trail report dag
"""
import airflow

from datetime import timedelta
from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator
from operators.process import Trigger

trigger = Trigger()

args = {
    'owner': 'Airflow',
    'start_date': airflow.utils.dates.days_ago(2)
}

dag = DAG(
    dag_id='audit_trail',
    default_args=args,
    schedule_interval='@daily',
    dagrun_timeout=timedelta(minutes=60)
)

run_report = BashOperator(
    task_id='generate_audit_report',
    bash_command=trigger.audit_report,
    dag=dag
)

run_report
