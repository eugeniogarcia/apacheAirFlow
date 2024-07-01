from airflow.models import Connection
from airflow.operators.bash import BashOperator

from airflowbook.operators.movielens_operator import (
    MovielensPopularityOperator,
    MovielensHook,
)

'''
Demuestra como usar un mock
'''

# Pasamos como argumento mocker. En este argumento se inyectara nuestro modulo de mocking
def test_movielenspopularityoperator(mocker):
    # definimos el mock
    mock_get = mocker.patch.object(
        MovielensHook, # objeto que mockeamos
        "get_connection", # metodo que mockeamos
        return_value=Connection(conn_id="test", login="airflow", password="airflow"), # valor que se devuelve
    )

    # objeto del test
    task = MovielensPopularityOperator(
        task_id="test_id",
        conn_id="testconn",
        start_date="2015-01-01",
        end_date="2015-01-03",
        top_n=5,
    )
    result = task.execute(context=None)
    assert len(result) == 5

    # podemos comprobar si el mock efectivamente se ha llamado
    assert mock_get.call_count == 1
    # podemos verificar que cuando se llamara el mock se le llamara con el argumento testconn
    mock_get.assert_called_with("testconn")


def test_example():
    task = BashOperator(task_id="test", bash_command="echo 'hello!'", xcom_push=True)
    result = task.execute(context={})
    assert result == "hello!"
