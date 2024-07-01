import csv
import json
from pathlib import Path

from airflowbook.operators.json_to_csv_operator import JsonToCsvOperator

'''
Demuestra como utilizar la fixture por defecto de pytest que nos ofrece la posibilidad de trabajar con el filesystem de forma temporal - filesystem que se elimina tras la ejecución del test.

Para más información de las fixtures de pytest podemos consultar https://docs.pytest.org/en/6.2.x/fixture.html
'''

# Usamos la fixture por defecto tmp_path para acceder a un directorio temporal
def test_json_to_csv_operator(tmp_path: Path):
    print(tmp_path.as_posix())

    # especificamos los dos parametros que el operador que queremos testear usa, empleando el directorio temporal
    input_path = tmp_path / "input.json"
    output_path = tmp_path / "output.csv"

    # Write input data to tmp path
    input_data = [
        {"name": "bob", "age": "41", "sex": "M"},
        {"name": "alice", "age": "24", "sex": "F"},
        {"name": "carol", "age": "60", "sex": "F"},
    ]

    # creamos los datos en el fichero de entrada del operador que queremos testear
    with open(input_path, "w") as f:
        f.write(json.dumps(input_data))

    # testeamos el operador
    operator = JsonToCsvOperator(task_id="test", input_path=input_path, output_path=output_path)
    operator.execute(context={})

    # vamos a verificar si el test es ok o no, mirando el contenido del archivo de salida
    with open(output_path, "r") as f:
        reader = csv.DictReader(f)
        result = [dict(row) for row in reader]

    # Assert
    assert result == input_data
