from pathlib import Path

import airflow.utils.dates
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.sensors.python import PythonSensor

dag = DAG(
    dag_id="figure_6_09",
    start_date=airflow.utils.dates.days_ago(14),
    schedule_interval="0 16 * * *",
    description="A batch workflow for ingesting supermarket promotions data, demonstrating the PythonSensor.",
)

create_metrics = DummyOperator(task_id="create_metrics", dag=dag)


def _wait_for_supermarket(supermarket_id_):
    supermarket_path = Path("/data/" + supermarket_id_)
    data_files = supermarket_path.glob("data-*.csv")
    success_file = supermarket_path / "_SUCCESS"
    return data_files and success_file.exists()


for supermarket_id in range(1, 5):
    wait = PythonSensor(
        task_id=f"wait_for_supermarket_{supermarket_id}",
        python_callable=_wait_for_supermarket,
        op_kwargs={"supermarket_id_": f"supermarket{supermarket_id}"},
        timeout=600, # Con el timeout indicamos el máximo tiempo que el sensor va a ejecutarse; Por defecto son siete dias
        mode="reschedule", # por defecto el modo es poke; En el modo poke la tarea figura running durante todo el tiempo que estamos chequeando - ejecuta, chequea, ejecuta, chquea, ... asi hasta que la condicion se cumpla o se agote todo el timeout. Con el modo reschedule la tarea no esta en running todo el tiempo sino solo cuando se hace el chequeo - ejecuta, chequea, reschedulea, ejecuta, cheuquea,... asi hasta que la condicion se cumpla o se agote todo el timeout 
        dag=dag,
    )
    copy = DummyOperator(task_id=f"copy_to_raw_supermarket_{supermarket_id}", dag=dag)
    process = DummyOperator(task_id=f"process_supermarket_{supermarket_id}", dag=dag)
    wait >> copy >> process >> create_metrics
