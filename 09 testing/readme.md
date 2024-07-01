# Ejemplos

- `test_dag_integrity.py. Ejemplo básico que nos demuestra como cargar programáticamente en módulo python, inspeccionar su contenido y ejecutar un test. En este ejemplo además vemos como especificamente como comprobar que un DAG no tenga loops - Airflow hace la comprobación en tiempo de ejecución; Con este test se pretende anticipar posibles errores antes de que se despliegue la DAG. Por último señalar que en este ejemplo usamos la anotación @pytest.mark.parametrize para ejecutar un test varias veces, especificando el valor de los argumentos de entrada al test method

- `conftest.py`. Archivo de configuración en el que podemos incluir fixtures y/o helpers que usaremos en nuestros tests. El archivo puede ubicarse en diferentes subdirectorios, pytest aplicara la configuración a los tests definidos "debajo" en la jerarquia

- `test_operators.py`. Demuestra como podemos utilizar un mock. Usa pytest-mock para definir mocks de funciones en clases. Vemos como construir el mock y como comprobar si se ha llegado a llamar, y con que argumentos se ha llamado al mock

- test_json_to_csv_operator. Demuestra como usar la fixture por defecto que nos permite usar un filesytem temporal - podremos escribir y leer archivos de esta ruta, y cuando el caso de prueba/test function termine, el directorio temporal y sus contenidos se eliminan, de modo que podemos repetir el caso de prueba las veces que queramos

- `test_movielens_operator.py`. 

- `test_movielens_operator2.py`. 
