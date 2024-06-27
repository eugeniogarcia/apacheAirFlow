import logging
from pathlib import Path
import tempfile
from urllib.request import urlretrieve
import zipfile

import click
import pandas as pd

#Configura el logging
logging.basicConfig(
    format="[%(asctime)-15s] %(levelname)s - %(message)s", level=logging.INFO
)

#Usamos click para definir el CLI. Indicamos los argumentos que se esperan, su tipo, si son obligatorios, y el valor por defecto
@click.command()
@click.option("--start_date", default="2019-01-01", type=click.DateTime())
@click.option("--end_date", default="2020-01-01", type=click.DateTime())
@click.option("--output_path", required=True)
def main(start_date, end_date, output_path):
    """Script for fetching movielens ratings within a given date range."""

    logging.info("Fetching ratings...")
    ratings = fetch_ratings()

    # Subset to expected range.
    logging.info(f"Filtering for dates {start_date} - {end_date}...")
    #convierte la serie timestamp en un datetime
    ts_parsed = pd.to_datetime(ratings["timestamp"], unit="s")
    #nos quedamos con los datos entre las fechas de inicio y fin
    ratings = ratings.loc[(ts_parsed >= start_date) & (ts_parsed < end_date)]

    #Guarda los datos como csv
    logging.info(f"Writing ratings to '{output_path}'...")
    ratings.to_csv(output_path, index=False)


def fetch_ratings():
    """Fetches ratings from the given URL."""

    url = "http://files.grouplens.org/datasets/movielens/ml-25m.zip"

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir, "download.zip")
        logging.info(f"Downloading zip file from {url}")
        urlretrieve(url, tmp_path)

        with zipfile.ZipFile(tmp_path) as zip_:
            logging.info(f"Downloaded zip file with contents: {zip_.namelist()}")

            logging.info("Reading ml-25m/ratings.csv from zip file")
            with zip_.open("ml-25m/ratings.csv") as file_:
                ratings = pd.read_csv(file_)

    return ratings


if __name__ == "__main__":
    main()
