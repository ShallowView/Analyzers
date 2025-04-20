import pandas as pd
import psycopg2

from ProcessPGN import *

# INPUT FILES
PGNFile = "Datasets/lichess_elite_2020-06.pgn"
lichessOpeningTSVs = ["Datasets/a.tsv", "Datasets/b.tsv", "Datasets/c.tsv", "Datasets/d.tsv", "Datasets/e.tsv"]

# OUTPUT FILES
PlayersCSV = "tmp/players.csv"
GamesCSV = "tmp/games.csv"
OpeningsCSV = "tmp/openings.csv"

# Database connection parameters
db_params = {
    "dbname": "chess",
    "user": "docker",
    "password": "docker",
    "host": "localhost",
    "port": 5432
}

# Read PGN file and convert to DataFrame
rawPGN = PGNtoDataFrame(PGNFile)

# Create DataFrames for players, openings, and games
players = createPlayersDataFrame(rawPGN)
openings = createOpeningsDataFrame(lichessOpeningTSVs)
games = createGamesDataFrame(rawPGN, players, openings)

# Save DataFrames to CSV files
players.to_csv(PlayersCSV, index=False)
games.to_csv(GamesCSV, index=False)
openings.to_csv(OpeningsCSV, index=False)

# Connect to the database
connection = psycopg2.connect(**db_params)

# Insert data into PostgreSQL tables
insertDataToPostgres(connection, "player", players)
insertDataToPostgres(connection, "opening", openings)
insertDataToPostgres(connection, "game", games)