# Ejemplos

- test_dag_integrity.py. Ejemplo básico que nos demuestra como cargar programáticamente en módulo python, inspeccionar su contenido y ejecutar un test. En este ejemplo además vemos como especificamente como comprobar que un DAG no tenga loops - Airflow hace la comprobación en tiempo de ejecución; Con este test se pretende anticipar posibles errores antes de que se despliegue la DAG. Por último señalar que en este ejemplo usamos la anotación @pytest.mark.parametrize para ejecutar un test varias veces, especificando el valor de los argumentos de entrada al test method
- test_operators.py
- test_json_to_csv_operator
- test_movielens_operator.py
- test_movielens_operator2.py
