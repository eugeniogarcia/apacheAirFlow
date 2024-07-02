import datetime
import os
from collections import namedtuple
from pathlib import Path

import pytest
from airflow.models import DAG, Connection
from pytest_docker_tools import fetch, container
from pytest_mock import MockFixture

from airflowbook.operators.movielens_operator import (
    MovielensDownloadOperator,
    MovielensHook,
    MovielensToPostgresOperator,
    PostgresHook,
)

'''
Otro ejemplo en el que se demuestra como utilizar fixtures y crear programáticamente un contenedor de docker para hacer el test
'''

# Paso 3. Creamos una fixture con scope modulo, en la que definimos las credenciales que usaremos en nuestra instancia de Postgress
@pytest.fixture(scope="module")
def postgres_credentials():
    # Definimos una clase namedtuple llamada PostgresCredentials que tiene dos campos, username y password 
    PostgresCredentials = namedtuple("PostgresCredentials", ["username", "password"])
    return PostgresCredentials("testuser", "testpass")

# Paso 1. Creamos la imagen. fetch es una pytest fixture, no es un metodo como tal. Por lo tanto postgres_image es tambien una pytest fixture
postgres_image = fetch(repository="postgres:11.1-alpine")

'''
Paso 2. Creamos el contenedor. container es una pytest fixture. Esta fixture se basa en la fixture postgres_image. El contenedor lo creamos con:

- unas variables de entorno que hacen referencia a las credenciales con las que se instanciara la base de datos postgress. Las credenciales son a su vez una fixture
- mapeo de puertos
- volumenes. montamos en el volumen /docker-entrypoint-initdb.d/ un script llamado postgres-init.sql. Todo lo que incluimos en este directorio es ejecutado cuando el contenedor se arranca. El contenido de este script lo tenemos en nuestro host en un archivo que se llama postgres-init.sql. Lo que estamos haciendo es inicializar el esquema de nuestra base Postgress
''' 
postgres = container(
    image="{postgres_image.id}",
    environment={
        "POSTGRES_USER": "{postgres_credentials.username}",
        "POSTGRES_PASSWORD": "{postgres_credentials.password}",
    },
    ports={"5432/tcp": None}, # Al indicar None se mapeara el puerto 5432 a un puerto aleatorio del host. Asi aseguramos que no haya conflictos porque el puerto este ocupado
    volumes={
        os.path.join(os.path.dirname(__file__), "postgres-init.sql"): {
            "bind": "/docker-entrypoint-initdb.d/postgres-init.sql"
        }
    },
)

# Usamos dos fixtures por defecto, el tmp_path y mocker
def test_movielens_operator(tmp_path: Path, mocker: MockFixture):
    mocker.patch.object(
        MovielensHook,
        "get_connection",
        return_value=Connection(conn_id="test", login="airflow", password="airflow"),
    )
    dag = DAG(
        "test_dag",
        default_args={"owner": "airflow", "start_date": datetime.datetime(2019, 1, 1)},
        schedule_interval="@daily",
    )

    task = MovielensDownloadOperator(
        task_id="test",
        conn_id="testconn",
        start_date="{{ prev_ds }}",
        end_date="{{ ds }}",
        output_path=str(tmp_path / "{{ ds }}.json"),
        dag=dag,
    )

    dag.clear()
    task.run(
        start_date=dag.default_args["start_date"],
        end_date=dag.default_args["start_date"],
        ignore_ti_state=True,
    )

''' 
Paso 3. Usamos varias fixtures:
- mocker. Es la fixture incluida por defecto al instala pytest-mock. Nos permite mockear metodos de clases
- test_dag: es una fixture que hemos creado en el archivo conftest. Crear un DAG
- postgres_credentials: es una fixture con scope modulo que hemos creado antes
- postgres: es una fixture que hace referencia a nuestro contenedor de Postgress
'''
def test_movielens_to_postgres_operator(
    mocker: MockFixture, test_dag: DAG, postgres, postgres_credentials
):
    mocker.patch.object(
        MovielensHook,
        "get_connection",
        return_value=Connection(conn_id="test", login="airflow", password="airflow"),
    )
    mocker.patch.object(
        PostgresHook,
        "get_connection",
        return_value=Connection(
            conn_id="postgres",
            conn_type="postgres",
            host="localhost",
            login=postgres_credentials.username, # Usamos las mismas credenciales que usamos en nuestro contenedor postgress para crear la instancia de Postgress
            password=postgres_credentials.password,
            port=postgres.ports["5432/tcp"][0], # usamos el puerto que hemos expuesto en nuestro contenedor docker de Postgress
        ),
    )

    task = MovielensToPostgresOperator(
        task_id="test",
        movielens_conn_id="movielens_id",
        start_date="{{ prev_ds }}",
        end_date="{{ ds }}",
        postgres_conn_id="postgres_id",
        insert_query=(
            "INSERT INTO movielens (movieId,rating,ratingTimestamp,userId,scrapeTime) "
            "VALUES ({0}, '{{ macros.datetime.now() }}')"
        ),
        dag=test_dag,
    )

    # Vamos a comprobar que efectivamente en Postgress se han hecho las cosas que se tendrían que haber hecho 
    pg_hook = PostgresHook()
    # comprobamos que tengamos las filas insertadas
    row_count = pg_hook.get_first("SELECT COUNT(*) FROM movielens")[0]
    assert row_count == 0

    # Usa el helper definido en conftest
    pytest.helpers.run_airflow_task(task, test_dag)

    row_count = pg_hook.get_first("SELECT COUNT(*) FROM movielens")[0]
    assert row_count > 0

# Creamos otro fixture con un contenedor
postgres_container = container(image="{postgres_image.id}", ports={"5432/tcp": None})


def test_call_fixture(postgres_container):
    print(
        f"Running Postgres container named {postgres_container.name} "
        f"on port {postgres_container.ports['5432/tcp'][0]}."
    )
