#!/bin/bash

# Inspired by https://github.com/mrts/docker-postgresql-multiple-databases/blob/master/create-multiple-postgresql-databases.sh
# DB names hardcoded, script is created for demo purposes.

set -euxo pipefail

function create_user_and_database() {
	local database=$1
	echo "Creando el usuario '$database' con la  base de datos '$database'."
	psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE USER $database WITH PASSWORD '$database';
    CREATE DATABASE $database;
    GRANT ALL PRIVILEGES ON DATABASE $database TO $database;
EOSQL
}

# 1. Create databases
echo "Hacemos create_user_and_database"
create_user_and_database "insideairbnb"
echo "Fin create_user_and_database"

# 2. Create table for insideairbnb listings
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" insideairbnb <<-EOSQL
CREATE TABLE IF NOT EXISTS listings(
  id                             VARCHAR(20),
  name                           TEXT,
  host_id                        INTEGER,
  host_name                      VARCHAR(100),
  neighbourhood_group            VARCHAR(100),
  neighbourhood                  VARCHAR(100),
  latitude                       NUMERIC(18,16),
  longitude                      NUMERIC(18,16),
  room_type                      VARCHAR(100),
  price                          INTEGER,
  minimum_nights                 INTEGER,
  number_of_reviews              INTEGER,
  last_review                    DATE,
  reviews_per_month              NUMERIC(5,2),
  calculated_host_listings_count INTEGER,
  availability_365               INTEGER,
  number_of_reviews_ltm          INTEGER,
  license                        VARCHAR(100),
  xxxx1                        VARCHAR(100)
);
EOSQL

# 3. Download Inside Airbnb Amsterdam listings data (http://insideairbnb.com/get-the-data.html)
listing_url="http://data.insideairbnb.com/the-netherlands/north-holland/amsterdam/{DATE}/visualisations/listings.csv"

listing_dates="
2024-03-11
2023-12-12
2023-09-03
2023-06-05
"

mkdir -p /tmp/insideairbnb
for d in ${listing_dates}
do
  url=${listing_url/\{DATE\}/$d}
  wget $url -O /tmp/insideairbnb/listing-$d.csv || true

  # Hacky way to add the "download_date", by appending the date to all rows in the downloaded file
  sed -i "1 s/$/,download_date/" /tmp/insideairbnb/listing-$d.csv
  sed -i "2,$ s/$/,$d/" /tmp/insideairbnb/listing-$d.csv

  psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" insideairbnb <<-EOSQL
    COPY listings FROM '/tmp/insideairbnb/listing-$d.csv' DELIMITER ',' CSV HEADER QUOTE '"';
EOSQL
done

function grant_all() {
	local database=$1
  echo "Cambiando el owner del esquema public a '$database'"
  echo "Asignando permisos al usuario '$database'"
	psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" $database <<-EOSQL
    ALTER SCHEMA public OWNER TO $database;
    GRANT USAGE ON SCHEMA public TO $database;
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $database;
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $database;
    GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO $database;
EOSQL
}

# Somehow the database-specific privileges must be set AFTERWARDS
echo "Hacemos grant_all"
grant_all "insideairbnb"
echo "Fin"

pg_ctl stop
