import datetime as dt
import os

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator


with DAG(
    dag_id="01_docker",
    description="Fetches ratings from the Movielens API using Docker.",
    start_date=dt.datetime(2019, 1, 1),
    end_date=dt.datetime(2019, 1, 3),
    schedule_interval="@daily",
) as dag:

    # arrancamos un contenedor en base a una imagen, especificando unos comandos. El dag no se indica explicitamente, pero estamos en un contexto, asi que se indica de forma indirecta
    fetch_ratings = DockerOperator(
        task_id="fetch_ratings",
        image="manning-airflow/movielens-fetch",
        command=[
            "fetch-ratings",
            "--start_date",
            "{{ds}}",
            "--end_date",
            "{{next_ds}}",
            "--output_path",
            "/data/ratings/{{ds}}.json",
            "--user",
            os.environ["MOVIELENS_USER"],
            "--password",
            os.environ["MOVIELENS_PASSWORD"],
            "--host",
            os.environ["MOVIELENS_HOST"],
        ],
        network_mode="airflow",
        # Note: this host path is on the HOST, not in the Airflow docker container.
        volumes=["/tmp/airflow/data:/data"],
    )

    # Instanciamos una segunda imagen
    rank_movies = DockerOperator(
        task_id="rank_movies",
        image="manning-airflow/movielens-rank",
        command=[
            "rank-movies",
            "--input_path",
            "/data/ratings/{{ds}}.json",
            "--output_path",
            "/data/rankings/{{ds}}.csv",
        ],
        volumes=["/tmp/airflow/data:/data"],
    )

    fetch_ratings >> rank_movies # como siempre
