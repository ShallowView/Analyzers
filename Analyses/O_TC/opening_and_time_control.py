from Analyses.base import *

"""
ADMIN ZONE : delcaring filenames and other
""" 
storage_directory_results = set_storage_directory(DEFAULT_STORAGE_DIR, __file__)
storage_directory_json = set_storage_directory('json', __file__)
# files in storage directory
heatmap_file_location = storage_directory_results + 'heatmap_opening_and_time_control.png'
barplot_file_location = storage_directory_results + 'barplot_opening_and_time_control.png'
#files in json storage directory
heatmap_plot_json_values = storage_directory_json + 'heatmap.json'
# files in parent directory
test_csv_file_location  = storage_directory_results + "../" + "test_csv_opening_and_time_control.csv"


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
    g.time_control
LIMIT {TEST_ROW_COUNT};"""

opening_and_time_control_query_with_count= f"""SELECT
    g.time_control,
    o.name AS opening,
    COUNT(*) AS game_count
FROM
    games g
JOIN
    openings o ON g.opening = o.id
GROUP BY
    g.time_control,
    o.name
ORDER BY
    g.time_control
LIMIT {TEST_ROW_COUNT};"""

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


### START OF ANALYSIS ##########################################################################################################

games_with_opening_and_time_control = fetch_data_from_sql(opening_and_time_control_query)

"""
Once again we are dealing with both categorical values and will have to be formatted for pandas numerically
"""
formatted_games_openings_and_time_controls = calculate_value_distribution(
    games_with_opening_and_time_control,
    group_column='opening',
    value_column='time_control'
)

filtered_games_and_openings : pd.DataFrame = filter_data_by_threshold(formatted_games_openings_and_time_controls, row_threshold=0.95,col_threshold=0/95)

time_control_occurrences : pd.Series = filtered_games_and_openings.sum(axis=0)
used_openings : pd.Series = time_control_occurrences[time_control_occurrences != 0] # removes unsuded openings
most_used_openings : pd.Series =  used_openings.sort_values(ascending=True)
time_controls = most_used_openings.index.values
opening_occurrence = most_used_openings.values
time_control_to_opening_data = pd.DataFrame({'opening': opening_occurrence, 'time_control':time_controls})

print(time_control_to_opening_data.head())


# ax : Axes = plot_heatmap(
#     time_control_to_opening_data,
#     title='Heatmap of Opening and Time Control',
#     xlabel='Opening',
#     ylabel='Time Control',
#     filename=heatmap_file_location
# )


# json_metadata = heatmap_plot_json(ax, time_control_to_opening_data)
# try:
#     with open(heatmap_plot_json_values, 'w') as f:
#         f.write(json_metadata)
# except IOError as e:
#     print(f"An error occurred while writing to the file: {e}")

"""
Here we are calculating the proportions to the grand total of each time control for each opening
We turn this finally into a dataframe containing the time control and the percentage of games played with that time control
"""
total_proportions_series : pd.Series = calculate_proportions_from_total(filtered_games_and_openings)
time_control_percentages : pd.DataFrame = series_to_dataframe(total_proportions_series, 'Time Control', 'Percentage')
time_control_percentages_nicer_format = time_control_percentages.sort_values(by='Percentage', ascending=False)
tope_ones =  time_control_percentages_nicer_format[:3] #HARDCODED 

print(tope_ones)
# axes_data_for_bars : Axes = plot_barplot(
#     tope_ones,
#     lables_list='Time Control',
#     values_list='Percentage',
#     title='Barplot of Time Control Percentages',
#     xlabel='Opening',
#     ylabel='Time Control',
#     filename=barplot_file_location
# )

