import datetime as dt
from pathlib import Path

import pandas as pd

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

dag = DAG(
    dag_id="11_atomic_send",
    schedule_interval="@daily",
    start_date=dt.datetime(year=2019, month=1, day=1),
    end_date=dt.datetime(year=2019, month=1, day=5),
    catchup=True, # Por defecto se hace catchup true; con catchup true el DAG se ejecutará de forma retroactiva desde el start_date, aunque la fecha sea pasada
)

fetch_events = BashOperator(
    task_id="fetch_events",
    bash_command=(
        "mkdir -p /data/events && "
        "curl -o /data/events/{{ds}}.json "
        "http://events_api:5000/events?"
        "start_date={{ds}}&"
        "end_date={{next_ds}}"
    ),
    dag=dag,
)


def _calculate_stats(**context):
    """Calculates event statistics."""
    input_path = context["templates_dict"]["input_path"]
    output_path = context["templates_dict"]["output_path"]

    events = pd.read_json(input_path)
    stats = events.groupby(["date", "user"]).size().reset_index()

    Path(output_path).parent.mkdir(exist_ok=True)
    stats.to_csv(output_path, index=False)


calculate_stats = PythonOperator(
    task_id="calculate_stats",
    python_callable=_calculate_stats,
    templates_dict={
        "input_path": "/data/events/{{ds}}.json",
        "output_path": "/data/stats/{{ds}}.csv",
    },
    dag=dag,
)


def email_stats(stats, email):
    """Send an email..."""
    print(f"Sending stats to {email}...")


def _send_stats(email, **context):
    stats = pd.read_csv(context["templates_dict"]["stats_path"])
    email_stats(stats, email=email)

'''
op_kwargs vs templates_dict

Ambas sirven para pasar parametros a Operador
Ambas son un diccionario

op_kwargs se desempaqueta al pasarla al operador, de modo que las keys se pasan como propiedades "separadas". templates_dict se pasa en el contexto como un diccionario

Al llegar al execute del Operador los keys de op_kwargs y de templates_dict llegan por separado, pero con la diferencia de que los valores de templates_dict se utilizan para proporcionar un valor por defecto
'''

# Para que el calculo de estadisticas sea atomico, separamos del calculo el envio del email. Asi en caso de que falle el envio de email no se repite el calculo de estadisticas
send_stats = PythonOperator(
    task_id="send_stats",
    python_callable=_send_stats,
    op_kwargs={"email": "user@example.com"},
    templates_dict={"stats_path": "/data/stats/{{ds}}.csv"},
    dag=dag,
)

fetch_events >> calculate_stats >> send_stats 
