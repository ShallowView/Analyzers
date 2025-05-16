from altair import LayerChart
from matplotlib.pyplot import plot
from Analyses.base import *
import prince

"""
ADMIN ZONE : delcaring filenames and other
""" 
storage_directory = set_storage_directory(DEFAULT_STORAGE_DIR, __file__)
json_storage_directory = set_storage_directory("json", __file__)
csv_stotrage_direcotry = set_storage_directory("csv", __file__)

# files in findings
try_plot_image = storage_directory + "apples.png"

csv_test_data = csv_stotrage_direcotry + "test_csv.csv"

"""
ANALYSIS PROFILE

Uses tables             : games, players
Uses columns            : games: {opening, time_control}, players: {title}
Description             : Doing an MCA on the most prevalent categorical features
Question                : Is there feature in this set that is more favoured or irrelevant?
Answer                  : 
Speculation             : 

Current problem         : This was supposed to find whihc of the combinations was more important,
                          which would summarize other analyses we have made. However, the high different 
                          in openings played ALMOST ALL in the same time control doesn't allow for a 
                          good insight into any other aspect. The title && time control is too great to 
                          see anything else.
                          To solve this we will do a series of chi square tests.
                                - To see the dependance of title onto the time_control
                                  and the dependance of opening onto the time control, it should confirm what 
                                  we have seen so far in other graphs.
                          
"""

opening_time_control_title_query = """SELECT
    g.time_control,
    g.opening,
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
"""

if not file_exists(csv_test_data):
    fetch_sql_and_save_to_csv(
        query=opening_time_control_title_query, 
        output_csv_path=csv_test_data)

correspondance_opening_time_control_title : pd.DataFrame = pd.read_csv(csv_test_data, nrows=100)

correspondance_opening_time_control_title.columns = ['time_control', 'opening', 'title']

# print(correspondance_opening_time_control_title.head())

mca : prince.MCA = prince.MCA(
    n_components=2, 
    n_iter=10,
    copy=True,
    check_input=True,
    engine='sklearn',
    random_state=42
)
mca : prince.MCA = mca.fit(correspondance_opening_time_control_title)

print(mca.eigenvalues_summary)

"""
These are the relatioships tested
"""
# print(mca.column_coordinates(correspondance_opening_time_control_title).head())

"""
The points in the graph are the relations 
"""
given_plot_object : LayerChart = mca.plot(
    correspondance_opening_time_control_title,
    x_component=0,
    y_component=1,
    show_column_markers=True,
    show_row_markers=True,
    show_column_labels=True,
    show_row_labels=False
)

row_coords_df = mca.row_coordinates(correspondance_opening_time_control_title).reset_index()
col_coords_df = mca.column_coordinates(correspondance_opening_time_control_title).reset_index()

plot_scatter_biplot(
    title='Biplot from scatterplots',
    row_coordinates=row_coords_df,
    columns_coordinates=col_coords_df,
    annotations=False,
    filepath="applemanio.png"
)