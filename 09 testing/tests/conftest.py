import datetime

import pytest
from airflow.models import DAG, BaseOperator

pytest_plugins = ["helpers_namespace"]

'''
Define elementos que queremos usar en todos los tests: fixtures y helpers
'''

# define una fixture
@pytest.fixture
def test_dag():
    return DAG(
        "test_dag",
        default_args={"owner": "airflow", "start_date": datetime.datetime(2015, 1, 1)},
        schedule_interval="@daily",
    )


# define una funcion helper
@pytest.helpers.register
def run_airflow_task(task: BaseOperator, dag: DAG):
    dag.clear()
    task.run(
        start_date=dag.default_args["start_date"],
        end_date=dag.default_args["start_date"],
        ignore_ti_state=True,
    )
