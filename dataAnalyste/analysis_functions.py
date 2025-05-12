#!/usr/bin/env python
# coding: utf-8

""" Chess Performance Analysis - Lichess Elite June 2020 """

import pandas as pd
import matplotlib.pyplot as plt





""" 1. MaxElo vs Current Elo """
def get_max_vs_current_elo(engine):
    query = """
        SELECT 
            p.name,
            p.max_elo,
            (w.avg_white + b.avg_black) / 2 AS current_elo
        FROM players p
        LEFT JOIN (
            SELECT g.white, AVG(g.white_elo) AS avg_white
            FROM games g
            GROUP BY g.white
        ) w ON p.id = w.white
        LEFT JOIN (
            SELECT g.black, AVG(g.black_elo) AS avg_black
            FROM games g
            GROUP BY g.black
        ) b ON p.id = b.black
        WHERE p.max_elo IS NOT NULL;
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
    plt.show()


""" 2. Win rate by title """
def get_win_rate_by_title(engine):
    query = """
        WITH all_titles AS (
            SELECT g.result, p_white.title AS title
            FROM games g
            JOIN players p_white ON g.white = p_white.id
            WHERE g.result = 'W'
            UNION ALL
            SELECT g.result, p_black.title AS title
            FROM games g
            JOIN players p_black ON g.black = p_black.id
            WHERE g.result = 'B'
        ),
        all_played AS (
            SELECT title FROM players
            WHERE title IS NOT NULL
        )
        SELECT 
            t.title,
            COUNT(*) * 100.0 / (
                SELECT COUNT(*) FROM all_played WHERE title = t.title
            ) AS winrate
        FROM all_titles t
        WHERE t.title IS NOT NULL
        GROUP BY t.title
        ORDER BY winrate DESC;
    """
    return pd.read_sql(query, engine)



def plot_win_rate_by_title(df):
    df = df.dropna().sort_values(by='winrate', ascending=False)
    plt.figure(figsize=(8, 6))
    plt.bar(df['title'], df['winrate'], color='coral')
    plt.title("Win Rate by Player Title")
    plt.ylabel("Win Rate (%)")
    plt.xlabel("Title")
    plt.ylim(0, 100)
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()


""" 3. Win rate by color """
def get_win_rate_by_color(engine):
    query = """
        SELECT result, COUNT(*) as count
        FROM games
        WHERE result IN ('W', 'B', 'D')
        GROUP BY result;
    """
    df = pd.read_sql(query, engine)
    total = df['count'].sum()
    df['percentage'] = df['count'] / total * 100
    df = df.replace({'result': {'W': 'White Wins', 'B': 'Black Wins', 'D': 'Draws'}})
    return df



def plot_win_rate_by_color(df):
    plt.figure(figsize=(8, 6))
    plt.bar(df['result'], df['percentage'], color=['#e0e0e0', '#444444', '#888888'])
    for i, val in enumerate(df['percentage']):
        plt.text(i, val + 1, f'{val:.1f}%', ha='center')
    plt.title("Win Rate by Color")
    plt.ylabel("Percentage (%)")
    plt.ylim(0, 100)
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()


""" 4. Average Elo by opening """
def get_avg_elo_by_opening(engine):
    query = """
        SELECT 
            g.opening AS opening,
            AVG((g.white_elo + g.black_elo)/2) AS average_elo
        FROM games g
        WHERE g.white_elo IS NOT NULL AND g.black_elo IS NOT NULL
        GROUP BY g.opening
        ORDER BY average_elo DESC
        LIMIT 15;
    """
    return pd.read_sql(query, engine)



def plot_avg_elo_by_opening(df):
    # Conversion explicite en chaîne
    df['opening'] = df['opening'].astype(str)

    df = df.sort_values("average_elo")
    plt.figure(figsize=(10, 7))
    plt.barh(df['opening'], df['average_elo'], color='seagreen')
    plt.title("Average Elo by Opening (Top 15)")
    plt.xlabel("Average Elo")
    plt.ylabel("Opening")
    plt.grid(axis='x', linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()

