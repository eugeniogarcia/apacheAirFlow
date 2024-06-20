# Schedule

## Imagenes

### Airflow

Construimos la imagen de airflow:

```ps
podman build .

podman image ls
```

etiquetamos la imagen

```ps
podman tag 367a3d24a5cb mi-airflow:latest
```

### api apoyo

Hay una imagen que elata una api flask que retorna un dataset de eventos. La api usa pandas

la construimos:

```ps
podman build .

podman image ls
```

incluimos un tag

```ps
podman tag f2da1f852f48 eventos:latest

podman image prune
```

### Essamble

Con las imagenes construidas y etiquetadas podemos arrancar el essemble con:

```ps
podman-compose up -d
```

esto require de `podman-compose`:

```ps
pip install podman-compose
```

para para el conjunto de servicios que hemos arrancado:

```ps
podman-compose down
```

finalmente destacar como hemos indicado en el contenedor que implementa el scheduler estamos indicando la ruta en el _host_ de las dags. Notese como indicamos que se use la ruta como lectura/escritura:

```yaml
    volumes:
      - ./dags:/opt/airflow/dags:rw,z
      - logs:/opt/airflow/logs
      - data:/data
```

#### Explicación sobre build

En el docker-compose hay una serie de tags `build`. Con estos tags lo que estamos haciendo es construir la imagen que vamos a usar. Por ejemplo:

```yaml
webserver:
  build:
    context: docker/airflow-data
    args:
      AIRFLOW_BASE_IMAGE: *airflow_image
  image: localhost/mi-airflow:latest
```

con esto indicamos que se use la imagen `localhost/mi-airflow:latest`, y que si esta imagen no esta en el repositorio construyamos una. Con `context` indicamos la ruta donde estará el dockerfile para construir la imagen. con `args` lo que especificamos son parametros que pasaremos al dockerfile. Este ejemplo podemos ver en el docker file:

```txt
ARG AIRFLOW_BASE_IMAGE="apache/airflow:2.0.0-python3.8"
FROM ${AIRFLOW_BASE_IMAGE}

USER root
RUN mkdir -p /data && chown airflow /data

USER airflow
```

#### Explicación sobre variables de entorno

En el archivo compose declaramos una serie de variables de entorno en las que se configuran diferentes aspectos de Airflow:

```yaml
# ====================================== AIRFLOW ENVIRONMENT VARIABLES =======================================
x-environment: &airflow_environment
  - AIRFLOW__CORE__EXECUTOR=LocalExecutor
  - AIRFLOW__CORE__FERNET_KEY=YlCImzjge_TeZc7jPJ7Jz2pgOtb4yTssA1pVyqIADWg=
  - AIRFLOW__CORE__LOAD_DEFAULT_CONNECTIONS=False
  - AIRFLOW__CORE__LOAD_EXAMPLES=False
  - AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql://airflow:airflow@postgres:5432/airflow
  - AIRFLOW__CORE__STORE_DAG_CODE=True
  - AIRFLOW__CORE__STORE_SERIALIZED_DAGS=True
  - AIRFLOW__WEBSERVER__EXPOSE_CONFIG=True
  - AIRFLOW_CONN_MY_POSTGRES=postgresql://airflow:airflow@wiki_results:5432/airflow

x-airflow-image: &airflow_image apache/airflow:2.0.0-python3.8
# ====================================== /AIRFLOW ENVIRONMENT VARIABLES ======================================
```

destacar:

- Variables donde configuramos que el metadato de Airflow sea postgress - en lugar de sqllite, que es el dedefto -, y más concretamente la conexión `postgresql://airflow:airflow@postgres:5432/airflow`
- Variable donde creamos una conexión a Postgress, al Postgress donde alojamos los datos de la wikipedia - `AIRFLOW_CONN_MY_POSTGRES` -, y que referenciaremos desde el operador `PostgresOperator` que tenemos en el `listing_4_20`

En los servicios que creamos hacemos referencia a estas variables de entorno. Por ejemplo, en el comando de inicialización de Airflow - que ejecutamos una vez la imagen de postgress esta corriendo:

```yaml

  init:
    build:
      context: docker
      args:
        AIRFLOW_BASE_IMAGE: *airflow_image
    image: localhost/mi-airflow:latest
    depends_on:
      - postgres
    environment: *airflow_environment
    entrypoint: /bin/bash
    command: -c 'airflow db init && airflow users create --username admin --password admin --firstname Anonymous --lastname Admin --role Admin --email egsmartin@gmail.com'
```

hacemos referencia a las variables con el puntero `*airflow_environment`
