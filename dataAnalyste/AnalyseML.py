import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.cluster import KMeans
import lightgbm as lgb
import plotly.express as px
import plotly.graph_objects as go
import plotly.tools as tls
import matplotlib.pyplot as plt
import seaborn as sns
import json

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

# Data Cleaning - Optimized string operations and vectorized assignments
def clean_data(games):
    games['date_time'] = pd.to_datetime(games['date_time'], errors='coerce')

    time_control_parts = games['time_control'].str.split('+', expand=True)
    games['BaseTime'] = pd.to_numeric(time_control_parts[0], errors='coerce')
    games['Increment'] = pd.to_numeric(time_control_parts[1], errors='coerce')

    games['EloDiff'] = games['white_elo'] - games['black_elo']
    games['Gagnant'] = games['result'].map({'W': 1, 'B': -1, 'D': 0})

    games['VainqueurElo'] = np.where(games['result'] == 'W', games['white_elo'],
                                     np.where(games['result'] == 'B', games['black_elo'], np.nan))
    games['PerdantElo'] = np.where(games['result'] == 'W', games['black_elo'],
                                   np.where(games['result'] == 'B', games['white_elo'], np.nan))
    return games

# Statistics - Now returns Plotly figures
def display_statistics(games):
    figures = []
    print("Statistiques descriptives sur les Elo :")
    print(games[['white_elo', 'black_elo', 'EloDiff']].describe())

    plotting_sample_size = 500000
    sampled_games = games.sample(n=min(len(games), plotting_sample_size), random_state=42)
    if len(games) > plotting_sample_size:
        print(f"Subsampling {len(sampled_games)} rows for faster plotting in display_statistics.")

    fig1 = go.Figure()
    fig1.add_trace(go.Histogram(x=sampled_games['white_elo'], name='White Elo', marker_color='blue', opacity=0.7, xbins=dict(size=50)))
    fig1.add_trace(go.Histogram(x=sampled_games['black_elo'], name='Black Elo', marker_color='red', opacity=0.7, xbins=dict(size=50)))
    fig1.update_layout(
        barmode='overlay',
        title_text='Distribution des Elo des joueurs',
        xaxis_title_text='Elo',
        yaxis_title_text='Fréquence',
        legend_title_text='Joueur'
    )
    figures.append(fig1)

    df_melted_elo = sampled_games[['VainqueurElo', 'PerdantElo']].melt(var_name='Type Elo', value_name='Elo').dropna(subset=['Elo'])

    # Ajout d'une vérification pour le graphique en boîte
    # S'assurer qu'il y a au moins 2 points par catégorie pour un boxplot significatif
    if not df_melted_elo.empty and df_melted_elo.groupby('Type Elo')['Elo'].count().min() > 1:
        fig2 = px.box(df_melted_elo, x='Type Elo', y='Elo',
                      title="Comparaison Elo Gagnants vs Perdants",
                      color='Type Elo',
                      color_discrete_map={'VainqueurElo': 'green', 'PerdantElo': 'orange'})
        figures.append(fig2)
    else:
        print("Avertissement: Données insuffisantes pour le graphique en boîte de la comparaison des Elo. (Moins de 2 points par catégorie ou données vides)")


    corr_matrix = sampled_games[['white_elo', 'black_elo', 'EloDiff', 'BaseTime', 'Increment', 'Gagnant']].corr()
    fig3 = px.imshow(corr_matrix, text_auto=True, aspect="auto",
                     color_continuous_scale='RdBu_r',
                     title="Heatmap des corrélations")
    figures.append(fig3)

    return figures

# Prediction of the winner - No plotting changes here, only model
def predict_winner(games):
    games_ml = games.dropna(subset=['opening', 'Gagnant']).copy()

    if games_ml.empty:
        print("Not enough data to predict winner after dropping NaNs.")
        return None, None

    le = LabelEncoder()
    if 'opening' in games_ml.columns and not games_ml['opening'].isnull().all():
        games_ml['opening_enc'] = le.fit_transform(games_ml['opening'])
    else:
        print("Warning: 'opening' column is missing or all NaN, skipping encoding.")
        games_ml['opening_enc'] = 0

    features = ['white_elo', 'black_elo', 'EloDiff', 'BaseTime', 'Increment']
    if 'opening_enc' in games_ml.columns:
        features.append('opening_enc')

    X = games_ml[features]
    y = games_ml['Gagnant']

    y_mapped = y.map({-1: 0, 0: 1, 1: 2})
    X, y_mapped = X.loc[y_mapped.notna()], y_mapped.loc[y_mapped.notna()]
    y_mapped = y_mapped.astype(int)

    if len(X) == 0 or len(y_mapped) == 0:
        print("Not enough data after feature selection or target mapping to perform train/test split.")
        return [], {} # Return empty lists for figures and reports

    if y_mapped.nunique() < 2:
        print(f"Only {y_mapped.nunique()} unique classes in target 'Gagnant' after mapping, cannot perform classification.")
        return [], {} # Return empty lists for figures and reports

    test_size_val = 0.2
    if len(X) * test_size_val < 1 and len(X) >=1:
        test_size_val = 1/len(X)
        print(f"Adjusting test_size to {test_size_val:.2f} due to small dataset size.")
    elif len(X) * test_size_val < 1:
        print("Not enough data to create a test set for prediction.")
        return [], {} # Return empty lists for figures and reports

    X_train, X_test, y_train, y_test = train_test_split(X, y_mapped, test_size=test_size_val, random_state=42, stratify=y_mapped)

    model = lgb.LGBMClassifier(objective='multiclass',
                                num_class=y_mapped.nunique(),
                                n_estimators=100,
                                num_leaves=31,
                                learning_rate=0.05,
                                random_state=42,
                                n_jobs=-1)
    print(f"Training LGBMClassifier with n_estimators={model.n_estimators} and n_jobs={model.n_jobs}...")

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    print("\n Rapport de classification (labels mappés -1->0, 0->1, 1->2) :")
    print(classification_report(y_test, y_pred))

    print(" Matrice de confusion (labels mappés -1->0, 0->1, 1->2) :")
    print(confusion_matrix(y_test, y_pred))

    return [], {"classification_report": classification_report(y_test, y_pred, output_dict=True),
                "confusion_matrix": confusion_matrix(y_test, y_pred).tolist()}


# Analysis of openings - Now returns Plotly figure, handles UUID
def analyze_openings(engine):
    figures = []
    query = """
        SELECT
            g.opening AS eco,
            COUNT(*) AS games,
            AVG(CASE WHEN g.result = 'W' THEN 1.0 ELSE 0.0 END) AS white_win_rate,
            AVG(CASE WHEN g.result = 'B' THEN 1.0 ELSE 0.0 END) AS black_win_rate,
            AVG(CASE WHEN g.result = 'D' THEN 1.0 ELSE 0.0 END) AS draw_rate
        FROM games g
        GROUP BY g.opening
        ORDER BY games DESC
        LIMIT 15
    """
    df = pd.read_sql(query, engine)

    df['eco'] = df['eco'].astype(str)

    print("\nTop 15 Ouvertures (ECO) les plus jouées :")
    print(df)

    df_melted = df.melt(id_vars=['eco', 'games'], value_vars=['white_win_rate', 'black_win_rate', 'draw_rate'],
                        var_name='result_type', value_name='proportion')

    result_map = {'white_win_rate': 'Victoire Blanc', 'black_win_rate': 'Victoire Noir', 'draw_rate': 'Nul'}
    df_melted['result_label'] = df_melted['result_type'].map(result_map)

    fig = px.bar(df_melted, x='eco', y='proportion', color='result_label',
                 title="Top 15 des ouvertures les plus jouées et leurs résultats",
                 labels={'proportion': 'Proportion de résultats', 'eco': 'Ouverture (ECO)'},
                 category_orders={"result_label": ["Victoire Blanc", "Victoire Noir", "Nul"]},
                 color_discrete_map={'Victoire Blanc': 'blue', 'Victoire Noir': 'red', 'Nul': 'gray'})

    fig.update_layout(xaxis_tickangle=-45)
    figures.append(fig)

    return figures

# Clustering of games - Now returns Plotly figure
def cluster_games(games):
    figures = []
    features_for_clustering = ['white_elo', 'black_elo', 'EloDiff', 'BaseTime', 'Increment']
    cluster_data = games[features_for_clustering].dropna()

    print(f"\n--- Diagnostic pour cluster_games ---")
    print(f"Taille originale du DataFrame 'games': {len(games)} lignes")
    print(f"Colonnes utilisées pour le clustering: {features_for_clustering}")
    print(f"Nombre de lignes après dropna() pour le clustering: {len(cluster_data)}")
    if cluster_data.empty:
        print("ATTENTION : cluster_data est vide après avoir supprimé les valeurs manquantes.")
        print("Vérifiez les données brutes dans les colonnes suivantes pour les NaN :")
        for col in features_for_clustering:
            nan_count = games[col].isnull().sum()
            if nan_count > 0:
                print(f"  - Colonne '{col}' a {nan_count} NaN(s).")
        print("Le clustering ne peut pas être effectué car il n'y a pas de données valides.")
        return []

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(cluster_data)

    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)
    cluster_data['Cluster'] = clusters

    plotting_sample_size = 500000
    sampled_cluster_data = cluster_data.sample(n=min(len(cluster_data), plotting_sample_size), random_state=42)
    if len(cluster_data) > plotting_sample_size:
        print(f"Subsampling {len(sampled_cluster_data)} rows for faster plotting in cluster_games.")

    fig = px.scatter(sampled_cluster_data, x='white_elo', y='black_elo', color='Cluster',
                     title="Clustering des parties par Elo (KMeans, 4 clusters)",
                     labels={'white_elo': 'Elo du joueur blanc', 'black_elo': 'Elo du joueur noir'},
                     color_discrete_sequence=px.colors.qualitative.Set2,
                     opacity=0.6)
    figures.append(fig)

    print("\nDistribution des points par cluster (sur toutes les données valides):")
    print(cluster_data['Cluster'].value_counts())
    print("\nCentres des clusters (échelles standardisées):")
    print(kmeans.cluster_centers_)

    return figures

# Player Profile Analysis - Now returns Plotly figures, handles UUID
def generate_player_profile(player_name, engine):
    figures = []
    player_query = f"""
        SELECT id, name, title, max_elo
        FROM players
        WHERE LOWER(name) = LOWER('{player_name}')
    """
    player_data = pd.read_sql(player_query, engine)

    if player_data.empty:
        print(f"Joueur {player_name} non trouvé")
        return []

    player_id = player_data.iloc[0]['id']

    games_query = f"""
        WITH player_games AS (
            SELECT
                date_time,
                opening,
                CASE
                    WHEN white = '{player_id}' THEN white_elo
                    ELSE black_elo
                END AS player_elo,
                CASE
                    WHEN white = '{player_id}' THEN 'White'
                    ELSE 'Black'
                END AS player_color,
                result,
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
            (SELECT COUNT(*) FROM player_games) AS total_games,
            (SELECT AVG(CASE WHEN player_result = 'Win' THEN 1.0 ELSE 0.0 END) FROM player_games) AS win_rate,
            (SELECT AVG(CASE WHEN player_color = 'White' THEN 1.0 ELSE 0.0 END) FROM player_games) AS white_ratio
        FROM player_games
        LIMIT 1;
    """
    stats = pd.read_sql(games_query, engine).iloc[0]

    openings_query = f"""
        SELECT
            opening,
            COUNT(*) AS games_count,
            AVG(CASE WHEN (white = '{player_id}' AND result = 'W') OR
                       (black = '{player_id}' AND result = 'B') THEN 1.0 ELSE 0.0 END) AS win_rate
        FROM games
        WHERE white = '{player_id}' OR black = '{player_id}'
        GROUP BY opening
        ORDER BY games_count DESC
        LIMIT 5
    """
    top_openings = pd.read_sql(openings_query, engine)

    if not top_openings.empty:
        top_openings['opening'] = top_openings['opening'].astype(str)

    profile = {
        'Nom': player_name,
        'Titre': player_data.iloc[0]['title'],
        'Elo Max': int(player_data.iloc[0]['max_elo']),
        'Parties Jouées': int(stats['total_games']),
        'Taux de Victoire': f"{stats['win_rate']*100:.1f}%",
        'Préférence Couleur': 'Blancs' if stats['white_ratio'] > 0.5 else 'Noirs',
        'Ouverture Favorite': top_openings.iloc[0]['opening'] if not top_openings.empty else 'N/A',
        'Top 5 Openings': top_openings.to_dict('records')
    }
    print(f"\n--- Profil du joueur {profile['Nom']} ---")
    for key, value in profile.items():
        if key != 'Top 5 Openings':
            print(f"{key}: {value}")
    print("Top 5 Openings (Détails):")
    print(pd.DataFrame(profile['Top 5 Openings']))


    # 1. Évolution de l'Elo
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

    if not history.empty and history['player_elo'].notna().any(): # Check if there's actual data for the line plot
        fig_elo_evol = px.line(history, x='date_time', y='player_elo',
                               title=f"Évolution de l'Elo - {profile['Nom']}",
                               labels={'date_time': 'Date', 'player_elo': 'Elo'},
                               line_shape='linear')
        figures.append(fig_elo_evol)
    else:
        print("Avertissement: Pas de données d'historique d'Elo disponibles pour le joueur.")


    # 2. Résultats par couleur
    result_counts = history.groupby(['player_color', 'result']).size().unstack(fill_value=0)
    result_counts = result_counts.reindex(columns=['W', 'D', 'B'], fill_value=0)
    result_counts.rename(columns={'W': 'Win', 'D': 'Draw', 'B': 'Loss'}, inplace=True)
    
    if not result_counts.empty and result_counts.sum().sum() > 0: # Check if there are any results
        result_counts_percent = result_counts.apply(lambda x: x / x.sum(), axis=1) * 100

        fig_results_color = px.bar(result_counts_percent,
                                   x=result_counts_percent.index,
                                   y=['Win', 'Draw', 'Loss'],
                                   title="Résultats par couleur (%)",
                                   labels={'x': 'Couleur jouée', 'value': 'Proportion (%)'},
                                   color_discrete_map={'Win': 'blue', 'Draw': 'gray', 'Loss': 'red'},
                                   text_auto=True)
        fig_results_color.update_layout(barmode='stack')
        figures.append(fig_results_color)
    else:
        print("Avertissement: Pas de données de résultats par couleur disponibles pour le joueur.")


    # 3. Distribution des ouvertures (Top 5)
    openings_df = pd.DataFrame(profile['Top 5 Openings'])
    if not openings_df.empty:
        fig_top_openings = px.bar(openings_df, x='opening', y='games_count',
                                  title="Top 5 des ouvertures les plus jouées",
                                  labels={'opening': 'Ouverture', 'games_count': 'Nombre de parties'},
                                  color_discrete_sequence=px.colors.viridis)
        fig_top_openings.update_layout(xaxis_tickangle=-45)
        figures.append(fig_top_openings)
    else:
        print("Pas de données d'ouverture disponibles pour le joueur.")

    # 4. Taux de victoire par ouverture
    if not openings_df.empty:
        fig_win_rate_openings = px.bar(openings_df, x='opening', y='win_rate',
                                       title="Taux de victoire par ouverture",
                                       labels={'opening': 'Ouverture', 'win_rate': 'Taux de victoire'},
                                       range_y=[0, 1],
                                       color_discrete_sequence=px.colors.viridis)
        fig_win_rate_openings.update_layout(xaxis_tickangle=-45)
        figures.append(fig_win_rate_openings)
    else:
        print("Pas de données de performance d'ouverture disponibles pour le joueur.")

    return figures

# --- Fonctions utilitaires basées sur l'exemple de votre camarade ---

def calculate_value_distribution(df: pd.DataFrame, group_column: str, value_column: str) -> pd.DataFrame:
    """
    Calcule la distribution des valeurs (counts) de `value_column` par `group_column`.
    Simule une table croisée.
    """
    # Utilise pd.crosstab pour obtenir une table de fréquences
    cross_tab = pd.crosstab(df[group_column], df[value_column])
    return cross_tab

def filter_data_by_threshold(df: pd.DataFrame, row_threshold: float = 0.0001, col_threshold: float = 0.0001) -> pd.DataFrame:
    """
    Filtre les lignes et les colonnes d'un DataFrame en fonction d'un seuil de proportion.
    Retire les lignes/colonnes dont la somme est inférieure au seuil (par rapport à la somme totale).
    """
    # Filtrer les lignes (group_column)
    row_sums = df.sum(axis=1)
    total_sum_rows = row_sums.sum()
    # Éviter la division par zéro si total_sum_rows est 0
    if total_sum_rows == 0:
        return pd.DataFrame(columns=df.columns) # Retourne un DataFrame vide avec les mêmes colonnes
    rows_to_keep = row_sums[row_sums / total_sum_rows >= row_threshold].index
    filtered_df = df.loc[rows_to_keep]

    # Filtrer les colonnes (value_column)
    col_sums = filtered_df.sum(axis=0)
    total_sum_cols = col_sums.sum()
    # Éviter la division par zéro si total_sum_cols est 0
    if total_sum_cols == 0:
        return pd.DataFrame(columns=filtered_df.columns) # Retourne un DataFrame vide
    cols_to_keep = col_sums[col_sums / total_sum_cols >= col_threshold].index
    filtered_df = filtered_df[cols_to_keep]

    return filtered_df

def calculate_proportions_from_total(games_and_openings : pd.DataFrame) -> pd.Series:
    time_control_counts = games_and_openings.sum(axis=0)
    total_games = time_control_counts.sum()
    if total_games == 0:
        return pd.Series(dtype='float64') # Retourne une série vide si pas de jeux
    time_control_proportions = time_control_counts / total_games
    time_control_percentages = time_control_proportions * 100
    return time_control_percentages

def series_to_dataframe(series : pd.Series, labels_list : str, values_list : str) -> pd.DataFrame:
    df = pd.DataFrame(series)
    df.reset_index(inplace=True)
    df.columns = [labels_list, values_list]
    return df

# --- Fonctions de Plotting (Matplotlib, puis converties en Plotly) ---

def plot_heatmap(data: pd.DataFrame, title: str, xlabel: str, ylabel: str):
    """Crée une heatmap Matplotlib."""
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(data, annot=True, fmt=".0f", cmap="viridis", linewidths=.5, ax=ax)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    return fig

def plot_barplot(data: pd.DataFrame, lables_list: str, values_list: str, title: str, xlabel: str, ylabel: str):
    """Crée un barplot Matplotlib."""
    fig, ax = plt.subplots(figsize=(10, 6))
    # Correction pour FutureWarning de Seaborn
    sns.barplot(x=lables_list, y=values_list, data=data, palette="coolwarm", ax=ax, hue=lables_list, legend=False)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return fig

# --- Nouvelle fonction d'analyse O_TC_analysis ---
def analyze_opening_time_control(engine):
    figures = []
    text_reports = {}

    opening_and_time_control_query = f"""SELECT
        g.time_control,
        o.name AS opening
    FROM
        games g
    JOIN
        openings o ON g.opening = o.id
    WHERE
        g.time_control IS NOT NULL AND o.name IS NOT NULL
    LIMIT 100000;
    """
    
    original_data = pd.read_sql(opening_and_time_control_query, engine)
    
    original_data['opening'] = original_data['opening'].astype(str)

    if original_data.empty:
        print("Aucune donnée disponible pour l'analyse des ouvertures et contrôles du temps.")
        return [], {}

    formatted_games_openings_and_time_controls = calculate_value_distribution(
        original_data,
        group_column='opening',
        value_column='time_control'
    )
    
    # Correction: Assurer que les seuils sont raisonnables, et vérifier le résultat
    filtered_data = filter_data_by_threshold(formatted_games_openings_and_time_controls,
                                             row_threshold=0.0001, col_threshold=0.0001)

    if filtered_data.empty:
        print("Avertissement: Les données filtrées pour l'analyse Ouverture vs Contrôle du Temps sont vides. Pas de plots générés.")
        return [], {}


    print("\n--- Analyse : Ouvertures et Contrôle du Temps ---")
    print(f"Données après filtrage pour l'analyse O_TC:\n{filtered_data.head()}")
    
    # Barplot des pourcentages de contrôle de temps
    barplot_data = calculate_proportions_from_total(filtered_data)
    time_control_percentages_df = series_to_dataframe(barplot_data, 'Time Control', 'Percentage')
    time_control_percentages_nicer_format = time_control_percentages_df.sort_values(by='Percentage', ascending=False).head(10)

    if not time_control_percentages_nicer_format.empty:
        mpl_fig_barplot = plot_barplot(
            time_control_percentages_nicer_format,
            lables_list='Time Control',
            values_list='Percentage',
            title='Pourcentages de Contrôle du Temps (Top 10)',
            xlabel='Contrôle du Temps',
            ylabel='Pourcentage (%)'
        )
        plt.close(mpl_fig_barplot) # Fermer la figure Matplotlib
        plotly_fig_barplot = tls.mpl_to_plotly(mpl_fig_barplot)
        plotly_fig_barplot.update_layout(title_text='Pourcentages de Contrôle du Temps (Top 10)')
        figures.append(plotly_fig_barplot)
    else:
        print("Avertissement: Pas de données pour le barplot des contrôles du temps après filtrage.")


    # Heatmap des ouvertures et contrôles du temps
    heatmap_data = filtered_data.copy()
    
    if not heatmap_data.empty:
        mpl_fig_heatmap = plot_heatmap(
            heatmap_data,
            title='Heatmap: Fréquence des Ouvertures par Contrôle du Temps',
            xlabel='Contrôle du Temps',
            ylabel='Ouverture'
        )
        plt.close(mpl_fig_heatmap) # Fermer la figure Matplotlib
        plotly_fig_heatmap = tls.mpl_to_plotly(mpl_fig_heatmap)
        plotly_fig_heatmap.update_layout(title_text='Heatmap: Fréquence des Ouvertures par Contrôle du Temps')
        figures.append(plotly_fig_heatmap)
    else:
        print("Avertissement: Pas de données pour la heatmap des ouvertures et contrôles du temps après filtrage.")

    return figures, text_reports