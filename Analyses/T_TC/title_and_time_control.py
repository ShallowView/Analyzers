from Analyses.base import *

"""
ADMIN ZONE : delcaring filenames and other
""" 
storage_directory = set_storage_directory(DEFAULT_STORAGE_DIR, __file__)
json_storage_directory = set_storage_directory("json", __file__)
# files in storage directory
heatmap_file_location = storage_directory + "heatmap_relation_title_and_time_control.png"
# files in json storage
heatmap_json = json_storage_directory + "heatmap.json"
# files in parent directory
test_csv_file_location  = storage_directory + "../" + "test_csv_relation_title_and_time_control.csv"


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
LIMIT {TEST_ROW_COUNT};"""


### START OF ANALYSIS ##########################################################################################################

games_with_titles_df = fetch_data_from_sql(title_and_time_control_query)

"""
This function is needed for categorical data since it has no numerical value, to be understood by pandas it needs a numerical 
value.
These numerical values are assigned by this function to these 2 columns
"""
title_time_control_distribution_df = calculate_value_distribution(
    games_with_titles_df,
    group_column='title',
    value_column='time_control'
)

"""
The heatmap becomes unreadable if this isn't applied, there are too many time controls that have almost no users
rendering the following plot bloated
"""
insignificant_value = 0.10 
filtered_distribution_df = filter_insignificant_data(title_time_control_distribution_df, threshold=insignificant_value)

"""These are the elements/feautres used in the table"""
bot_percentages_title = filtered_distribution_df.index
bot_percentages_time_controls = filtered_distribution_df.iloc[0].index
bot_percentages_percentage = filtered_distribution_df.iloc[0].values


# # Here is the representation of the data in an acceptable format
# data = []
# for i in range(len(bot_percentages_title)):
#     for j in range(len(bot_percentages_title)):
#         row = {
#             'title':  bot_percentages_title[i],
#             'time_control' : bot_percentages_time_controls[j],
#             'percentage' :  bot_percentages_percentage[j]    
#         }
#         data.append(row)
# data = pd.DataFrame(data)

ax : Axes = plot_heatmap(
    filtered_distribution_df,
    title='Proportion of Time Controls by Player Title (Filtered)',
    xlabel='Time Control',
    ylabel='Player Title',
    filename=heatmap_file_location
)

plotly_fig = tools.mpl_to_plotly(ax.get_figure())
print(plotly_fig)    

"""
Here get the heatmap metadata in json
"""
# json_metadata = heatmap_plot_json(ax,filtered_distribution_df)
# try:
#     with open(heatmap_json, 'w') as f:
#         f.write(json_metadata)
# except IOError as e:
#     print(f"An error occurred while writing to the file: {e}")

