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
