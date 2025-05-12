# code1.py

from sqlalchemy import create_engine
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

import logging

# Activer le mode debug pour SQLAlchemy
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Fonction pour créer l'engine (connexion à la base de données)




from sqlalchemy import create_engine

def get_engine():
    return create_engine(
        "postgresql+psycopg2://Ndeye659:Ibou@s0.net.pimous.dev:31003/shallowview",
        connect_args={
            "sslmode": "require",
            "sslcert": r"C:\Users\ASUS\Documents\Projet\dataAnalyste\Ndeye659.crt",
            "sslkey": r"C:\Users\ASUS\Documents\Projet\dataAnalyste\Ndeye659.key",
            "sslrootcert": r"C:\Users\ASUS\Documents\Projet\dataAnalyste\pimousdev-db.chain.crt"
        }
    )

    






def load_data(engine):
    games = pd.read_sql("SELECT id, date, white_elo, black_elo, time_control, result, eco FROM games", engine)
    players = pd.read_sql("SELECT * FROM players", engine)
    openings = pd.read_sql("SELECT * FROM openings", engine)
    return games, players, openings


def clean_data(games):
    games['date'] = pd.to_datetime(games['date'], errors='coerce')
    games[['base_time', 'increment']] = games['time_control'].str.split('+', expand=True).astype(float)
    games['elo_diff'] = games['white_elo'] - games['black_elo']
    games['gagnant'] = games['result'].map({'W': 1, 'B': -1, 'D': 0})
    return games.dropna(subset=['white_elo', 'black_elo', 'base_time', 'increment', 'gagnant'])


def display_statistics(games):
    print("\n--- Statistiques descriptives ---")
    print(games.describe())


def predict_winner(games):
    features = ['white_elo', 'black_elo', 'base_time', 'increment', 'elo_diff']
    X = games[features]
    y = games['gagnant']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    print("\n--- Rapport de classification ---")
    print(classification_report(y_test, y_pred))
    print("\n--- Matrice de confusion ---")
    print(confusion_matrix(y_test, y_pred))


def analyze_openings(engine):
    query = """
        SELECT eco, COUNT(*) as count
        FROM games
        GROUP BY eco
        ORDER BY count DESC
        LIMIT 10
    """
    df_openings = pd.read_sql(query, engine)

    sns.barplot(data=df_openings, x='eco', y='count')
    plt.title('Top 10 des ouvertures les plus jouées')
    plt.xlabel('Code ECO')
    plt.ylabel('Nombre de parties')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def cluster_games(games):
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(games[['white_elo', 'black_elo', 'base_time', 'increment']])

    kmeans = KMeans(n_clusters=3, random_state=42)
    games['cluster'] = kmeans.fit_predict(X_scaled)

    sns.scatterplot(data=games, x='white_elo', y='black_elo', hue='cluster', palette='Set2')
    plt.title('Clustering des parties selon les Elos')
    plt.xlabel('White Elo')
    plt.ylabel('Black Elo')
    plt.tight_layout()
    plt.show()
