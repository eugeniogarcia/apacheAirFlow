import os
import time

import pandas as pd

from flask import Flask, jsonify, request
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

DEFAULT_ITEMS_PER_PAGE = 100

#crea un pandas dataframe a partir de un archivo, toma una muestra de datos y los ordena por ts, usuario y pelicula
def _read_ratings(file_path):
    ratings = pd.read_csv(file_path)

    # Subsample dataset.
    ratings = ratings.sample(n=100000, random_state=0)

    # Sort by ts, user, movie for convenience.
    ratings = ratings.sort_values(by=["timestamp", "userId", "movieId"])

    return ratings

app = Flask(__name__)
#Carga los datos
app.config["ratings"] = _read_ratings("/ratings.csv")

'''
Toma las credenciales de variables de entorno; La contraseña la hashea. Este metodo toma la contraseña, el añade un salt aleatorio, y la hashea. Lo que devuelve el metodo es algoritmo$salt$hash
'''
auth = HTTPBasicAuth()
users = {os.environ["API_USER"]: generate_password_hash(os.environ["API_PASSWORD"])}

#Comprueba que el usuario este en la lista, y que la contraseña sea valida. La contraseña esta en plain test, y la contrastamos con la version hasheada 
@auth.verify_password
def verify_password(username, password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False


@app.route("/")
def hello():
    return "Hello from the Movie Rating API!"


#Api no anonima
@app.route("/ratings")
@auth.login_required
def ratings():
    """
    Returns ratings from the movielens dataset.

    Parameters
    ----------
    start_date : str
        Start date to query from (inclusive).
    end_date : str
        End date to query upto (exclusive).
    offset : int
        Offset to start returning data from (used for pagination).
    limit : int
        Maximum number of records to return (used for pagination).
    """
    #Convierte a date time
    start_date_ts = _date_to_timestamp(request.args.get("start_date", None))
    end_date_ts = _date_to_timestamp(request.args.get("end_date", None))

    #Toma el offset y el tamaño de paginacion
    offset = int(request.args.get("offset", 0))
    limit = int(request.args.get("limit", DEFAULT_ITEMS_PER_PAGE))

    #Toma los datos
    ratings_df = app.config.get("ratings")

    #Filtra los datos por fechas
    if start_date_ts:
        ratings_df = ratings_df.loc[ratings_df["timestamp"] >= start_date_ts]

    if end_date_ts:
        ratings_df = ratings_df.loc[ratings_df["timestamp"] < end_date_ts]

    #Toma la pagina de datos que "toca"
    subset = ratings_df.iloc[offset : offset + limit]

    #Retorna un json
    return jsonify(
        {
            "result": subset.to_dict(orient="records"),
            "offset": offset,
            "limit": limit,
            "total": ratings_df.shape[0],
        }
    )


def _date_to_timestamp(date_str):
    if date_str is None:
        return None
    return int(time.mktime(time.strptime(date_str, "%Y-%m-%d")))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
