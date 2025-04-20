import pandas as pd

from CSVtoData import *
from DataToSQL import *

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

rawPGN = PGNtoDataFrame(PGNFile)

players = createPlayersDataFrame(rawPGN)
openings = createOpeningsDataFrame(lichessOpeningTSVs)
games = createGamesDataFrame(rawPGN, players, openings)

# Save DataFrames to CSV files
players.to_csv(PlayersCSV, index=False)
games.to_csv(GamesCSV, index=False)
openings.to_csv(OpeningsCSV, index=False)

# Connect to the database
connection = psycopg2.connect(**db_params)

insert_data(connection, "player", players)
insert_data(connection, "opening", openings)
# insert_data(connection, "game", games)