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