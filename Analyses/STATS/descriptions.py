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


# WARNING : this query spans accross multiple files. currently includes : clusters.py
games_query ="""
        SELECT 
            id, white, black, result, white_elo, black_elo,
            date_time, time_control, opening
        FROM games
        LIMIT 100;
    """

@register_analysis('STATS_analysis')
def STATS_analysis(plot_list : list[str]):
    print("STATS_analysis called")
    games_data : pd.DataFrame = fetch_data_from_sql(games_query)
    cleaned_games_data : pd.DataFrame = clean_games_data(games_data)
    if (plot_list.__contains__('histogram')):
        print("STATS_analysis/histogram called")
        plot_stats_historgram(cleaned_games_data)
    if (plot_list.__contains__('boxplot')):
        print("STATS_analysis/boxplot called")
        plot_stats_boxplot(cleaned_games_data)
    if (plot_list.__contains__('heatmap')):
        print("STATS_analysis/heatmap called")
        plot_stats_heatmap(cleaned_games_data)


def clean_games_data(games) :
    games['date_time'] = pd.to_datetime(games['date_time'], errors='coerce')
    games[['BaseTime', 'Increment']] = games['time_control'].str.split('+', expand=True).astype(float)
    games['EloDiff'] = games['white_elo'] - games['black_elo']
    games['Gagnant'] = games['result'].map({'W': 1, 'B': -1, 'D': 0})
    games['VainqueurElo'] = games.apply(
        lambda row: 
            row['white_elo'] if row['result'] == 'W' else (row['black_elo'] if row['result'] == 'B' else None), 
        axis=1
    )
    games['PerdantElo'] = games.apply(
        lambda row: 
            row['black_elo'] if row['result'] == 'W' else (row['white_elo'] if row['result'] == 'B' else None),
        axis=1
    )
    return games

@assign_plot_to_analysis('STATS_analysis', 'histogram')
def plot_stats_historgram(games):
    figgy : Figure = plt.figure(figsize=(12, 5))
    sns.histplot(games['white_elo'], color='blue', label='White Elo', kde=True)
    sns.histplot(games['black_elo'], color='red', label='Black Elo', kde=True)
    plt.title("Distribution des Elo des joueurs")
    plt.legend()
    plt.grid(True)
    figgy.savefig("rainbow.png")
    
@assign_plot_to_analysis('STATS_analysis', 'boxplot')
def plot_stats_boxplot(games):
    plt.figure(figsize=(8, 6))
    sns.boxplot(data=games[['VainqueurElo', 'PerdantElo']])
    plt.title("Comparaison Elo Gagnants vs Perdants")
    plt.grid(True)

@assign_plot_to_analysis('STATS_analysis', 'heatmap')
def plot_stats_heatmap(games):
    plt.figure(figsize=(8, 6))
    sns.heatmap(games[['white_elo', 'black_elo', 'EloDiff', 'BaseTime', 'Increment', 'Gagnant']].corr(), 
                annot=True, cmap='coolwarm', fmt=".2f")
    plt.title("Heatmap des corrélations")
    

