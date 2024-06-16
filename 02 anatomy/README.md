# Chapter 2

## instalacion local

```ps
pip install apache-airflow
```

inicializamos la base de datos de airflow:

```ps
airflow db init
```

creamos un usuario administrador

```ps
airflow users create --username admin --password admin --firstname Anonymous --lastname Admin --role Admin --email egsmartin@gmail.com
```

copiamos el dag:

```ps
cp download_rocket_launches.py ~/airflow/dags/
```

arancamos el servidor y el scheduler:

```ps
airflow webserver

airflow scheduler
```