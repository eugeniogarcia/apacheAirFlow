import glob
import importlib.util
import os

import pytest
from airflow.models import DAG

# Crea una lista con todos los archivos py en el directorio ../../dags 
DAG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "dags/**.py")
DAG_FILES = glob.glob(DAG_PATH)


@pytest.mark.parametrize("dag_file", DAG_FILES) # lanzamos un test para cada uno de los elementos de la lista DAG_FILES
def test_dag_integrity(dag_file):
    
    # obtiene el nombre y la ruta del archivo
    module_name, _ = os.path.splitext(dag_file)
    module_path = os.path.join(DAG_PATH, dag_file)

    # carga el modulo python
    mod_spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(mod_spec)
    mod_spec.loader.exec_module(module)

    # crea una lista con todos los componentes del modulo que implementen la clase DAG
    dag_objects = [var for var in vars(module).values() if isinstance(var, DAG)]
    
    # comprobacion 1. Comprobamos que la lista no este vacia
    assert dag_objects

    # comprobacion 2. Para cada DAG hacemos el test que chequea que no haya loops en el DAG 
    for dag in dag_objects:
        # Test cycles
        dag.test_cycle()
