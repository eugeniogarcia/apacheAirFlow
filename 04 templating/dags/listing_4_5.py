from urllib import request

import airflow.utils.dates
from airflow import DAG
from airflow.operators.python import PythonOperator

dag = DAG(
    dag_id="listing_4_05",
    start_date=airflow.utils.dates.days_ago(1),
    schedule_interval="@hourly",
)


def _get_data(execution_date):
    year, month, day, hour, *_ = execution_date.timetuple()
    url = (
        "https://dumps.wikimedia.org/other/pageviews/"
        f"{year}/{year}-{month:0>2}/pageviews-{year}{month:0>2}{day:0>2}-{hour:0>2}0000.gz"
    )
    output_path = "/tmp/wikipageviews.gz"
    request.urlretrieve(url, output_path)

#En el python operator lo que pasamos como argumento es una función, no un string; Esto significa que el jinja template no tiene efecto como si sucedía en el bashoperator; Lo que tendremos que hacer es en la logica de la propia funcion tomar los parametros del runtime y formatear la string
get_data = PythonOperator(task_id="get_data", python_callable=_get_data, dag=dag)
