#!/usr/bin/env python
# coding: utf-8

""" Chess Performance Analysis - Lichess Elite June 2020 """

import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import  plotly.tools as tools
from plotly.tools import mpl_to_plotly
import seaborn as sns
from json import load
from .utile import plot_barplot

""" Function to create a secure connection to the database"""
def get_engine(params):
    ssl_args = {
        "sslmode": params["sslmode"],
        "sslcert": params["sslcert"],
        "sslkey": params["sslkey"],
        "sslrootcert": params["sslrootcert"]
    }

    ssl_query = "&".join([f"{key}={quote_plus(val)}" for key, val in ssl_args.items()])

    url = (
        f"postgresql+psycopg2://{params['user']}:{params['password']}@"
        f"{params['host']}:{params['port']}/{params['dbname']}?{ssl_query}"
    )

    return create_engine(url)




""" 1. MaxElo vs Current Elo """

"""
Description             : Analyze the difference between a player's peak (max) Elo and their current estimated Elo
Question                : Are elite players still playing at their peak Elo level, or has their performance declined?
Answer                  : Most players have a lower current Elo compared to their max Elo, with a visible gap for many of them
Speculation             : This gap could be due to inactivity, less frequent competitive play, experimentation, or aging.
                          It is also possible that some players continue to play but not with the same intensity or ambition 
                          as during their peak periods, hence a slight decline in consistency and rating.
"""

def get_max_vs_current_elo(engine):
    query = """
        SELECT 
            p.max_elo , current_elo
        FROM players p;
    """
    df = pd.read_sql(query, engine)
    df['EloGap'] = df['max_elo'] - df['current_elo']
    return df



def plot_max_vs_current_elo(df):
    plt.figure(figsize=(8, 6))
    plt.hist(df['EloGap'].dropna(), bins=30, color='skyblue', edgecolor='black')
    plt.title("Distribution of Elo Gap (MaxElo - CurrentElo)")
    plt.xlabel("Elo Gap")
    plt.ylabel("Number of Players")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    axes : Axes = plt.gca()




""" 2. Win rate by title """

"""
Description            : Analyse du taux de victoire en fonction du titre des joueurs.
Question               : Les joueurs avec des titres plus prestigieux (GM, IM, FM, etc.) ont-ils un taux de victoire supérieur ?
Réponse                : Oui. Les Grands Maîtres (GM) ont le taux de victoire le plus élevé (~55.3%), suivis des Maîtres Internationaux (IM) avec ~50.5%.
                        À l’inverse, les titres moins élevés comme NM ou LM ont des taux plus bas (~44-45%).
Spéculation            : Cela confirme que les joueurs avec un niveau plus élevé ont une meilleure performance moyenne.
                        Leur préparation, expérience et compréhension du jeu leur donnent un avantage mesurable.
"""


def get_win_rate_by_title(engine):
    query = """
    WITH win_counts AS (
        SELECT
            CASE
                WHEN g.result = 'W' THEN p_white.title
                WHEN g.result = 'B' THEN p_black.title
            END AS title
        FROM games g
        LEFT JOIN players p_white ON g.white = p_white.id
        LEFT JOIN players p_black ON g.black = p_black.id
        WHERE g.result IN ('W', 'B')
    ),
    total_counts AS (
        SELECT title, COUNT(*) AS total_games
        FROM (
            SELECT p.title
            FROM players p
            JOIN games g ON p.id = g.white OR p.id = g.black
            WHERE p.title IS NOT NULL
        ) sub
        GROUP BY title
    )
    SELECT
        w.title,
        COUNT(*) * 100.0 / t.total_games AS win_rate
    FROM win_counts w
    JOIN total_counts t ON w.title = t.title
    WHERE w.title IS NOT NULL
    GROUP BY w.title, t.total_games
    ORDER BY win_rate DESC;

    """
    return pd.read_sql(query, engine)

def plot_win_rate_by_title_json(current_data):
    return mpl_to_plotly(plot_barplot(
        current_data,
        lables_list='title',
        values_list='win_rate',
        title='Win Rate by Title',
        xlabel='Title',
        ylabel='Win Rate (%)',
        rotation=0
    ).get_figure())



    
""" 3. Win rate by color """

"""
Description            : Évaluation du taux de victoire en fonction de la couleur jouée (blancs, noirs, nulle).
Question               : Y a-t-il un avantage significatif à jouer avec les blancs ou les noirs ?
Réponse                : Oui. Les blancs gagnent environ 46.6% des parties, contre 41.4% pour les noirs. Les nulles représentent environ 12%.
Spéculation            : L’avantage du premier coup (initiative) pour les blancs semble confirmé ici.
                        Cela renforce l’idée largement admise qu’avoir les blancs procure un léger avantage stratégique dès l’ouverture.
"""

def get_win_rate_by_color(engine):
    query = """
        SELECT "result", COUNT(*) as count
        FROM games
        WHERE "result" IN ('W', 'B', 'D')
        GROUP BY "result";
    """
    df = pd.read_sql(query, engine)
    total = df['count'].sum()
    df['win_rate'] = df['count'] / total * 100
    df = df.astype({'result': 'str', 'count': 'int', 'win_rate': 'float'})
    return df


def plot_win_rate_by_color_json(current_data):
    return mpl_to_plotly(plot_barplot(
        current_data,
        lables_list='result',
        values_list='win_rate',
        title='Win Rate by Game Result',
        xlabel='Game Result',
        ylabel='Win Rate (%)',
        rotation=0
    ).get_figure())



""" 4. Average Elo by opening """

"""
Description     : Analysis of the average player level based on the openings they play.
Question        : Are there specific openings preferred by top-level players?
Answer          : Yes. Some openings are associated with very high average Elo ratings — up to around 2960.
                  The top five openings all have average Elos above 2880, indicating they are mainly used by elite players.
Speculation     : These openings are likely more technical, solid, or better documented in chess theory, which attracts top-level players.
                  They may also lead to favorable positions with minimal risk — a key factor in high-stakes games.
                  To explore further, one could link the UUIDs to the actual opening names to better interpret strategic preferences.

"""

def get_avg_elo_by_opening(engine):
    query = """
        SELECT 
            g."opening" AS opening,
            AVG((g.white_elo + g.black_elo)/2.0) AS avg_elo
        FROM games g
        WHERE g.white_elo IS NOT NULL AND g.black_elo IS NOT NULL
        GROUP BY g.opening
        ORDER BY avg_elo DESC
        LIMIT 15;
    """
    df = pd.read_sql(query, engine)
    df = df.astype({'opening': 'str', 'avg_elo': 'float'})
    return df


def plot_avg_elo_by_opening_json(current_data):
    return mpl_to_plotly(plot_barplot(
        current_data,
        lables_list='opening_name',
        values_list='avg_elo',
        title='Average Elo by Opening',
        xlabel='Opening',
        ylabel='Average Elo',
        rotation=45
    ).get_figure())


def json_win_rate_by_title(axes: Axes):
    return tools.mpl_to_plotly(axes.get_figure())
