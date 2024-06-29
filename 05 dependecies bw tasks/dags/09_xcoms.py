import uuid

import airflow

from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator

'''
xcoms es el object store incluido con AIF. Podemos pasar datos de una tarea a otra usando el xcom - solo se puede usar cuando el tamaño de la información que queremos intercambiar es moderado. El tamaño depende del motor de base de datos que usemos para definir el esquema de AIF - postgres, mysql, sqlite
'''

def _train_model(**context):
    model_id = str(uuid.uuid4())
    context["task_instance"].xcom_push(key="model_id", value=model_id) #guardamos en el XCOM. Esto registrara para las tarea y fecha de ejecución, este key pair


def _deploy_model(**context):
    model_id = context["task_instance"].xcom_pull( #recuperamos del XCOM el key pair que se ha generado en la tarea que especifiquemos. También se puede especificar el DAG en lugar de la tarea. Sino indicamos la fecha se toma por defecto la fecha actual de ejecución
        task_ids="train_model", key="model_id"
    )
    print(f"Deploying model {model_id}")


with DAG(
    dag_id="10_xcoms",
    start_date=airflow.utils.dates.days_ago(3),
    schedule_interval="@daily",
) as dag:
    start = DummyOperator(task_id="start")

    fetch_sales = DummyOperator(task_id="fetch_sales")
    clean_sales = DummyOperator(task_id="clean_sales")

    fetch_weather = DummyOperator(task_id="fetch_weather")
    clean_weather = DummyOperator(task_id="clean_weather")

    join_datasets = DummyOperator(task_id="join_datasets")

    train_model = PythonOperator(task_id="train_model", python_callable=_train_model)

    deploy_model = PythonOperator(task_id="deploy_model", python_callable=_deploy_model)

    start >> [fetch_sales, fetch_weather]
    fetch_sales >> clean_sales
    fetch_weather >> clean_weather
    [clean_sales, clean_weather] >> join_datasets
    join_datasets >> train_model >> deploy_model
