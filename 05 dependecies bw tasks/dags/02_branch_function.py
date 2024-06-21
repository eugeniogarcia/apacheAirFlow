import airflow

from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator

ERP_CHANGE_DATE = airflow.utils.dates.days_ago(1)

'''
Tenemos dos logicas de negocio que queremos implementar en un determinado paso de la DAG. Por ejemplo, supongamos que a la hora de limpiar datos, los registros que nos descargamos tienen dos formatos diferentes dependiendo de la fecha en la que fueron generados.

Con el enfoque de este ejemplo, las dos logicas estarían enlatadas en el propio paso. Así pues nuestra tarea "clean_sales" es una, se ejecuta siempre, y "dentro de la lógica", se ejecuta una u otra funcionalidad dependiendo en la fecha de procesamiento.

Visualmente no sabemos si se ejecuto una u otra logica, tendremos que mirar los logs.
'''

def _fetch_sales(**context): #La propia tarea tiene embebidas dos logicas diferentes. El branching esta en la propia funcion (graficamente no se aprecia que haya dos logicas de negocio)
    if context["execution_date"] < ERP_CHANGE_DATE:
        _fetch_sales_old(**context)
    else:
        _fetch_sales_new(**context)


def _fetch_sales_old(**context):
    print("Fetching sales data (OLD)...")


def _fetch_sales_new(**context):
    print("Fetching sales data (NEW)...")


def _clean_sales(**context): #La propia tarea tiene embebidas dos logicas diferentes. El branching esta en la propia funcion
    if context["execution_date"] < airflow.utils.dates.days_ago(1):
        _clean_sales_old(**context)
    else:
        _clean_sales_new(**context)


def _clean_sales_old(**context):
    print("Preprocessing sales data (OLD)...")


def _clean_sales_new(**context):
    print("Preprocessing sales data (NEW)...")


with DAG(
    dag_id="02_branch_function",
    start_date=airflow.utils.dates.days_ago(3),
    schedule_interval="@daily",
) as dag:
    start = DummyOperator(task_id="start")

    fetch_sales = PythonOperator(task_id="fetch_sales", python_callable=_fetch_sales)
    clean_sales = PythonOperator(task_id="clean_sales", python_callable=_clean_sales)

    fetch_weather = DummyOperator(task_id="fetch_weather")
    clean_weather = DummyOperator(task_id="clean_weather")

    join_datasets = DummyOperator(task_id="join_datasets")
    train_model = DummyOperator(task_id="train_model")
    deploy_model = DummyOperator(task_id="deploy_model")

    start >> [fetch_sales, fetch_weather]
    fetch_sales >> clean_sales
    fetch_weather >> clean_weather
    [clean_sales, clean_weather] >> join_datasets
    join_datasets >> train_model >> deploy_model
