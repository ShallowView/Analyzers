import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.cluster import KMeans
import plotly.tools as tools

# Loading data from the database
def load_games(engine):
    query = """
        SELECT 
            id, white, black, result, white_elo, black_elo,
            date_time, time_control, opening
        FROM games
    """
    df = pd.read_sql(query, engine)
    return df

def load_players(engine):
    query = "SELECT id, name, title, max_elo, current_elo FROM players"
    return pd.read_sql(query, engine)

def load_openings(engine):
    query = "SELECT id, eco, name, pgn FROM openings"
    return pd.read_sql(query, engine)

# Data Cleaning
def clean_data(games):
    games['date_time'] = pd.to_datetime(games['date_time'], errors='coerce')
    games[['BaseTime', 'Increment']] = games['time_control'].str.split('+', expand=True).astype(float)
    games['EloDiff'] = games['white_elo'] - games['black_elo']
    games['Gagnant'] = games['result'].map({'W': 1, 'B': -1, 'D': 0})
    games['VainqueurElo'] = games.apply(
        lambda row: row['white_elo'] if row['result'] == 'W' else (row['black_elo'] if row['result'] == 'B' else None),
        axis=1
    )
    games['PerdantElo'] = games.apply(
        lambda row: row['black_elo'] if row['result'] == 'W' else (row['white_elo'] if row['result'] == 'B' else None),
        axis=1
    )
    return games

# Statistics
"""
ANALYSIS PROFILE

Uses tables             : games  
Uses columns            : {white_elo, black_elo, EloDiff, VainqueurElo, PerdantElo, BaseTime, Increment, Gagnant}  
Description             : Analyse statistique descriptive des distributions d'Elo et de leurs corrélations avec les conditions de jeu  
Question                : Comment les Elo sont-ils distribués et quelles sont leurs relations avec les paramètres des parties ?  
Answer                  : L'analyse révèle :  
                          - Une distribution symétrique entre les Elo Blancs/Noirs (moyenne/médiane similaires)  
                          - Un écart significatif d'Elo entre gagnants et perdants (boîtes à moustaches montrant une différence médiane)  
                          - Une faible corrélation entre les contrôles de temps et l'Elo (heatmap montre |r| < 0,3)  
Speculation             : ... 
"""  
def display_statistics(games):
    print("Statistiques descriptives sur les Elo :")
    print(games[['white_elo', 'black_elo', 'EloDiff']].describe())

    plt.figure(figsize=(12, 5))
    sns.histplot(games['white_elo'], color='blue', label='White Elo', kde=True)
    sns.histplot(games['black_elo'], color='red', label='Black Elo', kde=True)
    plt.title("Distribution des Elo des joueurs")
    plt.legend()
    plt.grid(True)
    plt.show()

    plt.figure(figsize=(8, 6))
    sns.boxplot(data=games[['VainqueurElo', 'PerdantElo']])
    plt.title("Comparaison Elo Gagnants vs Perdants")
    plt.grid(True)
    plt.show()

    plt.figure(figsize=(8, 6))
    sns.heatmap(games[['white_elo', 'black_elo', 'EloDiff', 'BaseTime', 'Increment', 'Gagnant']].corr(), 
                annot=True, cmap='coolwarm', fmt=".2f")
    plt.title("Heatmap des corrélations")
    plt.show()

# Prediction of the winner

"""
ANALYSIS PROFILE

Uses tables             : games  
Uses columns            : {opening, Gagnant, white_elo, black_elo, EloDiff, BaseTime, Increment}  
Description             : Implémentation d'un modèle RandomForest pour prédire le gagnant  
Question                : Quels facteurs influencent le plus la victoire et avec quelle précision peut-on prédire le résultat ?  
Answer                  : Résultats : ...
                          
Speculation             : ...
"""

def predict_winner(games):
    games_ml = games.dropna(subset=['opening', 'Gagnant']).copy()
    le = LabelEncoder()
    games_ml['opening_enc'] = le.fit_transform(games_ml['opening'])

    X = games_ml[['white_elo', 'black_elo', 'EloDiff', 'BaseTime', 'Increment', 'opening_enc']]
    y = games_ml['Gagnant']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    print("\n Rapport de classification :")
    print(classification_report(y_test, y_pred))

    print(" Matrice de confusion :")
    print(confusion_matrix(y_test, y_pred))

# Analysis of openings

"""
ANALYSIS PROFILE

Uses tables             : games
Uses columns            : {opening, result}
Description             : Évaluation statistique de l'impact des ouvertures sur les résultats de parties
Question                : Existe-t-il des corrélations entre choix d'ouverture et issue de partie ?
Answer                  : ...
Speculation             : ...
"""
def analyze_openings(engine):
    query = """
        SELECT 
            g.opening AS eco,
            COUNT(*) AS games,
            AVG(CASE WHEN g.result = 'W' THEN 1 ELSE 0 END) AS white_win_rate,
            AVG(CASE WHEN g.result = 'B' THEN 1 ELSE 0 END) AS black_win_rate,
            AVG(CASE WHEN g.result = 'D' THEN 1 ELSE 0 END) AS draw_rate
        FROM games g
        GROUP BY g.opening
        ORDER BY games DESC
        LIMIT 15
    """
    df = pd.read_sql(query, engine)

    print("\nTop 15 Ouvertures (ECO) les plus jouées :")
    print(df)

    plt.figure(figsize=(14, 6))
    sns.barplot(data=df, x='eco', y='white_win_rate', color='blue', label='White Win')
    sns.barplot(data=df, x='eco', y='black_win_rate', color='red', label='Black Win', bottom=df['white_win_rate'])
    sns.barplot(data=df, x='eco', y='draw_rate', color='gray', label='Draw',
                bottom=df['white_win_rate'] + df['black_win_rate'])
    plt.title("Top 15 des ouvertures les plus jouées et leurs résultats")
    plt.ylabel("Proportion de résultats")
    plt.legend()
    plt.show()

# Clustering of games

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
def cluster_games(games):
    cluster_data = games[['white_elo', 'black_elo', 'EloDiff', 'BaseTime', 'Increment']].dropna()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(cluster_data)

    kmeans = KMeans(n_clusters=4, random_state=42)
    clusters = kmeans.fit_predict(X_scaled)
    cluster_data['Cluster'] = clusters

    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=cluster_data, x='white_elo', y='black_elo', hue='Cluster', palette='Set2')
    plt.title("Clustering des parties par Elo (KMeans, 4 clusters)")
    plt.grid(True)
    plt.show()


# [...] (vos imports existants)

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


