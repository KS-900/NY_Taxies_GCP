# this script will ingest one csv file and one parquet file that is locally located into the postgres database
import os
from dotenv import load_dotenv
import pandas as pd
import psycopg2

load_dotenv()

def _db_requirements():
    """
    This function checks if the required environment variables are set.
    If any of the required variables are missing, it raises an exception.
    """
    required_vars = ["pg_user", "pg_password", "pg_database"]
    for var in required_vars:
        if not os.getenv(var):
            raise EnvironmentError(f"Required environment variable '{var}' is not set.")
    return required_vars

def fetch_data_from_csv():
    """
    This function reads a CSV file and returns a pandas DataFrame.
    """
    try:
        df = pd.read_csv(os.getenv("csv_file_path"))
        return df
    except Exception as e:
        raise RuntimeError(f"Error reading CSV file: {e}")

def fetch_data_from_parquet():
    """
    This function reads a Parquet file and returns a pandas DataFrame.
    """
    try:
        df = pd.read_parquet(os.getenv("parquet_file_path"))
        return df
    except Exception as e:
        raise RuntimeError(f"Error reading Parquet file: {e}")
    
def create_connection():
    """
    This function creates a connection to the PostgreSQL database using credentials from environment variables.
    """
    try:
        conn = psycopg2.connect(
            user=os.getenv("pg_user"),
            password=os.getenv("pg_password"),
            dbname=os.getenv("pg_database"),
            port=5433,  # default PostgreSQL port
            host="localhost" # assuming the database is running on the local machine
        )
        return conn
    except Exception as e:
        raise ConnectionError(f"Error connecting to the database: {e}")

def ingest_data_to_postgres(df, table_name):
    """
    This function ingests a pandas DataFrame into a PostgreSQL table.
    If the table does not exist, it will be created.
    """
    conn = create_connection()
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        {', '.join([f"{col} TEXT" for col in df.columns])}
    );
    """
    cursor.execute(create_table_query)
    
    # Insert data into the table
    for index, row in df.iterrows():
        insert_query = f"""
        INSERT INTO {table_name} ({', '.join(df.columns)}) 
        VALUES ({', '.join(['%s'] * len(row))});
        """
        cursor.execute(insert_query, tuple(row))
    
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    _db_requirements()
    
    # Ingest CSV data
    csv_df = fetch_data_from_csv()
    ingest_data_to_postgres(csv_df, "taxi_zone_lookup")
    
    # Ingest Parquet data
    parquet_df = fetch_data_from_parquet()
    ingest_data_to_postgres(parquet_df, "green_tripdata_2025_11")