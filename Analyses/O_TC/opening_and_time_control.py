from operator import contains
from Analyses.registry import *
from Analyses.base import *  
from plotly import tools
"""
ANALYSIS PROFILE

Uses tables             : games
Uses columns            : games: {id, time_control, opening}  
Description             : Finding a relation between the opening and the time control of the  game
Question                : Is the preference for different openings related to the game mode/time control?
Answer                  : 
Speculation             : 
"""

opening_and_time_control_query = f"""SELECT
    g.time_control,
    o.name AS opening
    
FROM
    games g
JOIN
    openings o ON g.opening = o.id
GROUP BY
    g.time_control,
    o.name
ORDER BY
    g.time_control;"""

### START OF ANALYSIS ##########################################################################################################
@register_analysis('O_TC_analysis')
def O_TC_analysis(list_of_plot_names : list[str]):
    print("O_TC_analysis called")
    # original_data = set_original_data(opening_and_time_control_query)
    # filtered_data = format_data_for_plots(original_data)
    if (list_of_plot_names.__contains__('barplot')):
        print("O_TC_analysis/barplot created")
        # barplot_data = get_barplot_data(filtered_data)
        # analysis_plot_json_barplot = plot_opening_and_time_control_barplot(barplot_data)
        # store_analysis_file('O_TC_analysis/barplot',analysis_plot_json_barplot)
    if (list_of_plot_names.__contains__('heatmap')):
        print("O_TC_analysis/heatmap created")
        # heatmap_data = get_heatmap_data(filtered_data)
        # analysis_plot_json_barplot = plot_opening_and_time_control_heatmap(heatmap_data)
        # store_analysis_file('O_TC_analysis/heatmap', analysis_plot_json_barplot)
        
"""
    Functions used for this analysis
"""
def calculate_proportions_from_total(games_and_openings : pd.DataFrame) -> pd.Series:
    time_control_counts = games_and_openings.sum(axis=0)
    total_games = time_control_counts.sum()
    time_control_proportions = time_control_counts / total_games
    time_control_percentages = time_control_proportions * 100
    return time_control_percentages

def series_to_dataframe(series : pd.Series, labels_list : str, values_list : str) -> pd.DataFrame:
    df = pd.DataFrame(series)
    df.reset_index(inplace=True)
    df.columns = [labels_list, values_list]
    return df

# This function contains some formatting for BOTH plots
def format_data_for_plots(intial_data_from_sql_query : pd.DataFrame) -> pd.DataFrame :
    """
    Once again we are dealing with both categorical values and will have to be formatted for pandas numerically
    """
    formatted_games_openings_and_time_controls = calculate_value_distribution(
        intial_data_from_sql_query,
        group_column='opening',
        value_column='time_control'
    )
    return filter_data_by_threshold(formatted_games_openings_and_time_controls, row_threshold=0.95,col_threshold=0/95)

"""
PLOT FUNCTIONS
"""
@assign_plot_to_analysis('O_TC_analysis','heatmap')
def plot_opening_and_time_control_heatmap(current_data : pd.DataFrame):
    return tools.mpl_to_plotly(plot_heatmap(
            current_data,
            title='Heatmap of Opening and Time Control',
            xlabel='Opening',
            ylabel='Time Control'
            ).get_figure())

def get_heatmap_data(filtered_games_and_openings_data : pd.DataFrame) -> pd.DataFrame :
    """
    This is the things needed for the heatmap data
    """
    time_control_occurrences : pd.Series = filtered_games_and_openings_data.sum(axis=0)
    used_openings : pd.Series = time_control_occurrences[time_control_occurrences != 0] # removes unsuded openings
    most_used_openings : pd.Series =  used_openings.sort_values(ascending=True)
    time_controls = most_used_openings.index.values
    opening_occurrence = most_used_openings.values
    time_control_to_opening_data = pd.DataFrame({'opening': opening_occurrence}, index=time_controls)
    return time_control_to_opening_data

@assign_plot_to_analysis('O_TC_analysis','barplot')
def plot_opening_and_time_control_barplot(current_data : pd.DataFrame):
    """
    This is the original plot wrapped in another function to turn it into the JSON format that the front
    end needs to read plots and reconstruct them
    """
    return tools.mpl_to_plotly(plot_barplot(
        current_data,
        lables_list='Time Control',
        values_list='Percentage',
        title='Barplot of Time Control Percentages',
        xlabel='Opening',
        ylabel='Time Control'
    ).get_figure())

def get_barplot_data(filtered_games_and_openings_data : pd.DataFrame) -> pd.DataFrame:
    """
    Here we are calculating the proportions to the grand total of each time control for each opening
    We turn this finally into a dataframe containing the time control and the percentage of games played with that time control
    """
    total_proportions_series : pd.Series = calculate_proportions_from_total(filtered_games_and_openings_data)
    time_control_percentages : pd.DataFrame = series_to_dataframe(total_proportions_series, 'Time Control', 'Percentage')
    time_control_percentages_nicer_format : pd.DataFrame = time_control_percentages.sort_values(by='Percentage', ascending=False)
    return time_control_percentages_nicer_format[:3] #HARDCODED 

"""
This will set the data to be used for both analyses
"""
def set_original_data(opening_and_time_control_query : str) -> pd.DataFrame:
    return fetch_data_from_sql(opening_and_time_control_query)
