#!/usr/bin/env python
# coding: utf-8


# Analyse de Performance des Joueurs d'Échecs (Lichess Elite 2020)
# Auteur : Mame Faty SECK
# Dataset : Lichess Elite - Juin 2020

import pandas as pd
import matplotlib.pyplot as plt

# 1. Chargement des fichiers
print("Chargement des données...")
games = pd.read_csv('lichess_elite_2020-06_games.csv')
players = pd.read_csv('lichess_elite_2020-06_players.csv')

# 2. Prétraitement et enrichissement
print("Préparation des données...")

# Associer les UUID à leur nom
id_to_name = dict(zip(players['id'], players['PlayerName']))
games['WhitePlayer'] = games['White'].map(id_to_name)
games['BlackPlayer'] = games['Black'].map(id_to_name)

# Calcul de l'écart de Elo
games['RatingDiff'] = games['WhiteElo'] - games['BlackElo']

# Conversion des dates
games['Date'] = pd.to_datetime(games['Date'])

# 3. Évolution de l'Elo moyen par jour
print("Calcul de l'évolution du Elo moyen par jour...")

daily_elos = games.groupby(games['Date'].dt.date)[['WhiteElo', 'BlackElo']].mean()
daily_elos['AverageElo'] = daily_elos.mean(axis=1)


# 4. Comparaison MaxElo (carrière) vs Elo actuel (tournoi)
print("Comparaison MaxElo vs Elo actuel...")

# Calcul de l'Elo moyen actuel pour chaque joueur
white_avg = games.groupby('WhitePlayer')['WhiteElo'].mean()
black_avg = games.groupby('BlackPlayer')['BlackElo'].mean()
average_elo = (white_avg.add(black_avg, fill_value=0)) / 2

# Ajout au tableau des joueurs
players['CurrentElo'] = players['PlayerName'].map(average_elo)
players['EloGap'] = players['MaxElo'] - players['CurrentElo']
players_with_data = players.dropna(subset=['CurrentElo'])

# 5. Statistiques descriptives
print("\nStatistiques : MaxElo vs Elo actuel")
print(players_with_data[['MaxElo', 'CurrentElo', 'EloGap']].describe().round(2))

# 6. Écart de Elo moyen entre gagnant et perdant
print("\nAnalyse de l'écart Elo moyen gagnant vs perdant...")

# Filtrer les parties décisives (sans nuls)
decisive_games = games[games['Result'] != 'D']
elo_gap_avg = decisive_games['RatingDiff'].abs().mean()

print(f"Moyenne d'écart Elo entre gagnant et perdant : {elo_gap_avg:.2f}")





# 2. Nettoyage et enrichissement
id_to_name = dict(zip(players['id'], players['PlayerName']))
games['WhitePlayer'] = games['White'].map(id_to_name)
games['BlackPlayer'] = games['Black'].map(id_to_name)
games['RatingDiff'] = games['WhiteElo'] - games['BlackElo']
games['Date'] = pd.to_datetime(games['Date'])

# 3. Evolution du Elo moyen par jour
elo_by_date = games.groupby(games['Date'].dt.date)[['WhiteElo', 'BlackElo']].mean()
elo_by_date['AverageElo'] = elo_by_date.mean(axis=1)

# 4. Comparaison MaxElo vs Elo actuel
white_avg = games.groupby('WhitePlayer')['WhiteElo'].mean()
black_avg = games.groupby('BlackPlayer')['BlackElo'].mean()
current_elo = (white_avg.add(black_avg, fill_value=0)) / 2

players['CurrentElo'] = players['PlayerName'].map(current_elo)
players['EloGap'] = players['MaxElo'] - players['CurrentElo']
players_with_elo = players.dropna(subset=['CurrentElo'])

# 5. Statistiques MaxElo vs CurrentElo
print(players_with_elo[['MaxElo', 'CurrentElo', 'EloGap']].describe())

# 6. Moyenne d'écart Elo entre gagnant et perdant
victory_games = games[games['Result'] != 'D']
elo_diff_mean = victory_games['RatingDiff'].abs().mean()
print(f"Moyenne d'écart Elo entre gagnant et perdant : {elo_diff_mean:.2f}")

# Vérification du format "W", "B", "D"
if "Result" not in games.columns:
    raise ValueError("La colonne 'Result' est absente du fichier.")

# Compter les occurrences
total_games = len(games)
white_wins = (games['Result'] == 'W').sum()
black_wins = (games['Result'] == 'B').sum()
draws = (games['Result'] == 'D').sum()

# Calcul du taux
white_win_rate = white_wins / total_games * 100
black_win_rate = black_wins / total_games * 100
draw_rate = draws / total_games * 100

# Préparer les données pour le graphe
labels = ['Blancs', 'Noirs', 'Nuls']
values = [white_win_rate, black_win_rate, draw_rate]

# Tracer le graphe
plt.figure(figsize=(8, 6))
bars = plt.bar(labels, values, color=['#dcdcdc', '#333333', '#888888'])

# Ajouter les valeurs sur les barres
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, height, f'{height:.1f}%', ha='center', va='bottom')

plt.title("Taux de victoire par couleur (jeux élite)")
plt.ylabel("Pourcentage de parties")
plt.ylim(0, 100)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()


# Vérifier présence des colonnes
if 'ECO' not in games.columns or 'Result' not in games.columns:
    raise ValueError("Les colonnes 'ECO' ou 'Result' sont manquantes dans le fichier.")

# S'assurer que les noms d'ouverture existent (ou les créer)
if 'opening_name' not in games.columns:
    # S'il existe une correspondance ECO → nom, tu peux la charger ici avec tableau.csv si souhaité
    games['opening_name'] = games['ECO']  # fallback au code ECO sinon

# Calcul des stats par ouverture
grouped = games.groupby('opening_name')['Result'].value_counts(normalize=True).unstack().fillna(0)

# On garde les ouvertures les plus jouées (top 10 par exemple)
top_openings = games['opening_name'].value_counts().head(10).index
grouped_top = grouped.loc[top_openings]

# Renommer les colonnes
grouped_top = grouped_top.rename(columns={
    'W': 'Victoires Blancs',
    'B': 'Victoires Noirs',
    'D': 'Nuls'
})

# Graphique empilé
grouped_top[['Victoires Blancs', 'Victoires Noirs', 'Nuls']].plot(kind='barh', stacked=True, figsize=(10, 7), colormap="Pastel1")

plt.title("Résultats par couleur pour les 10 ouvertures les plus jouées")
plt.xlabel("Proportion des parties")
plt.ylabel("Ouverture")
plt.legend(loc='lower right')
plt.grid(axis='x', linestyle='--', alpha=0.6)
plt.tight_layout()


# 11. Analyse complémentaire : Temps de partie ou Elo moyen par ouverture
games['avg_elo'] = (games['WhiteElo'] + games['BlackElo']) / 2

elo_by_opening = games.groupby('opening_name')['avg_elo'].mean().sort_values(ascending=False)

plt.figure(figsize=(10, 8))
elo_by_opening.plot(kind="barh")
plt.title("Elo moyen par ouverture")
plt.xlabel("Elo moyen")
plt.ylabel("Ouverture")
plt.tight_layout()

games['Date'] = pd.to_datetime(games['Date'])

# Exemple : sélection d’un joueur spécifique
joueur = "Magnus Carlsen"
id_to_name = dict(zip(players['id'], players['PlayerName']))
games['WhitePlayer'] = games['White'].map(id_to_name)
games['BlackPlayer'] = games['Black'].map(id_to_name)

# Elo du joueur selon qu’il joue avec les Blancs ou les Noirs
elo_white = games[games['WhitePlayer'] == joueur][['Date', 'WhiteElo']].rename(columns={'WhiteElo': 'Elo'})
elo_black = games[games['BlackPlayer'] == joueur][['Date', 'BlackElo']].rename(columns={'BlackElo': 'Elo'})

# Fusion
elo_all = pd.concat([elo_white, elo_black]).sort_values('Date')

# Tracé
plt.figure(figsize=(10, 5))
plt.plot(elo_all['Date'], elo_all['Elo'], marker='o', linestyle='-', color='blue')
plt.title(f"Évolution du Elo de {joueur} en juin 2020")
plt.xlabel("Date")
plt.ylabel("Elo")
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()


id_to_title = dict(zip(players['id'], players['Title']))

# Ajouter les titres
games['WhiteTitle'] = games['White'].map(id_to_title)
games['BlackTitle'] = games['Black'].map(id_to_title)

# Exclure les parties nulles
games_decisive = games[games['Result'] != 'D']

# Comptage des victoires par titre
white_wins = games_decisive[games_decisive['Result'] == 'W']['WhiteTitle'].value_counts()
black_wins = games_decisive[games_decisive['Result'] == 'B']['BlackTitle'].value_counts()
total_played = pd.concat([games['WhiteTitle'], games['BlackTitle']]).value_counts()

# Total des victoires
total_wins = white_wins.add(black_wins, fill_value=0)
win_rate_by_title = (total_wins / total_played) * 100

# Tracé
win_rate_by_title = win_rate_by_title.dropna().sort_values(ascending=False)

plt.figure(figsize=(8, 6))
win_rate_by_title.plot(kind='bar', color='skyblue')
plt.title("Taux de victoire par titre")
plt.ylabel("Taux de victoire (%)")
plt.xlabel("Titre")
plt.ylim(0, 100)
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()


# Détection du type de cadence selon le format lichess (ex: '300+5' → Blitz)
def detect_cadence(tc_str):
    base = int(tc_str.split('+')[0])
    if base < 180:
        return "Bullet"
    elif base < 600:
        return "Blitz"
    elif base < 1800:
        return "Rapid"
    else:
        return "Classical"

games['Cadence'] = games['TimeControl'].map(detect_cadence)

# Compter les résultats par cadence
result_by_cadence = games.groupby('Cadence')['Result'].value_counts(normalize=True).unstack().fillna(0)

# Tracé en barres empilées
result_by_cadence = result_by_cadence.rename(columns={'W': 'Blancs', 'B': 'Noirs', 'D': 'Nuls'})

result_by_cadence[['Blancs', 'Noirs', 'Nuls']].plot(kind='bar', stacked=True, colormap="Set3", figsize=(9,6))
plt.title("Résultats par cadence")
plt.ylabel("Proportion des résultats")
plt.xlabel("Cadence")
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.tight_layout()


