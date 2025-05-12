import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from code1 import load_games, load_players, load_openings, clean_data, display_statistics, predict_winner, analyze_openings, cluster_games
from DataCollection.ProcessPGN import insertDataToPostgres




from utils.insert import insertDataToPostgres  # adapte le chemin selon ton projet

def main():
    engine = get_engine()  # ta fonction psycopg2 ou sqlalchemy
    games, players, openings = load_data()  # récupère les données
    
    # Insertion en base
    connection_params = {
        "dbname": "your_db",
        "user": "your_user",
        "password": "your_password",
        "host": "localhost",
        "port": "5432",
        "sslmode": "prefer",
        "sslrootcert": r"C:\chemin\certs\root.crt",
        "sslcert": r"C:\chemin\certs\client.crt",
        "sslkey": r"C:\chemin\certs\client.key"
    }

    insertDataToPostgres(connection_params, "games", games)
    insertDataToPostgres(connection_params, "players", players)
    insertDataToPostgres(connection_params, "openings", openings)


if __name__ == "__main__":
    main()
