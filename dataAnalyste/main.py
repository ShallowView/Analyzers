import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

from code1 import load_games, load_players, load_openings, clean_data, display_statistics, predict_winner, analyze_openings, cluster_games, generate_player_profile
#from DataCollection.ProcessPGN import insertDataToPostgres

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
    generate_player_profile(player_name, engine)




if __name__ == "__main__":
    main()
