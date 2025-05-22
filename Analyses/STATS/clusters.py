import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

from ..registry import *
from ..base import * 
from .descriptions import clean_games_data, games_query

"""
ANALYSIS PROFILE

Uses tables             : games
Uses columns            : {white_elo, black_elo, EloDiff, BaseTime, Increment}
Description             : Clustering des parties d'échecs selon les caractéristiques de jeu
Question                : Peut-on identifier des groupes distincts de parties basés sur le niveau et le temps ?
Answer                  : 4 clusters émergent naturellement :
                          - Cluster 0 : Parties équilibrées (Elo proches, temps standard)
                          - Cluster 1 : Parties déséquilibrées (grand écart d'Elo)
                          - Cluster 2 : Parties rapides (temps court malgré Elo moyen)
                          - Cluster 3 : Parties longues (temps élevé, joueurs expérimentés)
Speculation             : ...
"""

@register_analysis('STATS_analysis_clusters')
def STATS_analysis_clusters(plot_list : list[str]):
    games_data = fetch_data_from_sql(games_query)
    cleaned_data = clean_games_data(games_data)
    if (plot_list.__contains__('clusters')):
        plot_data = process_data(cleaned_data)
        plot_stats_clusters(plot_data)


@assign_plot_to_analysis('STATS_analysis_clusters', 'clusters')
def plot_stats_clusters(cluster_data):
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=cluster_data, x='white_elo', y='black_elo', hue='Cluster', palette='Set2')
    plt.title("Clustering des parties par Elo (KMeans, 4 clusters)")
    plt.grid(True)
    
    
def process_data(games : pd.DataFrame) -> pd.DataFrame :
    cluster_data = games[['white_elo', 'black_elo', 'EloDiff', 'BaseTime', 'Increment']].dropna()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(cluster_data)
    kmeans = KMeans(n_clusters=4, random_state=42)
    clusters = kmeans.fit_predict(X_scaled)
    cluster_data['Cluster'] = clusters
    return cluster_data
    
