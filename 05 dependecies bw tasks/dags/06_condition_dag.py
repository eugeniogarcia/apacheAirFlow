import airflow
import pendulum

from airflow import DAG
from airflow.exceptions import AirflowSkipException
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator

ERP_CHANGE_DATE = airflow.utils.dates.days_ago(1)

'''
Se demuestra como implementar una ejecucion condicional. La tarea implementa una logica que lanza una excepción AirflowSkipException cuando queremos que la tarea se skippe. Esto combinado con la regla de triggering nos permite definir condiciones para ejecutar o no el DAG. Con la regla de triggering por defecto, para que se ejecute una tarea todas las previas tienen que estar ejecutadas successfully. Si alguna de las tareas previas es skipped, entonces la tarea tambien se skippea  
'''

def _pick_erp_system(**context):
    if context["execution_date"] < ERP_CHANGE_DATE:
        return "fetch_sales_old"
    else:
        return "fetch_sales_new"


def _latest_only(**context):
    now = pendulum.now("UTC")
    left_window = context["dag"].following_schedule(context["execution_date"])
    right_window = context["dag"].following_schedule(left_window)

    # Al lanzar la excepción AirflowSkipException, la DAG marcará la tarea como skipped
    if not left_window < now <= right_window:
        raise AirflowSkipException()


with DAG(
    dag_id="06_condition_dag",
    start_date=airflow.utils.dates.days_ago(3),
    schedule_interval="@daily",
) as dag:
    start = DummyOperator(task_id="start")

    pick_erp = BranchPythonOperator(
        task_id="pick_erp_system", python_callable=_pick_erp_system
    )

    fetch_sales_old = DummyOperator(task_id="fetch_sales_old")
    clean_sales_old = DummyOperator(task_id="clean_sales_old")

    fetch_sales_new = DummyOperator(task_id="fetch_sales_new")
    clean_sales_new = DummyOperator(task_id="clean_sales_new")

    join_erp = DummyOperator(task_id="join_erp_branch", trigger_rule="none_failed")

    fetch_weather = DummyOperator(task_id="fetch_weather")
    clean_weather = DummyOperator(task_id="clean_weather")

    join_datasets = DummyOperator(task_id="join_datasets")
    train_model = DummyOperator(task_id="train_model")

    latest_only = PythonOperator(task_id="latest_only", python_callable=_latest_only)

    deploy_model = DummyOperator(task_id="deploy_model")

    start >> [pick_erp, fetch_weather]
    pick_erp >> [fetch_sales_old, fetch_sales_new]
    fetch_sales_old >> clean_sales_old
    fetch_sales_new >> clean_sales_new
    [clean_sales_old, clean_sales_new] >> join_erp
    fetch_weather >> clean_weather
    [join_erp, clean_weather] >> join_datasets
    join_datasets >> train_model >> deploy_model # Notese como estamos declarando que deploy_model se tiene que ejecutar cuando train_model se ejecute satisfactoriamente y ...
    latest_only >> deploy_model # ... cuando latest_only sea tambien satisfactoria. Si la tarea se skippea, no se cumple la trigger condition, y se skippea deploy_model
