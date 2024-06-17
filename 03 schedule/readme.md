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
