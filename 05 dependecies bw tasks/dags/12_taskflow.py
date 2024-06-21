import uuid

import airflow

from airflow import DAG
from airflow.decorators import task


with DAG(
    dag_id="12_taskflow",
    start_date=airflow.utils.dates.days_ago(3),
    schedule_interval="@daily",
) as dag: #define un contexto de dag

    #Este decorador combierte a la función en una tarea del dag; Ver que estamos dentro del contexto de un dag
    @task
    def train_model():
        model_id = str(uuid.uuid4())
        return model_id

    @task
    def deploy_model(model_id: str):
        print(f"Deploying model {model_id}")

    model_id = train_model() # Indirectamente al invocar a las funciones y usar las variables de respuesta como argumentos de entrada, estamos definiendo el DAG
    deploy_model(model_id)
