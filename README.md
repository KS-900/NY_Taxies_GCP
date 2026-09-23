# NY Taxis GCP

Infrastructure and local data-ingestion setup for the New York City taxi data project.

## Project Overview

This project combines:

- Google Cloud Storage for raw taxi files
- BigQuery for analytical data
- PostgreSQL for local ingestion and development
- Kestra for workflow orchestration
- pgAdmin for local PostgreSQL administration

Terraform creates the Google Cloud Storage bucket and BigQuery dataset. Docker Compose runs the local PostgreSQL, Kestra, and pgAdmin services. The Python script loads one CSV file and one Parquet file into PostgreSQL.

## Prerequisites

- Docker Desktop with Docker Compose
- Terraform
- Python 3.10 or later
- A Google Cloud project with billing enabled
- A Google Cloud service-account key with permissions to create or manage the configured bucket and dataset

The repository contains a local virtual environment in taxi_env. Do not commit service-account keys or other credentials to source control.

## Google Cloud Setup

1. Review the defaults in variable.tf, especially project, region, location, and gcs_bucket_name.
2. Make sure the bucket name is globally unique.
3. Confirm that keys/ny-creds.json contains the service-account key referenced by credentials.
4. Initialize and apply Terraform:

powershell:
terraform init
terraform plan
terraform apply


To remove the resources created by Terraform:

powershell
terraform destroy

## Start Local Services

Start the local PostgreSQL, Kestra, and pgAdmin services from the project directory:

powershell:
docker compose up -d

Available services:

| Service | URL or connection |
| PostgreSQL | localhost:5432 |
| pgAdmin | http://localhost:8085 |
| Kestra | http://localhost:8080 |

Default local PostgreSQL settings from `docker-compose.yml`:

Host: localhost
Port: 5432
Database: ny_taxi
User: root
Password: root


Stop the services with:

powershell:
docker compose down


Use docker compose down -v only when you also want to remove the named database and Kestra volumes.

## BigQuery Workflow

This is the BigQuery workflow used for the Yellow Taxi data in the project. It creates an external table backed by files in Google Cloud Storage, previews the data, and then creates non-partitioned and partitioned tables for analysis.

```sql
-- Create an external table referencing files in GCS
CREATE OR REPLACE EXTERNAL TABLE `ny-rides-alexey-507306.ny_taxi_data.external_yellow_tripdata`
OPTIONS (
  format = 'CSV',
  uris = [
    'gs://ny-rides-alexey-507306-bucket/Trips/yellow_tripdata_2019-01.csv'
  ]
);

-- Preview yellow trip data from the external table
SELECT *
FROM `ny-rides-alexey-507306.ny_taxi_data.external_yellow_tripdata`
LIMIT 10;

-- Create a non-partitioned table from the external table
CREATE OR REPLACE TABLE `ny-rides-alexey-507306.ny_taxi_data.yellow_tripdata_non_partitioned AS
SELECT *
FROM `ny-rides-alexey-507306.ny_taxi_data.external_yellow_tripdata`;

-- Create a partitioned table from the external table
CREATE OR REPLACE TABLE `ny-rides-alexey-507306.ny_taxi_data.yellow_tripdata_partitioned`
PARTITION BY DATE(tpep_pickup_datetime) AS
SELECT *
FROM `ny-rides-alexey-507306.ny_taxi_data.external_yellow_tripdata`;

-- Inspect data in the partitioned table
SELECT DISTINCT(VendorID)
FROM `ny-rides-alexey-507306.ny_taxi_data.yellow_tripdata_non_partitioned`
WHERE DATE(tpep_pickup_datetime) BETWEEN '2019-01-01' AND '2019-01-31';
```

This approach lets you query raw data stored in GCS without importing everything up front, then materialize the cleaned data into BigQuery tables for better performance and cost control.

## Ingest Local Data

The ingestion script reads paths from environment variables and requires these values:

pg_user=root
pg_password=root
pg_database=ny_taxi
csv_file_path=./taxi_zone_lookup.csv
parquet_file_path=./path/to/green_tripdata.parquet

Create a .env file in the project root with the values for your local files, then run:

powershell
& .\taxi_env\Scripts\Activate.ps1
python .\scripts\ingest.py

The script creates and populates these PostgreSQL tables:

- taxi_zone_lookup
- green_tripdata_2025_11

### PostgreSQL Port Note

The Compose file publishes PostgreSQL on host port 5432, while scripts/ingest.py currently connects to host port 5433. Update one of those values before running ingestion so they match. The simplest local setup is to change the script connection port to 5432.

## Useful Commands

Check running containers:

powershell:
docker compose ps

View service logs:

powershell:
docker compose logs -f kestra


Format and validate Terraform:

powershell
terraform fmt
terraform validate

## Repository Layout

main.tf                 Google Cloud resources
variable.tf             Terraform variables and defaults
docker-compose.yml      Local PostgreSQL, Kestra, and pgAdmin services
scripts/ingest.py       CSV and Parquet ingestion script
taxi_zone_lookup.csv    Taxi zone lookup data
keys/                   Local service-account credentials

Keep `keys/` and `.env` files private, and rotate any credentials that may have been exposed.

