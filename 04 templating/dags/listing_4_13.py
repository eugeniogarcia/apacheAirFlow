from urllib import request

import airflow.utils.dates
from airflow import DAG
from airflow.operators.python import PythonOperator

dag = DAG(
    dag_id="listing_4_13",
    start_date=airflow.utils.dates.days_ago(1),
    schedule_interval="@hourly",
)


def _get_data(year, month, day, hour, output_path, **_):
    url = (
        "https://dumps.wikimedia.org/other/pageviews/"
        f"{year}/{year}-{month:0>2}/pageviews-{year}{month:0>2}{day:0>2}-{hour:0>2}0000.gz"
    )
    request.urlretrieve(url, output_path)

'''
op_kwargs vs templates_dict

Ambas sirven para pasar parametros a Operador
Ambas son un diccionario

op_kwargs se desempaqueta al pasarla al operador, de modo que las keys se pasan como propiedades "separadas". templates_dict se pasa en el contexto como un diccionario

Al llegar al execute del Operador los keys de op_kwargs y de templates_dict llegan por separado, pero con la diferencia de que los valores de templates_dict se utilizan para proporcionar un valor por defecto
'''

get_data = PythonOperator(
    task_id="get_data",
    python_callable=_get_data,
    op_kwargs={ # Podemos pasar argumentos adicionales a los que proporciona el propio runtime con el parametro op_kwargs - se pasa un diccionario, como en este ejemplo -, o con el parametro op_args - se pasa una lista de parametros que se asignan en orden; Como podemos pasar strings, podemos usar jinga para formatearlos, como se demuestra en el ejemplo 
        "year": "{{ execution_date.year }}",
        "month": "{{ execution_date.month }}",
        "day": "{{ execution_date.day }}",
        "hour": "{{ execution_date.hour }}",
        "output_path": "/tmp/wikipageviews.gz",
    },
    dag=dag,
)
