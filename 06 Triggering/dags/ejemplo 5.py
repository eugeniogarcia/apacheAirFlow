import airflow.utils.dates
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
from airflow.sensors.external_task import ExternalTaskSensor

dag1 = DAG(
    dag_id="figure_6_19_dag_1",
    start_date=airflow.utils.dates.days_ago(3),
    schedule_interval="0 0 * * *",
)
dag2 = DAG(
    dag_id="figure_6_19_dag_2",
    start_date=airflow.utils.dates.days_ago(3),
    schedule_interval="0 0 * * *",
)
dag3 = DAG(
    dag_id="figure_6_19_dag_3",
    start_date=airflow.utils.dates.days_ago(3),
    schedule_interval="0 0 * * *",
)
dag4 = DAG(
    dag_id="figure_6_19_dag_4",
    start_date=airflow.utils.dates.days_ago(3),
    schedule_interval=None,
)

#DAGs 1, 2 y 3
DummyOperator(task_id="etl", dag=dag1)
DummyOperator(task_id="etl", dag=dag2)
DummyOperator(task_id="etl", dag=dag3)

#DAG 4
#Tenemos una Sensores que esperan a que se termine una tarea en otro DAG
[
    ExternalTaskSensor(
        task_id="wait_for_etl_dag1",
        external_dag_id="figure_6_19_dag_1", # hace referencia al DAG 1
        external_task_id="etl", # hace referencia a una tarea dentro de ese DAG
        dag=dag4,
    ),
    ExternalTaskSensor(
        task_id="wait_for_etl_dag2",
        external_dag_id="figure_6_19_dag_2", # hace referencia al DAG 2
        external_task_id="etl", # hace referencia a una tarea dentro de ese DAG
        dag=dag4,
    ),
    ExternalTaskSensor(
        task_id="wait_for_etl_dag3",
        external_dag_id="figure_6_19_dag_3", # hace referencia al DAG 3
        external_task_id="etl", # hace referencia a una tarea dentro de ese DAG
        dag=dag4,
    ),
] >> PythonOperator(task_id="report", dag=dag4, python_callable=lambda: print("hello"))
