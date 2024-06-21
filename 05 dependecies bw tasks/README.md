# Chapter 5

Code accompanying Chapter 5 of the book 'Data pipelines with Apache Airflow'.

## Contents

This code example contains the following DAGs:

- 01_start.py - Initial DAG with several tasks.
- 02_branch_in_function.py - Branching within a function.
- 03_branch_in_dag.py - Branching within the DAG.
- 06_branch_in_dag.py - Condition within the DAG.
- 07_trigger_rules.py - DAG illustrating several trigger rules.
- 09_xcoms.py y 10_xcoms_template.py - Demuestra como usar XCom
- 12_taskflow.py - Demuestra como definir una tarea PythonOperator simplemente anotando una funcion; La definición del DAG se hace llamando a las funciones python
- 13_taskflow_full.py - Demuestra como usar los dos estilos de definición de las tareas en el dag, con anotaciones y operadores explicitos, para construir un DAG 

## Usage

To get started with the code examples, start Airflow in docker using the following command:

    docker-compose up -d --build

Wait for a few seconds and you should be able to access the examples at http://localhost:8080/.

To stop running the examples, run the following command:

    docker-compose down
