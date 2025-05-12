"""!/usr/bin/env python
 coding: utf-8
"""

# In[ ]:


import pandas as pd
import matplotlib.pyplot as plt


""" loading data"""

df_games = pd.read_csv("lichess_elite_2020-06_games.csv")
df_players = pd.read_csv("lichess_elite_2020-06_players.csv")


"""Clean up column names to avoid spaces"""
df_players.columns = df_players.columns.str.strip()

# SELECTION DU JOUEUR (à personnaliser ici) 
player_name = "Cor64"  # <-- Change juste ce nom ici pour n'importe quel joueur

# Vérifier les colonnes disponibles
print(df_players.columns)  # Affiche les colonnes disponibles

# Récupérer l'ID du joueur
player_row = df_players[df_players["PlayerName"] == player_name] # Vérifie que 'username' est correct
if player_row.empty:
    print(f"Le joueur '{player_name}' n'a pas été trouvé.")
    print("Liste des joueurs disponibles:")
    print(df_players.head())  # Affiche les premières lignes pour vérifier la présence du joueur
    raise ValueError(f"Le joueur '{player_name}' est introuvable dans les données.")
player_id = player_row["id"].values[0]

#EXTRACTION DES PARTIES DU JOUEUR
df_player_games = df_games[(df_games["White"] == player_id) | (df_games["Black"] == player_id)].copy()
df_player_games["Color"] = df_player_games["White"].apply(lambda x: "White" if x == player_id else "Black")
df_player_games["Victory"] = df_player_games.apply(
    lambda row: "Win" if (row["White"] == player_id and row["Result"] == "W") or 
                         (row["Black"] == player_id and row["Result"] == "B")
                else "Loss" if row["Result"] != "D" else "Draw", axis=1)

# OUVERTURES
eco_counts = df_player_games["ECO"].value_counts().head(10)
plt.figure(figsize=(8, 4))
eco_counts.plot(kind="bar", color="skyblue", title=f"Top 10 Ouvertures - {player_name}")
plt.ylabel("Nombre de parties")
plt.xlabel("Code ECO")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

#FORMAT DE TEMPS 
def classify_timecontrol(tc):
    try:
        base, inc = map(int, str(tc).split('+'))
        total = base + inc * 40
        if total <= 120: return "Bullet"
        elif total <= 600: return "Blitz"
        elif total <= 1800: return "Rapid"
        else: return "Classical"
    except:
        return "Unknown"

df_player_games["GameType"] = df_player_games["TimeControl"].apply(classify_timecontrol)
format_counts = df_player_games["GameType"].value_counts()
format_counts.plot(kind="bar", color="salmon", title=f"Formats joués - {player_name}")
plt.ylabel("Nombre de parties")
plt.xlabel("Format")
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()

#  COULEURS & PERFORMANCES 
color_counts = df_player_games["Color"].value_counts()
victory_by_color = df_player_games.groupby(["Color", "Victory"]).size().unstack().fillna(0)

# Répartition des couleurs
color_counts.plot(kind="pie", autopct="%1.1f%%", title=f"Couleurs jouées - {player_name}", ylabel="")
plt.show()

# Victoire/défaite par couleur
victory_by_color.plot(kind="bar", stacked=True, title=f"Résultats par couleur - {player_name}", colormap="Set2")
plt.ylabel("Nombre de parties")
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()


# In[35]:


import pandas as pd
import matplotlib.pyplot as plt

#  CHARGEMENT DES DONNÉES ---
df_games = pd.read_csv("lichess_elite_2020-06_games.csv")
df_players = pd.read_csv("lichess_elite_2020-06_players.csv")

#  TROUVER LES 5 MEILLEURS JOUEURS PAR ELO ---
top5_players = df_players.sort_values(by="MaxElo", ascending=False).head(5)
print("Top 5 joueurs :\n", top5_players[["PlayerName", "MaxElo"]])

#  PRÉPARATION DES DONNÉES ---
top5_ids = top5_players["id"].values
id_to_name = dict(zip(top5_players["id"], top5_players["PlayerName"]))

#  1. Analyse du format de temps préféré ---
df_top_games = df_games[(df_games["White"].isin(top5_ids)) | (df_games["Black"].isin(top5_ids))].copy()

def classify_timecontrol(tc):
    try:
        base, inc = map(int, str(tc).split('+'))
        total = base + inc * 40
        if total <= 120: return "Bullet"
        elif total <= 600: return "Blitz"
        elif total <= 1800: return "Rapid"
        else: return "Classical"
    except:
        return "Unknown"

df_top_games["GameType"] = df_top_games["TimeControl"].apply(classify_timecontrol)

# Ajouter les noms des joueurs pour faciliter la lecture
def get_player_name(uuid):
    return id_to_name.get(uuid, "Autre")

df_top_games["Player"] = df_top_games["White"].apply(get_player_name)
df_top_games.loc[~df_top_games["White"].isin(top5_ids), "Player"] = df_top_games["Black"].apply(get_player_name)

# Affichage : Répartition des formats par joueur ---
plt.figure(figsize=(10, 6))
df_top_games.groupby(["Player", "GameType"]).size().unstack().fillna(0).plot(kind="bar", stacked=True)
plt.title("Répartition des formats de jeu par les 5 meilleurs joueurs")
plt.ylabel("Nombre de parties")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

#  2. Répartition des ouvertures (Top 5 ECO par joueur) ---
eco_by_player = df_top_games[df_top_games["Player"].isin(top5_players["PlayerName"])]

for player in top5_players["PlayerName"]:
    eco_counts = eco_by_player[eco_by_player["Player"] == player]["ECO"].value_counts().head(5)
    plt.figure(figsize=(6, 3))
    eco_counts.plot(kind="bar", color="skyblue")
    plt.title(f"{player} - Top 5 ouvertures (ECO)")
    plt.ylabel("Nombre de parties")
    plt.xlabel("Code ECO")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

#  3. Taux de victoire global par joueur ---
def calc_victory(row):
    if row["White"] in top5_ids and row["Result"] == "W":
        return id_to_name[row["White"]]
    elif row["Black"] in top5_ids and row["Result"] == "B":
        return id_to_name[row["Black"]]
    else:
        return None

df_top_games["Victor"] = df_top_games.apply(calc_victory, axis=1)

victory_counts = df_top_games["Victor"].value_counts().reindex(top5_players["PlayerName"], fill_value=0)
plt.figure(figsize=(8, 4))
victory_counts.plot(kind="bar", color="limegreen")
plt.title("Nombre de victoires par les 5 meilleurs joueurs")
plt.ylabel("Victoires")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


# In[15]:


# 1. Importation
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# 2. Chargement des fichiers
games = pd.read_csv("lichess_elite_2020-06_games.csv")
players = pd.read_csv("lichess_elite_2020-06_players.csv")
tableau = pd.read_csv("tableau.csv")

# 3. Préparation des données
games = games.dropna(subset=["Result", "ECO", "White", "Black"])
games['opening_code'] = games['ECO']

# Associer ECO à nom d'ouverture via tableau.csv
if 'eco' in tableau.columns and 'event' in tableau.columns:
    eco_mapping = dict(zip(tableau['eco'], tableau['event']))
else:
    eco_mapping = {}

games['opening_name'] = games['opening_code'].map(eco_mapping).fillna(games['opening_code'])

games['avg_elo'] = (games['WhiteElo'] + games['BlackElo']) / 2

# 4. Fonction de génération du profil joueur par nom
def generate_player_profile_by_name(player_name):
    # Rechercher l'ID du joueur via PlayerName
    player_row = players[players['PlayerName'].str.lower() == player_name.lower()]

    if player_row.empty:
        print(f" Joueur '{player_name}' introuvable.")
        return None

    player_id = player_row.iloc[0]['id']
    title = player_row.iloc[0].get('Title', 'Non précisé')
    max_elo = player_row.iloc[0].get('MaxElo', 'Non précisé')

    # Récupérer ses parties
    white_games = games[games["White"] == player_id]
    black_games = games[games["Black"] == player_id]
    total_games = len(white_games) + len(black_games)

    if total_games == 0:
        print(f" Aucune partie trouvée pour ce joueur dans le dataset.")
        return None

    # Calcul des résultats
# Correction si Result ∈ {"W", "B", "D"}

    white_wins = (white_games["Result"] == "W").sum()
    white_draws = (white_games["Result"] == "D").sum()
    white_losses = (white_games["Result"] == "B").sum()

    black_wins = (black_games["Result"] == "B").sum()
    black_draws = (black_games["Result"] == "D").sum()
    black_losses = (black_games["Result"] == "W").sum()

    wins = white_wins + black_wins
    draws = white_draws + black_draws
    losses = white_losses + black_losses

    win_rate = wins / total_games * 100
    draw_rate = draws / total_games * 100
    loss_rate = losses / total_games * 100


    preferred_color = "white" if len(white_games) >= len(black_games) else "black"

    # Ouverture la plus fréquente
    all_openings = pd.concat([white_games, black_games])
    fav_opening = all_openings['opening_name'].value_counts().idxmax()

    # Résumé
    profile = {
        "Nom": player_name,
        "Titre": title,
        "Max Elo": max_elo,
        "Nombre de parties": total_games,
        "Victoire (%)": round(win_rate, 2),
        "Défaite (%)": round(loss_rate, 2),
        "Nul (%)": round(draw_rate, 2),
        "Couleur préférée": preferred_color,
        "Ouverture favorite": fav_opening
    }

    return profile

# 5. Interaction
player_name = input(" Entrez le nom du joueur (exactement comme dans PlayerName) : ")

profil = generate_player_profile_by_name(player_name)

if profil:
    print("\n Profil du joueur :\n")
    for key, value in profil.items():
        print(f"{key} : {value}")





# In[11]:


# 1. Importation
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Style des graphiques
sns.set(style="whitegrid")

# 2. Chargement des fichiers
games = pd.read_csv("lichess_elite_2020-06_games.csv")
players = pd.read_csv("lichess_elite_2020-06_players.csv")
tableau = pd.read_csv("tableau.csv")

# 3. Préparation des données
games = games.dropna(subset=["Result", "ECO", "White", "Black"])
games['opening_code'] = games['ECO']

# Associer ECO à nom d'ouverture via tableau.csv
if 'eco' in tableau.columns and 'event' in tableau.columns:
    eco_mapping = dict(zip(tableau['eco'], tableau['event']))
else:
    eco_mapping = {}

games['opening_name'] = games['opening_code'].map(eco_mapping).fillna(games['opening_code'])
games['avg_elo'] = (games['WhiteElo'] + games['BlackElo']) / 2

# 4. Fonction de génération du profil joueur par nom
def generate_player_profile_by_name(player_name):
    """
    cette fonction permet de generer le profil de n'importe quel joueur
    """
    # Rechercher l'ID du joueur via PlayerName
    player_row = players[players['PlayerName'].str.lower() == player_name.lower()]

    if player_row.empty:
        print(f" Joueur '{player_name}' introuvable.")
        return None, None, None

    player_id = player_row.iloc[0]['id']
    title = player_row.iloc[0].get('Title', 'Non précisé')
    max_elo = player_row.iloc[0].get('MaxElo', 'Non précisé')

    # Récupérer ses parties
    white_games = games[games["White"] == player_id]
    black_games = games[games["Black"] == player_id]
    total_games = len(white_games) + len(black_games)

    if total_games == 0:
        print(f" Aucune partie trouvée pour ce joueur dans le dataset.")
        return None, None, None

    # Calcul des résultats
    white_wins = (white_games["Result"] == "W").sum()
    white_draws = (white_games["Result"] == "D").sum()
    white_losses = (white_games["Result"] == "B").sum()

    black_wins = (black_games["Result"] == "B").sum()
    black_draws = (black_games["Result"] == "D").sum()
    black_losses = (black_games["Result"] == "W").sum()

    wins = white_wins + black_wins
    draws = white_draws + black_draws
    losses = white_losses + black_losses

    win_rate = wins / total_games * 100
    draw_rate = draws / total_games * 100
    loss_rate = losses / total_games * 100

    preferred_color = "white" if len(white_games) >= len(black_games) else "black"

    all_openings = pd.concat([white_games, black_games])
    fav_opening = all_openings['opening_name'].value_counts().idxmax()

    # Résumé du profil
    profile = {
        "Nom": player_name,
        "Titre": title,
        "Max Elo": max_elo,
        "Nombre de parties": total_games,
        "Victoire (%)": round(win_rate, 2),
        "Défaite (%)": round(loss_rate, 2),
        "Nul (%)": round(draw_rate, 2),
        "Couleur préférée": preferred_color,
        "Ouverture favorite": fav_opening
    }

    return profile, white_games, black_games

# 5. Interaction utilisateur
player_name = input(" Entrez le nom du joueur (exactement comme dans PlayerName) : ")

profil, white_games, black_games = generate_player_profile_by_name(player_name)

if profil:
    print("\n Profil du joueur :\n")
    for key, value in profil.items():
        print(f"{key} : {value}")

    # Création des figures
all_games = pd.concat([white_games.assign(Color="White"), black_games.assign(Color="Black")])
all_games['Result_for_player'] = all_games.apply(
    lambda row: "Win" if (row["Color"] == "White" and row["Result"] == "W") or 
                            (row["Color"] == "Black" and row["Result"] == "B")
    else "Loss" if (row["Color"] == "White" and row["Result"] == "B") or 
                   (row["Color"] == "Black" and row["Result"] == "W")
    else "Draw",
    axis=1
)

# 1. Répartition des résultats
plt.figure(figsize=(6,4))
sns.countplot(data=all_games, x="Result_for_player", hue="Result_for_player", palette="Set2", legend=False)
plt.title(f"Résultats des parties de {player_name}")
plt.xlabel("Résultat")
plt.ylabel("Nombre de parties")
plt.tight_layout()
plt.show()

# 2. Répartition des couleurs jouées
plt.figure(figsize=(6,4))
sns.countplot(data=all_games, x="Color", hue="Color", palette="pastel", legend=False)
plt.title(f"Couleurs jouées par {player_name}")
plt.xlabel("Couleur")
plt.ylabel("Nombre de parties")
plt.tight_layout()
plt.show()

# 3. Top 10 des ouvertures utilisées
top_openings_df = pd.DataFrame({
    "Opening": top_openings.index,
    "Count": top_openings.values
})

plt.figure(figsize=(8,5))
sns.barplot(data=top_openings_df, y="Opening", x="Count", hue="Opening", palette="muted", legend=False)
plt.title(f"Top 10 ouvertures utilisées par {player_name}")
plt.xlabel("Nombre de parties")
plt.ylabel("Ouverture")
plt.tight_layout()
plt.show()


# 4. Évolution de l’ELO moyen (si date dispo)
if 'UTCDate' in all_games.columns:
    all_games['UTCDate'] = pd.to_datetime(all_games['UTCDate'], errors='coerce')
    elo_by_date = all_games.dropna(subset=['UTCDate']).groupby('UTCDate')['avg_elo'].mean()

    if not elo_by_date.empty:
        plt.figure(figsize=(10,4))
        elo_by_date.plot()
        plt.title(f"Évolution de l'ELO moyen de {player_name} dans le temps")
        plt.xlabel("Date")
        plt.ylabel("ELO moyen")
        plt.tight_layout()
        plt.show()



# In[13]:


# 1. Importations
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid", palette="Set2")  # Style général

# 2. Chargement des données
games = pd.read_csv("lichess_elite_2020-06_games.csv")
players = pd.read_csv("lichess_elite_2020-06_players.csv")
tableau = pd.read_csv("tableau.csv")

# 3. Préparation des données
games = games.dropna(subset=["Result", "ECO", "White", "Black"])
games['opening_code'] = games['ECO']

eco_mapping = dict(zip(tableau['eco'], tableau['event'])) if 'eco' in tableau.columns else {}
games['opening_name'] = games['opening_code'].map(eco_mapping).fillna(games['opening_code'])
games['avg_elo'] = (games['WhiteElo'] + games['BlackElo']) / 2

# 4. Fonction de profil
def generate_player_profile_by_name(player_name):
    player_row = players[players['PlayerName'].str.lower() == player_name.lower()]

    if player_row.empty:
        print(f" Joueur '{player_name}' introuvable.")
        return None, None, None

    player_id = player_row.iloc[0]['id']
    title = player_row.iloc[0].get('Title', 'Non précisé')
    max_elo = player_row.iloc[0].get('MaxElo', 'Non précisé')

    white_games = games[games["White"] == player_id]
    black_games = games[games["Black"] == player_id]
    total_games = len(white_games) + len(black_games)

    if total_games == 0:
        print(" Aucune partie trouvée.")
        return None, None, None

    white_wins = (white_games["Result"] == "W").sum()
    white_draws = (white_games["Result"] == "D").sum()
    white_losses = (white_games["Result"] == "B").sum()

    black_wins = (black_games["Result"] == "B").sum()
    black_draws = (black_games["Result"] == "D").sum()
    black_losses = (black_games["Result"] == "W").sum()

    wins = white_wins + black_wins
    draws = white_draws + black_draws
    losses = white_losses + black_losses

    win_rate = wins / total_games * 100
    draw_rate = draws / total_games * 100
    loss_rate = losses / total_games * 100

    preferred_color = "white" if len(white_games) >= len(black_games) else "black"
    all_openings = pd.concat([white_games, black_games])
    fav_opening = all_openings['opening_name'].value_counts().idxmax()

    profile = {
        "Nom": player_name,
        "Titre": title,
        "Max Elo": max_elo,
        "Nombre de parties": total_games,
        "Victoire (%)": round(win_rate, 2),
        "Défaite (%)": round(loss_rate, 2),
        "Nul (%)": round(draw_rate, 2),
        "Couleur préférée": preferred_color,
        "Ouverture favorite": fav_opening
    }

    return profile, white_games, black_games

# 5. Entrée utilisateur
player_name = input(" Entrez le nom du joueur : ")
profil, white_games, black_games = generate_player_profile_by_name(player_name)

if profil:
    print("\n Profil du joueur :\n")
    for k, v in profil.items():
        print(f"{k} : {v}")

    all_games = pd.concat([white_games.assign(Color="White"), black_games.assign(Color="Black")])
    all_games['Result_for_player'] = all_games.apply(
        lambda row: "Win" if (row["Color"] == "White" and row["Result"] == "W") or 
                                (row["Color"] == "Black" and row["Result"] == "B")
        else "Loss" if (row["Color"] == "White" and row["Result"] == "B") or 
                       (row["Color"] == "Black" and row["Result"] == "W")
        else "Draw", axis=1
    )

    # 1. Résultats des parties
    plt.figure(figsize=(6, 4))
    sns.countplot(data=all_games, x="Result_for_player", hue="Result_for_player", palette="Set2", legend=False)
    plt.title(f"Résultats des parties de {player_name}")
    plt.xlabel("Résultat")
    plt.ylabel("Nombre")
    plt.tight_layout()
    plt.show()

    # 2. Répartition des couleurs (camembert)
    color_counts = all_games['Color'].value_counts()
    plt.figure(figsize=(5, 5))
    plt.pie(color_counts, labels=color_counts.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette("pastel"))
    plt.title(f"Répartition des couleurs jouées par {player_name}")
    plt.tight_layout()
    plt.show()

    # 3. Résultats par couleur (barres horizontales)
    by_color_result = all_games.groupby(['Color', 'Result_for_player']).size().unstack().fillna(0)
    by_color_result.plot(kind='barh', stacked=True, colormap='Set2', figsize=(8, 4))
    plt.title(f"Résultats de {player_name} selon la couleur")
    plt.xlabel("Nombre de parties")
    plt.ylabel("Couleur")
    plt.tight_layout()
    plt.show()

    # 4. Ouvertures préférées
    top_openings = all_games['opening_name'].value_counts().nlargest(10)
    top_openings_df = pd.DataFrame({
        "Opening": top_openings.index,
        "Count": top_openings.values
    })

    plt.figure(figsize=(8, 5))
    sns.barplot(data=top_openings_df, y="Opening", x="Count", hue="Opening", palette="muted", legend=False)
    plt.title(f"Top 10 ouvertures utilisées par {player_name}")
    plt.xlabel("Nombre de parties")
    plt.ylabel("Ouverture")
    plt.tight_layout()
    plt.show()

    # 5. Évolution de l’ELO
    if 'UTCDate' in all_games.columns:
        all_games['UTCDate'] = pd.to_datetime(all_games['UTCDate'], errors='coerce')
        elo_by_date = all_games.dropna(subset=['UTCDate']).groupby('UTCDate')['avg_elo'].mean()
        if not elo_by_date.empty:
            plt.figure(figsize=(10, 4))
            elo_by_date.plot(color="purple")
            plt.title(f"Évolution de l'ELO moyen de {player_name}")
            plt.xlabel("Date")
            plt.ylabel("ELO moyen")
            plt.tight_layout()
            plt.show()



# In[ ]:




