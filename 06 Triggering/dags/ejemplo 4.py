from pathlib import Path

import airflow.utils.dates
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.sensors.python import PythonSensor

'''
Demostramos como llamar a un DAG desde otro

Declaramos dos DAGs
'''
dag1 = DAG(
    dag_id="listing_6_04_dag01",
    start_date=airflow.utils.dates.days_ago(3),
    schedule_interval="0 16 * * *",
)
dag2 = DAG(
    dag_id="listing_6_04_dag02",
    start_date=airflow.utils.dates.days_ago(3),
    schedule_interval=None, # este DAG lo vamos a llamar desde el dag1
)


def _wait_for_supermarket(supermarket_id_):
    supermarket_path = Path("/data/" + supermarket_id_)
    data_files = supermarket_path.glob("data-*.csv")
    success_file = supermarket_path / "_SUCCESS"
    return data_files and success_file.exists()

#Tenemos 4 ramas que se ejecutan en el DAG1, y que terminan ejecutando el DAG2
for supermarket_id in range(1, 5):
    # Tarea normal ejecutada en el DAG1 
    wait = PythonSensor(
        task_id=f"wait_for_supermarket_{supermarket_id}",
        python_callable=_wait_for_supermarket,
        op_kwargs={"supermarket_id_": f"supermarket{supermarket_id}"},
        dag=dag1,
    )
    # Tarea normal ejecutada en el DAG1
    copy = DummyOperator(task_id=f"copy_to_raw_supermarket_{supermarket_id}", dag=dag1)
    # Tarea normal ejecutada en el DAG1
    process = DummyOperator(task_id=f"process_supermarket_{supermarket_id}", dag=dag1)
    # Tarea que dispara el DAG2
    trigger_create_metrics_dag = TriggerDagRunOperator(
        task_id=f"trigger_create_metrics_dag_supermarket_{supermarket_id}",
        trigger_dag_id="listing_6_04_dag02", # Este es el ID del DAG que vamos a arrancar; En este caso se corresponde con el id del DAG2
        dag=dag1, # La tarea esta dentro del DAG1
    )
    wait >> copy >> process >> trigger_create_metrics_dag

#Estas tareas pertenecen al DAG2
compute_differences = DummyOperator(task_id="compute_differences", dag=dag2)
update_dashboard = DummyOperator(task_id="update_dashboard", dag=dag2)
notify_new_data = DummyOperator(task_id="notify_new_data", dag=dag2)
compute_differences >> update_dashboard
