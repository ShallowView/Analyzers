import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.cluster import KMeans

# Chargement des données depuis la base de données
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

# Nettoyage des données
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

# Statistiques
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

# Prédiction du gagnant
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

# Analyse des ouvertures
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

# Clustering des jeux
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
