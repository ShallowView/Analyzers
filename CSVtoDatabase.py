import pandas as pd
import psycopg2
from psycopg2 import sql

def load_csv_to_dataframe(csv_file_path):
    """
    Load a CSV file into a pandas DataFrame.
    """
    return pd.read_csv(csv_file_path)

def create_table(connection, table_name, dataframe):
    """
    Create a table in the PostgreSQL database based on the DataFrame's structure.
    """
    columns = ", ".join(
        f"{col} TEXT" for col in dataframe.columns
    )  # Adjust data types as needed
    create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns});"

    with connection.cursor() as cursor:
        cursor.execute(create_table_query)
        connection.commit()

def insert_data(connection, table_name, dataframe):
    """
    Insert data from a pandas DataFrame into the PostgreSQL table.
    """
    with connection.cursor() as cursor:
        for _, row in dataframe.iterrows():
            insert_query = sql.SQL(
                f"INSERT INTO {table_name} ({', '.join(dataframe.columns)}) VALUES ({', '.join(['%s'] * len(row))})"
            )
            cursor.execute(insert_query, tuple(row))
        connection.commit()

# Example usage
if __name__ == "__main__":
    # Database connection parameters
    db_params = {
        "dbname": "your_database",
        "user": "your_username",
        "password": "your_password",
        "host": "localhost",
        "port": 5432
    }

    # File and table details
    csv_file_path = "lichess_elite_2020-06_players.csv"
    table_name = "players"

    # Connect to the database
    connection = psycopg2.connect(**db_params)

    try:
        # Load CSV into DataFrame
        df = load_csv_to_dataframe(csv_file_path)

        # Create table
        create_table(connection, table_name, df)

        # Insert data
        insert_data(connection, table_name, df)

    finally:
        connection.close()