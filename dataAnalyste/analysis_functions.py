#!/usr/bin/env python
# coding: utf-8

""" Chess Performance Analysis - Lichess Elite June 2020 """

import pandas as pd
import matplotlib.pyplot as plt
from main import get_engine, db_params_SSL


""" Connect to database """
engine = get_engine(db_params_SSL)


""" 1. MaxElo vs Current Elo"""
def get_max_vs_current_elo(engine):
    query = """
        SELECT 
            p."PlayerName",
            p."MaxElo",
            (w.avg_white + b.avg_black)/2 AS "CurrentElo"
        FROM players p
        LEFT JOIN (
            SELECT g."White", AVG(g."WhiteElo") as avg_white
            FROM games g
            GROUP BY g."White"
        ) w ON p.id = w."White"
        LEFT JOIN (
            SELECT g."Black", AVG(g."BlackElo") as avg_black
            FROM games g
            GROUP BY g."Black"
        ) b ON p.id = b."Black"
        WHERE p."MaxElo" IS NOT NULL;
    """
    df = pd.read_sql(query, engine)
    df['EloGap'] = df['MaxElo'] - df['CurrentElo']
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
            SELECT g."Result", p_white."Title" AS "Title"
            FROM games g
            JOIN players p_white ON g."White" = p_white.id
            WHERE g."Result" = 'W'
            UNION ALL
            SELECT g."Result", p_black."Title" AS "Title"
            FROM games g
            JOIN players p_black ON g."Black" = p_black.id
            WHERE g."Result" = 'B'
        ),
        all_played AS (
            SELECT "Title" FROM players
            WHERE "Title" IS NOT NULL
        )
        SELECT 
            t."Title",
            COUNT(*) * 100.0 / (
                SELECT COUNT(*) FROM all_played WHERE "Title" = t."Title"
            ) AS "WinRate"
        FROM all_titles t
        WHERE t."Title" IS NOT NULL
        GROUP BY t."Title"
        ORDER BY "WinRate" DESC;
    """
    return pd.read_sql(query, engine)


def plot_win_rate_by_title(df):
    df = df.dropna().sort_values(by='WinRate', ascending=False)
    plt.figure(figsize=(8, 6))
    plt.bar(df['Title'], df['WinRate'], color='coral')
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
        SELECT "Result", COUNT(*) as count
        FROM games
        WHERE "Result" IN ('W', 'B', 'D')
        GROUP BY "Result";
    """
    df = pd.read_sql(query, engine)
    total = df['count'].sum()
    df['Percentage'] = df['count'] / total * 100
    df = df.replace({'Result': {'W': 'White Wins', 'B': 'Black Wins', 'D': 'Draws'}})
    return df


def plot_win_rate_by_color(df):
    plt.figure(figsize=(8, 6))
    plt.bar(df['Result'], df['Percentage'], color=['#e0e0e0', '#444444', '#888888'])
    for i, val in enumerate(df['Percentage']):
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
            COALESCE(g."Opening", g."ECO") AS "Opening",
            AVG((g."WhiteElo" + g."BlackElo")/2) AS "AverageElo"
        FROM games g
        WHERE g."WhiteElo" IS NOT NULL AND g."BlackElo" IS NOT NULL
        GROUP BY "Opening"
        ORDER BY "AverageElo" DESC
        LIMIT 15;
    """
    return pd.read_sql(query, engine)


def plot_avg_elo_by_opening(df):
    df = df.sort_values("AverageElo")
    plt.figure(figsize=(10, 7))
    plt.barh(df['Opening'], df['AverageElo'], color='seagreen')
    plt.title("Average Elo by Opening (Top 15)")
    plt.xlabel("Average Elo")
    plt.ylabel("Opening")
    plt.grid(axis='x', linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()





