"""
This dag is demo airflow and serve as team example.
"""
import airflow
from operators.demo import do_one_thing, do_some_others, finish_up

from datetime import timedelta
from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator


args = {
    'owner': 'Airflow',
    'retries': 1,
    'start_date': airflow.utils.dates.days_ago(2),
    'retry_delay': timedelta(minutes=1)
}

dag = DAG(
    dag_id='demo',
    default_args=args,
    schedule_interval='0 0 * * *',
    dagrun_timeout=timedelta(minutes=60)
)

dot = PythonOperator(
    task_id='do_one_thing',
    python_callable=do_one_thing,
    dag=dag
)

dso1 = PythonOperator(
    task_id='do_some_others_1',
    python_callable=do_some_others,
    op_args=[1],
    dag=dag
)

dso2 = PythonOperator(
    task_id='do_some_others_2',
    python_callable=do_some_others,
    op_args=[2],
    dag=dag
)

fu = PythonOperator(
    task_id='finish_up',
    python_callable=finish_up,
    dag=dag
)

dot >> [dso1, dso2] >> fu
