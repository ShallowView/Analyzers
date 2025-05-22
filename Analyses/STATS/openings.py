import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from ..registry import *
from ..base import * 


"""
ANALYSIS PROFILE

Uses tables             : games
Uses columns            : {opening, result}
Description             : Évaluation statistique de l'impact des ouvertures sur les résultats de parties
Question                : Existe-t-il des corrélations entre choix d'ouverture et issue de partie ?
Answer                  : ...
Speculation             : ...
"""

openings_query = """
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



@register_analysis('STATS_analysis_openings')
def STATS_analysis_openings(plot_list : list[str]):
    print("STATS_analysis_openings called")
    openings_data : pd.DataFrame = fetch_data_from_sql(openings_query)
    if (plot_list.__contains__('barplot')):
        print("STATS_analysis_openings/barplot called")
        plot_stats_openings_barplots(openings=openings_data)


"""
Top 15 most used openings, and what the result of those games yielded
"""
@assign_plot_to_analysis('STATS_analysis_openings', 'barplot')
def plot_stats_openings_barplots(openings : pd.DataFrame):
    plt.figure(figsize=(14, 6))
    sns.barplot(data=openings, x='eco', y='white_win_rate', color='blue', label='White Win')
    sns.barplot(data=openings, x='eco', y='black_win_rate', color='red', label='Black Win', bottom=openings['white_win_rate'])
    sns.barplot(data=openings, x='eco', y='draw_rate', color='gray', label='Draw',
                bottom=openings['white_win_rate'] + openings['black_win_rate'])
    plt.title("Top 15 des ouvertures les plus jouées et leurs résultats")
    plt.ylabel("Proportion de résultats")
    plt.legend()
    