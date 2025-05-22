from ..base import *
from ..registry import * 
import plotly.tools as tools

"""
ANALYSIS PROFILE

Uses tables             : games, players
Uses columns            : games: {black, white}, players: {id, title}
Description             : Finding a correlation for a certain time control with a certain title
Question                : Is the preference for different time controls related to chess titles?
Answer                  : No, they ALL highly favour Blitz 180 with no time increment
Speculation             : They most ikely want to play as many games as possible and following the pseudolaw of Piretto they 
                          find that they will gain the most practice and experience from playing games that are short enough
                          so as to still be able to think about the moves and be able to play many games.
                          It is , in my opinion, for this reason that this time control is preferred.
"""    

title_and_time_control_query = f"""SELECT
    g.time_control,
    CASE
        WHEN white.title IS NOT NULL THEN white.title
        WHEN black.title IS NOT NULL THEN black.title
        ELSE 'No Title'
    END AS title
FROM
    games g
LEFT JOIN
    players white ON g.white = white.id
LEFT JOIN
    players black ON g.black = black.id
WHERE white.title IS NOT NULL OR black.title IS NOT NULL
LIMIT {10};"""


### START OF ANALYSIS ##########################################################################################################

@register_analysis('T_TC_analysis')
def T_TC_analysis(plot_names : list[str]):
    print("T_TC_analysis called")
    original_data = fetch_data_from_sql(title_and_time_control_query)
    if (plot_names.__contains__('heatmap')):
        formatted_heatmap_data = format_data_for_plot(original_data)
        filtered_heatmap_data = filter_data_for_plot(formatted_heatmap_data)
        heatmap_plot_analysis = plot_title_and_time_control_heatmap(filtered_heatmap_data)
        store_analysis_file('T_TC_analysis/heatmap', heatmap_plot_analysis)

@assign_plot_to_analysis('T_TC_analysis','heatmap')
def plot_title_and_time_control_heatmap(formatted_and_filtered : pd.DataFrame):
    print("T_TC_analysis/heatmap called")
    return tools.mpl_to_plotly(plot_heatmap(
    formatted_and_filtered,
    title='Proportion of Time Controls by Player Title (Filtered)',
    xlabel='Time Control',
    ylabel='Player Title'
    ).get_figure())

## Data handler functions

def format_data_for_plot(original_data : pd.DataFrame):
    """
    This function is needed for categorical data since it has no numerical value, to be understood by pandas it needs a numerical 
    value.
    These numerical values are assigned by this function to these 2 columns
    """
    return calculate_value_distribution(
        original_data,
        group_column='title',
        value_column='time_control'
    )
    
def filter_data_for_plot(formatted_data : pd.DataFrame):
    """
    The heatmap becomes unreadable if this isn't applied, there are too many time controls that have almost no users
    rendering the following plot bloated
    """
    insignificant_value = 0.10 
    filtered_distribution_df = filter_insignificant_data(formatted_data, threshold=insignificant_value)
    """These are the elements/feautres used in the table"""
    # bot_percentages_title = filtered_distribution_df.index
    # bot_percentages_time_controls = filtered_distribution_df.iloc[0].index
    # bot_percentages_percentage = filtered_distribution_df.iloc[0].values
    return filtered_distribution_df


