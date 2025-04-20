import pandas as pd
from psycopg2 import sql

def insert_data(connection, table_name : str, dataframe : pd.DataFrame):
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