
from Analyses.base import *

"""
ADMIN ZONE : delcaring filenames and other
""" 
storage_directory = set_storage_directory(DEFAULT_STORAGE_DIR, __file__)
heatmap_file_location = storage_directory + "heatmap_relation_title_and_time_control.png"
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

if not file_exists(test_csv_file_location):
    fetch_sql_and_save_to_csv(title_and_time_control_query,DB_STR_ENGINE, test_csv_file_location)
        
games_with_titles_df = pd.read_csv(test_csv_file_location)

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

plot_heatmap(
    filtered_distribution_df,
    title='Proportion of Time Controls by Player Title (Filtered)',
    xlabel='Time Control',
    ylabel='Player Title',
    filename=heatmap_file_location
)
