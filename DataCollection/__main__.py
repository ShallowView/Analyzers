from ProcessPGN import *

# INPUT FILES
PGNFiles = ["Datasets/lichess_elite_2020-06.pgn",
            "Datasets/lichess_elite_2020-07.pgn",
            "Datasets/lichess_elite_2020-08.pgn"]
PGNFile = "Datasets/lichess_elite_2020-09.pgn"

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

# Names of the tables in the database
tables = {
    "games": "games",
    "players": "players",
    "openings": "openings"
}

# Limits total number of cores used in multiprocessing, by default it uses all available cores - 1, reduce if needed
setMaxCores()

addOpeningsToDatabase(lichessOpeningTSVs, db_params, tables)

addNewPGNtoDatabase(PGNFiles, db_params, tables)
addNewPGNtoDatabase([PGNFile], db_params, tables)