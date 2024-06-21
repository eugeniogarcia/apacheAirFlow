import airflow

from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator

ERP_CHANGE_DATE = airflow.utils.dates.days_ago(1)

'''
Tenemos dos logicas de negocio que queremos implementar en un determinado paso de la DAG. Por ejemplo, supongamos que a la hora de limpiar datos, los registros que nos descargamos tienen dos formatos diferentes dependiendo de la fecha en la que fueron generados.

Con el enfoque de este ejemplo tenemos dos tareas con cada una de las lógicas, y habrá una tarea previa de branching que decidirá por que rama hacer la ejecución. Hay una tarea nueva en la DAG, que usa un BranchPythonOperator y que tiene como misión devolver el id de la tarea que tiene que ejecutarse a continuación.

También es necesario cambiar la trigger rule por defecto de la tarea que se ejecuta después del limpiado de datos, para que sepa que no han de ejecutarse las dos tareas previas, sino solo una de ellas.

Visualmente veremos porque ruta se ejecuto la DAG.
'''

def _pick_erp_system(**context): # Paso 2. Esta funcion se usa con el BranchOperator - ver más abajo; Retorna el id de una tarea, el id de la tarea que tiene que ejecutarse a continuación
    if context["execution_date"] < ERP_CHANGE_DATE:
        return "fetch_sales_old"
    else:
        return "fetch_sales_new"


def _fetch_sales_old(**context):
    print("Fetching sales data (OLD)...")


def _fetch_sales_new(**context):
    print("Fetching sales data (NEW)...")


def _clean_sales_old(**context):
    print("Preprocessing sales data (OLD)...")


def _clean_sales_new(**context):
    print("Preprocessing sales data (NEW)...")


with DAG(
    dag_id="03_branch_dag",
    start_date=airflow.utils.dates.days_ago(3),
    schedule_interval="@daily",
) as dag:
    start = DummyOperator(task_id="start")

    pick_erp_system = BranchPythonOperator( # Paso 1. Usamos un branch operator. Este operador devuelve el id de la tarea que tiene que ejecutarse a continuación.
        task_id="pick_erp_system", python_callable=_pick_erp_system
    )

    fetch_sales_old = PythonOperator(
        task_id="fetch_sales_old", python_callable=_fetch_sales_old
    )
    clean_sales_old = PythonOperator(
        task_id="clean_sales_old", python_callable=_clean_sales_old
    )

    fetch_sales_new = PythonOperator(
        task_id="fetch_sales_new", python_callable=_fetch_sales_new
    )
    clean_sales_new = PythonOperator(
        task_id="clean_sales_new", python_callable=_clean_sales_new
    )

    fetch_weather = DummyOperator(task_id="fetch_weather")
    clean_weather = DummyOperator(task_id="clean_weather")

    # Using the wrong trigger rule ("all_success") results in tasks being skipped downstream.
    # join_datasets = DummyOperator(task_id="join_datasets")

    join_datasets = DummyOperator(task_id="join_datasets", trigger_rule="none_failed") # Paso 3. Esta tarea se dispara cuando todaslas tareas previas se han ejecutado sin fallos (es decir, en estado success o skipped); por defacto la trigger rule es all_success, lo que significa que todas las tareas previas se han tenido que ejecutar (es decir, todas las tareas previas tienen que estar en estado success)
    train_model = DummyOperator(task_id="train_model")
    deploy_model = DummyOperator(task_id="deploy_model")

    start >> [pick_erp_system, fetch_weather]
    pick_erp_system >> [fetch_sales_old, fetch_sales_new] # Paso 4. Despues de la tarea de branching se incluyen todas las tareas que pueden llegar a ejecutarse
    fetch_sales_old >> clean_sales_old
    fetch_sales_new >> clean_sales_new
    fetch_weather >> clean_weather
    [clean_sales_old, clean_sales_new, clean_weather] >> join_datasets # Paso 5. En la tarea join_datasets tendremos que cambiar la trigger_rule para indicar que se puede ejecutar si las previas estan skipped o succed - ver Paso 3
    join_datasets >> train_model >> deploy_model
