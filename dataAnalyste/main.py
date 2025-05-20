import pandas as pd
from sqlalchemy import create_engine
import time
import json

# Importez les fonctions d'analyse
from AnalyseML import (
    load_games, load_players, load_openings, clean_data,
    display_statistics, predict_winner, analyze_openings,
    cluster_games, generate_player_profile,
    analyze_opening_time_control # Nouvelle importation
)

# Fonction principale
def main():
    start_total_time = time.time()
    # Connexion à la base de données
    start_time = time.time()
    engine = create_engine("postgresql+psycopg2://Ndeye659:@s0.net.pimous.dev:31003/shallowview", connect_args={
        "sslmode": "require",
        "sslcert":"C:.crt" ,
        "sslkey": "C:.key",
        "sslrootcert":"C:.crt"
    })
    print(f"Database connection established in {time.time() - start_time:.2f} seconds.")

    # Chargement des données
    start_time = time.time()
    games = load_games(engine)
    players = load_players(engine)
    openings = load_openings(engine)
    print(f"Data loaded in {time.time() - start_time:.2f} seconds. Games: {len(games)} rows.")

    # Nettoyage des données
    start_time = time.time()
    games = clean_data(games)
    print(f"Data cleaned in {time.time() - start_time:.2f} seconds.")

    # Dictionnaire pour stocker toutes les figures Plotly et les données textuelles
    all_analysis_results = {
        "plots": {},
        "text_reports": {}
    }

    # Visualisation et analyse - Les fonctions retournent maintenant des figures Plotly
    print("\n--- Displaying Statistics ---")
    start_time = time.time()
    stats_figures = display_statistics(games)
    all_analysis_results["plots"]["statistics"] = [fig.to_json() for fig in stats_figures]
    print(f"Statistics analysis performed in {time.time() - start_time:.2f} seconds.")

    print("\n--- Predicting Winner ---")
    start_time = time.time()
    pred_figures, pred_reports = predict_winner(games)
    if pred_figures:
        all_analysis_results["plots"]["winner_prediction"] = [fig.to_json() for fig in pred_figures]
    if pred_reports:
        all_analysis_results["text_reports"]["winner_prediction"] = pred_reports
    print(f"Winner prediction performed in {time.time() - start_time:.2f} seconds.")

    print("\n--- Analyzing Openings ---")
    start_time = time.time()
    openings_figures = analyze_openings(engine)
    all_analysis_results["plots"]["opening_analysis"] = [fig.to_json() for fig in openings_figures]
    print(f"Opening analysis performed in {time.time() - start_time:.2f} seconds.")

    print("\n--- Clustering Games ---")
    start_time = time.time()
    cluster_figures = cluster_games(games)
    all_analysis_results["plots"]["clustering"] = [fig.to_json() for fig in cluster_figures]
    print(f"Game clustering performed in {time.time() - start_time:.2f} seconds.")

    # --- Nouvelle analyse : Ouverture et Contrôle du Temps ---
    print("\n--- Analyzing Opening and Time Control ---")
    start_time = time.time()
    # analyze_opening_time_control est appelée avec l'engine
    otc_figures, otc_reports = analyze_opening_time_control(engine)
    if otc_figures:
        all_analysis_results["plots"]["opening_time_control_analysis"] = [fig.to_json() for fig in otc_figures]
    if otc_reports:
        all_analysis_results["text_reports"]["opening_time_control_analysis"] = otc_reports
    print(f"Opening and Time Control analysis performed in {time.time() - start_time:.2f} seconds.")


    # Define a player name for profile generation
    player_name_to_analyze = "Hikaru Nakamura"
    print(f"\n--- Generating Player Profile for {player_name_to_analyze} ---")
    start_time = time.time()
    player_profile_figures = generate_player_profile(player_name_to_analyze, engine)
    all_analysis_results["plots"]["player_profile"] = [fig.to_json() for fig in player_profile_figures]
    print(f"Player profile generated in {time.time() - start_time:.2f} seconds.")

    # Export all analysis results to a JSON file
    output_filename = "analysis_results.json"
    with open(output_filename, 'w') as f:
        json.dump(all_analysis_results, f, indent=4)
    print(f"\nAll analysis results (plots and text) exported to '{output_filename}'")
    print(f"Total script execution time: {time.time() - start_total_time:.2f} seconds.")

if __name__ == "__main__":
    main()