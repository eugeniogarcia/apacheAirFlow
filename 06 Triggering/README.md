# Ejemplos

- ejemplo 1.py y ejemplo 2.py - Demuestran el uso de sensores (FileSensor y PythonSensor)
- ejemplo 3.py - Indica que hay dos modos de ejecutar un sensor, poke - por defecto - o rescheduled
- ejemplo 4.py - Demuestra como evitar tareas kilometricas que corresponden a diferentes bloques funcionales en un DAG haciendo que un DAG llame a otro DGA
- ejemplo 5.py y ejemplo 6.py - demuestra como poder esperar en un DAG por el fin de otra tarea en otro DAG. Se trata de un sensor intre DAGs. En el ejemplo 6 podemos ver que hacer cuando los dos DAGs que queremos referenciar no tienen la misma schedule
- ejemplo 7. Ejecutar un DAG desde el CLI de Airflow o usando la API REST de Airflow

## ejemplo 7. Llamada REST

Para hacer la llamada, hacemos un POST a:

<http://localhost:8080/api/v1/dags/<nombre del dag>/dagRuns>

en nuestro caso será:

localhost:8080/api/v1/dags/listing_6_08/dagRuns

Usamos basic authentication, usando admin, admin. Como payload pasamos:

```json
{
    "conf":{
        "nombre":"eugenio",
        "apellido":"garcia san martin"
    }
}
```

esto dispara la ejecución de nuestro DAG. Entre los datos de contexto, en la propiedad `dag_run` tendremos un atributo `conf`:

```py
print(context["dag_run"].conf)
```