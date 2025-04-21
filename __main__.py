import pandas as pd
import psycopg2

from ProcessPGN import *

# INPUT FILES
PGNFiles = ["Datasets/lichess_elite_2020-06.pgn",
            "Datasets/lichess_elite_2020-07.pgn",
            "Datasets/lichess_elite_2020-08.pgn"]
lichessOpeningTSVs = ["Datasets/a.tsv",
                      "Datasets/b.tsv",
                      "Datasets/c.tsv",
                      "Datasets/d.tsv",
                      "Datasets/e.tsv"]

# Database connection parameters
db_params = {
    "dbname": "chess",
    "user": "docker",
    "password": "docker",
    "host": "localhost",
    "port": 5432
}

# Limits total number of cores used, by default it uses all available cores - 1
setMaxCores()

# Connect to the database
connection = psycopg2.connect(**db_params)

# Read PGN file and convert to DataFrame
rawPGN = PGNtoDataFrame(PGNFiles)

# Create DataFrame for openings and insert into PostgreSQL
openings = createOpeningsDataFrame(lichessOpeningTSVs)
insertDataToPostgres(db_params, "openings", openings)

with connection.cursor() as cursor:
    cursor.execute("SELECT id, name, title, max_elo FROM players")
    DBplayers = pd.DataFrame(cursor.fetchall(), columns=["id", "name", "title", "max_elo"])

# Create DataFrame for new players and insert into PostgreSQL
players = createPlayersDataFrame(rawPGN, DBplayers)
insertDataToPostgres(db_params, "players", players)

# Get updated player and opening data from the database
with connection.cursor() as cursor:
    cursor.execute("SELECT id, name FROM players")
    players = pd.DataFrame(cursor.fetchall(), columns=["id", "name"])

    cursor.execute("SELECT id, name, pgn FROM openings")
    openings = pd.DataFrame(cursor.fetchall(), columns=["id", "name", "pgn"])

# Create the games DataFrame and insert into PostgreSQL
games = createGamesDataFrame(rawPGN, players, openings)
insertDataToPostgres(db_params, "games", games)

# Update players' max ELO in the database
with connection.cursor() as cursor:
    cursor.execute("SELECT update_players_max_elo()")
    connection.commit()

connection.close()