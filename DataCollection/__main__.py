from ProcessPGN import *

# INPUT FILES
PGNFiles = ["Datasets/lichess_elite_2024-06.pgn",
            "Datasets/lichess_elite_2024-07.pgn",
            "Datasets/lichess_elite_2024-08.pgn"]
PGNFiles2 = ["Datasets/lichess_elite_2024-09.pgn",
            "Datasets/lichess_elite_2024-10.pgn",
            "Datasets/lichess_elite_2024-11.pgn"]
PGNFiles3 = ["Datasets/lichess_elite_2024-12.pgn",
            "Datasets/lichess_elite_2025-01.pgn",
            "Datasets/lichess_elite_2025-02.pgn"]

lichessOpeningTSVs = ["Datasets/a.tsv",
                      "Datasets/b.tsv",
                      "Datasets/c.tsv",
                      "Datasets/d.tsv",
                      "Datasets/e.tsv"]

# Database connection parameters
db_params_SSL = {
    "dbname": "shallowview",
    "user": "user", # Replace with your database username
    "password": "password", # Replace with your database password
    "host": "s0.net.pimous.dev",
    "port": 31003,
    "sslmode": "require",  # Enforce SSL connection
    "sslcert": "path/client-certificate.crt",  # Path to client certificate
    "sslkey": "path/client-key.key",    # Path to client private key
    "sslrootcert": "path/CA-certificate.chain.crt"   # Path to CA certificate
}

db_params_local = {
    "dbname": "postgres",
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

# Limits total number of cores used in multiprocessing, by default it's ~80% of the cores, reduce if needed
setMaxCores()

addOpeningsToDatabase(lichessOpeningTSVs, db_params_SSL, tables)

addNewPGNtoDatabase(PGNFiles, db_params_SSL, tables)
addNewPGNtoDatabase(PGNFiles2, db_params_SSL, tables)
addNewPGNtoDatabase(PGNFiles3, db_params_SSL, tables)