from matplotlib.axes import Axes
from matplotlib.figure import Figure
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.cluster import KMeans
import plotly.tools as tools

from ..registry import *
from ..base import * 


# Player Profile Analysis
"""
ANALYSIS PROFILE

Uses tables             : games, players
Uses columns            : games: {white, black, result, white_elo, black_elo, opening}
                         players: {id, name, title, max_elo}
Description             : Analyse complète du profil d'un joueur avec statistiques personnelles
Question                : Quelles sont les caractéristiques et performances spécifiques d'un joueur donné ?
Answer                  : Le profil révèle :
                          - Un taux de victoire de X% (Y% avec les Blancs, Z% avec les Noirs)
                          - Une préférence pour les ouvertures A, B, C
                          - Une performance supérieure avec une couleur spécifique
                          - Une évolution d'Elo montrant [pattern]
Speculation             : Les forces/faiblesses du joueur suggèrent :
                          1. Une affinité pour les positions de type [type]
                          2. Des difficultés contre [certaines stratégies]
                          3. Une adaptation aux contrôles de temps [rapide/long]
"""
def generate_player_profile(player_name, engine):
    # 1. Récupération des données du joueur
    player_query = f"""
        SELECT id, name, title, max_elo 
        FROM players 
        WHERE LOWER(name) = LOWER('{player_name}')
    """
    player_data = pd.read_sql(player_query, engine)
    
    if player_data.empty:
        print(f"Joueur {player_name} non trouvé")
        return None
    
    player_id = player_data.iloc[0]['id']
    
    # 2. Statistiques des parties
    games_query = f"""
        WITH player_games AS (
            SELECT 
                *,
                CASE WHEN white = '{player_id}' THEN 'White' ELSE 'Black' END AS player_color,
                CASE 
                    WHEN (white = '{player_id}' AND result = 'W') OR 
                         (black = '{player_id}' AND result = 'B') THEN 'Win'
                    WHEN result = 'D' THEN 'Draw'
                    ELSE 'Loss'
                END AS player_result
            FROM games
            WHERE white = '{player_id}' OR black = '{player_id}'
        )
        SELECT 
            COUNT(*) AS total_games,
            AVG(CASE WHEN player_result = 'Win' THEN 1 ELSE 0 END) AS win_rate,
            AVG(CASE WHEN player_color = 'White' THEN 1 ELSE 0 END) AS white_ratio,
            AVG(white_elo + black_elo)/2 AS avg_game_elo
        FROM player_games
    """
    stats = pd.read_sql(games_query, engine).iloc[0]
    
    # 3. Ouvertures favorites
    openings_query = f"""
        SELECT 
            opening,
            COUNT(*) AS games_count,
            AVG(CASE WHEN (white = '{player_id}' AND result = 'W') OR 
                       (black = '{player_id}' AND result = 'B') THEN 1 ELSE 0 END) AS win_rate
        FROM games
        WHERE white = '{player_id}' OR black = '{player_id}'
        GROUP BY opening
        ORDER BY games_count DESC
        LIMIT 5
    """
    
    top_openings = pd.read_sql(openings_query, engine)
    
    # 4. Construction du profil
    profile = {
        'Nom': player_name,
        'Titre': player_data.iloc[0]['title'],
        'Elo Max': int(player_data.iloc[0]['max_elo']),
        'Parties Jouées': int(stats['total_games']),
        'Taux de Victoire': f"{stats['win_rate']*100:.1f}%",
        'Préférence Couleur': 'Blancs' if stats['white_ratio'] > 0.5 else 'Noirs',
        'Ouverture Favorite': top_openings.iloc[0]['opening'],
        'Top 5 Openings': top_openings.to_dict('records')
    }
    
    # 5. Visualisation
    visualize_player_profile(profile, player_id, engine)
    
    return profile

def visualize_player_profile(profile, player_id, engine):
    # 1. Récupération des données pour les graphiques
    history_query = f"""
        SELECT 
            date_time,
            CASE WHEN white = '{player_id}' THEN white_elo ELSE black_elo END AS player_elo,
            CASE WHEN white = '{player_id}' THEN 'White' ELSE 'Black' END AS player_color,
            result
        FROM games
        WHERE white = '{player_id}' OR black = '{player_id}'
        ORDER BY date_time
    """
    history = pd.read_sql(history_query, engine)
    history['date_time'] = pd.to_datetime(history['date_time'])
    
    # 2. Configuration des graphiques
    plt.figure(figsize=(15, 10))
    
    # Graphique 1: Évolution de l'Elo
    plt.subplot(2, 2, 1)
    sns.lineplot(data=history, x='date_time', y='player_elo')
    plt.title(f"Évolution de l'Elo - {profile['Nom']}")
    plt.xlabel('Date')
    plt.ylabel('Elo')
    
    # Graphique 2: Résultats par couleur
    plt.subplot(2, 2, 2)
    result_counts = history.groupby(['player_color', 'result']).size().unstack()
    result_counts.plot(kind='bar', stacked=True, colormap='coolwarm')
    plt.title("Résultats par couleur")
    plt.ylabel("Nombre de parties")
    
    # Graphique 3: Distribution des ouvertures
    plt.subplot(2, 2, 3)
    openings = pd.DataFrame(profile['Top 5 Openings'])
    sns.barplot(data=openings, x='opening', y='games_count', hue='opening', legend=False)
    plt.title("Top 5 des ouvertures")
    plt.xticks(rotation=45)
    
    # Graphique 4: Performance par ouverture
    plt.subplot(2, 2, 4)
    sns.barplot(data=openings, x='opening', y='win_rate', hue='opening', legend=False)
    plt.title("Taux de victoire par ouverture")
    plt.xticks(rotation=45)
    plt.ylim(0, 1)
    
    plt.tight_layout()
    plt.show()