import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from code1 import load_games, load_players, load_openings, clean_data, display_statistics, predict_winner, analyze_openings, cluster_games
from DataCollection.ProcessPGN import insertDataToPostgres

# Fonction principale
def main():
    # Connexion à la base de données
    engine = create_engine("postgresql+psycopg2://Ndeye659:@s0.net.pimous.dev:31003/shallowview", connect_args={
        "sslmode": "require",
        "sslcert":"C:\\Users\\ASUS\\Downloads\\Ndeye659.crt" ,
        "sslkey": "C:\\Users\\ASUS\\Downloads\\Ndeye659.key",
        "sslrootcert":"C:\\Users\\ASUS\\Downloads\\pimousdev-db.chain.crt"  
    })
    
    # Chargement des données
    games = load_games(engine)
    players = load_players(engine)
    openings = load_openings(engine)
    
    # Nettoyage des données
    games = clean_data(games)

    # Visualisation et analyse
    display_statistics(games)
    predict_winner(games)
    analyze_openings(engine)
    cluster_games(games)


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
