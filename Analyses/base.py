
"""
Analyses -> format = <directory_acronym>/<elements_in_acronym> : <explanation>

T_TC/title_and_time_control : Finding a relation between the title and the time control

"""

import array
from ast import List
import json
from matplotlib.axes import Axes
from numpy import ndarray
import  plotly.tools as tools
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

"""
CONSTANTS
DB_STR              -> connection string/url for the connect function in psycopg ( not currently being used )
DB_STR_ENGINE       -> connection string/url for engine connection in sqlalchemy
TEST_ROW_COUNT      -> number of rows to query the database while testing
DEFAULT_STORAGE_DIR -> name of directory in every package that contains plots/findings of the analysis in question
"""
load_dotenv()
DB_STR_ENGINE : str = ""
TEST_ROW_COUNT : int = 10000 # for testing purposes, don't need to query entire database
DEFAULT_STORAGE_DIR="findings" # for admin zone

"""
Utiliy functions for ALL analyses (descriptions are in the function definitions)
"""

def fetch_data_from_sql(query : str, db_connection_string=DB_STR_ENGINE, chunk_size=10000) -> pd.DataFrame : 
    """
    Fetches data from a SQL database in chunks to handle large datasets efficiently.

    Args:
        query (str): The SQL query to execute.
        db_connection_string (str): The connection string for the database [ can be URL or normal connection string ]
        chunk_size (int, optional): The number of rows to fetch per chunk. Defaults to 10000.

    Returns:
        pd.DataFrame: A DataFrame containing the results of the query.
    """
    all_chunks = []
    engine = create_engine(db_connection_string)
    with engine.connect() as conn:
        for chunk_df in pd.read_sql_query(query, conn, chunksize=chunk_size):
            all_chunks.append(chunk_df)
    return pd.concat(all_chunks, ignore_index=True)

def fetch_sql_and_save_to_csv(query : str, output_csv_path: str, db_connection_string=DB_STR_ENGINE, chunk_size=10000) -> None:
    """
    Fetches data from a SQL database in chunks and saves the entire result to a CSV file.

    Args:
        query (str): The SQL query to execute.
        db_connection_string (str): The connection string for the database.
        output_csv_path (str): The path where the CSV file will be saved.
        chunk_size (int, optional): The number of rows to fetch per chunk. Defaults to 10000.
    """
    all_chunks = []
    engine = create_engine(db_connection_string)
    try:
        with engine.connect() as conn:
            for chunk_df in pd.read_sql_query(query, conn, chunksize=chunk_size):
                all_chunks.append(chunk_df)

        if all_chunks:
            combined_df = pd.concat(all_chunks, ignore_index=True)
            combined_df.to_csv(output_csv_path, index=False)
            print(f"Data from SQL query saved to: {output_csv_path}")
        else:
            print("No data returned from the SQL query.")

    except Exception as e:
        print(f"An error occurred while fetching data from SQL: {e}")
    
def calculate_value_distribution(df : pd.DataFrame, group_column : str, value_column : str, normalize=True) -> pd.DataFrame:
    """
    Calculates the distribution of a value column within groups of another column.

    Args:
        df (pd.DataFrame): The input DataFrame.
        group_column (str): The column to group by.
        value_column (str): The column whose distribution to calculate.
        normalize (bool, optional): Whether to normalize the counts to proportions. Defaults to True.

    Returns:
        pd.DataFrame: A DataFrame showing the distribution of the value column per group.
    """
    return df.groupby(group_column)[value_column].value_counts(normalize=normalize).unstack(fill_value=0)

def filter_insignificant_data(df : pd.DataFrame, threshold=0.10) -> pd.DataFrame:
    """
    Filters rows and columns in a DataFrame based on a minimum value threshold.

    Args:
        df (pd.DataFrame): The input DataFrame.
        threshold (float, optional): The minimum value for a row or column to be considered significant. Defaults to 0.10.

    Returns:
        pd.DataFrame: A DataFrame with rows and columns containing at least one value above the threshold.
    """
    filtered_rows = df[(df >= threshold).any(axis=1)]
    filtered_df = filtered_rows.loc[:, (filtered_rows >= threshold).any(axis=0)]
    return filtered_df

def filter_data_by_threshold(df: pd.DataFrame, row_threshold=None, col_threshold=None) -> pd.DataFrame:
    """
    Filters rows and columns in a DataFrame based on specified value thresholds.

    Args:
        df (pd.DataFrame): The input DataFrame.
        row_threshold (float, optional): The minimum value for a row to be considered significant
                                         (at least one value >= threshold). Defaults to None (no row filtering).
        col_threshold (float, optional): The minimum value for a column to be considered significant
                                         (at least one value >= threshold). Defaults to None (no column filtering).

    Returns:
        pd.DataFrame: A DataFrame with rows and columns meeting the specified thresholds.
    """
    filtered_df = df.copy()  # It's good practice to work on a copy

    if row_threshold is not None:
        filtered_rows = filtered_df[(filtered_df >= row_threshold).any(axis=1)]
        filtered_df = filtered_rows

    if col_threshold is not None:
        filtered_cols = filtered_df.loc[:, (filtered_df >= col_threshold).any(axis=0)]
        filtered_df = filtered_cols

    return filtered_df


"""
Admin configuration functions
"""

def set_storage_directory(storage_directory_name: str, magic_file_attribute) -> str:
    """Creates a storage directory path relative to a file's directory.

    Args:
        storage_directory_name: Name of the storage directory (e.g., "data").
        magic_file_attribute: The `__file__` attribute of a module.

    Returns:
        Full path to the storage directory: `<module_directory>/<storage_directory_name>/`.
    """
    current_dir_name = os.path.dirname(magic_file_attribute)
    os.makedirs(current_dir_name + "/" +  storage_directory_name, exist_ok=True)
    return current_dir_name + "/" +  storage_directory_name + "/"

"""
This is where wrapper functions for plots are to be placed
"""

def plot_heatmap(df : pd.DataFrame, title : str, xlabel  : str, ylabel : str, filename="heatus_mapus.png", annot=True, cmap='viridis', fmt=".2f", figsize=(10, 8)) -> Axes:
    """
    Generates and saves a heatmap plot from a DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to plot.
        title (str): The title of the heatmap.
        xlabel (str): The label for the x-axis.
        ylabel (str): The label for the y-axis.
        filename (str, optional): The name of the file to save the plot to. Defaults to "heatus_mapus.png".
        annot (bool, optional): Whether to display annotations on the heatmap cells. Defaults to True.
        cmap (str, optional): The colormap to use. Defaults to 'viridis'.
        fmt (str, optional): The format string for the annotations. Defaults to ".2f".
        figsize (tuple, optional): The figure size. Defaults to (10, 8).
    """
    plt.figure(figsize=figsize)
    axes_data : Axes = sns.heatmap(df, annot=annot, cmap=cmap, fmt=fmt)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    return axes_data

def plot_barplot(data : pd.DataFrame, lables_list , values_list, title: str, xlabel: str, ylabel: str, filename="barus_chartus.png", figsize=(10, 6), rotation=45, ha='right') -> Axes:
    """
    Generates and saves a bar plot using Seaborn.

    Args:
        data (pd.DataFrame): The data to plot. If a DataFrame,
                                         'x_col' and 'y_col' must be column names.
                                         Otherwise, 'x_col' will be treated as labels
                                         and 'y_col' as values.
        lables_list (str): The name of the column to use for the x-axis (or list of labels).
        values_list (str): The name of the column to use for the y-axis (or list of values).
        title (str): The title of the bar plot.
        xlabel (str): The label for the x-axis.
        ylabel (str): The label for the y-axis.
        filename (str, optional): The name of the file to save the plot to. Defaults to "barus_chartus.png".
        figsize (tuple, optional): The figure size. Defaults to (10, 6).
        rotation (int, optional): The rotation angle for x-axis labels. Defaults to 45.
        ha (str, optional): The horizontal alignment of x-axis labels. Defaults to 'right'.
    """
    plt.figure(figsize=figsize)
    axes_data : Axes = sns.barplot(x=data[lables_list], y=data[values_list])
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=rotation, ha=ha)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    return axes_data

def plot_scatter_biplot(title : str, row_coordinates : pd.DataFrame, columns_coordinates : pd.DataFrame, x_label : str = 'Component 1', y_label : str = 'Component 2', annotations = False, filepath :str  = "scatterplott_MCA_biplot.png"): 
    """
    
    """
    # need to process the row andd columns from the mca object after analysis
    row_coordinates.rename(columns={0: x_label, 1: y_label}, inplace=True)
    columns_coordinates.rename(columns={0: x_label, 1: y_label}, inplace=True)
    
    plottyman = plt.figure(figsize=(10, 10))
    sns.scatterplot(x=x_label, y=y_label, data=row_coordinates, label='Rows')
    sns.scatterplot(x=x_label, y=y_label, data=columns_coordinates, marker='^', color='red', label='Columns')
    if annotations:
        for i, row in columns_coordinates.iterrows():
            plt.annotate(row['index'], (row[x_label], row[y_label]), textcoords="offset points", xytext=(5,5), ha='left')
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()
    plt.grid(True)
    plottyman.savefig(filepath)

"""
This is where the counterpart functions for the JSON representation of the wrapper functions abovve will be placed
"""

"""
Other
"""

def file_exists(file_path: str) -> bool:
    """Checks if a file exists at the given path.

    Args:
        file_path: The path to the file to check (string).

    Returns:
        True if the file exists, False otherwise (boolean).
    """
    return os.path.exists(file_path) and os.path.isfile(file_path)