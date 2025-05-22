from xml.sax.handler import property_interning_dict

from matplotlib.figure import SubFigure
from ..registry import *
from ..base import *
import plotly.tools as tools
import plotly.express as px
import plotly.graph_objects as go
import prince

"""
ANALYSIS PROFILE

Uses tables             : games, players
Uses columns            : games: {opening, time_control}, players: {title}
Description             : Doing an MCA on the most prevalent categorical features
Question                : Is there feature in this set that is more favoured or irrelevant?
Answer                  : 
Speculation             : 

Current problem         : This was supposed to find which of the combinations was more important,
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

### START OF ANALYSIS ##########################################################################################################
@register_analysis('MCA_analysis')
def MCA_analysis(list_of_plots : list[str]) -> None:
    print("MCA_analysis called")
    # general_data = fetch_data_from_sql(opening_time_control_title_query)
    if (list_of_plots.__contains__('scatter_biplot')):
        print("MCA_analysis/scatter_biplot called")
        # fitted_data : prince.MCA = process_and_fit_data(general_data)
        # formatted_data = format_data_for_scatter_biplot(general_data, fitted_data)
        # plot_MCA_scatter_biplot(formatted_data)

@assign_plot_to_analysis('MCA_analysis', 'scatter_biplot')
def plot_MCA_scatter_biplot(coordinates : dict[str,pd.DataFrame]) -> list:
    both_plots = plot_scatter_biplot(
        title='Biplot from scatterplots',
        row_coordinates=coordinates["row_data"],
        columns_coordinates=coordinates["column_data"],
        annotations=False
    )
    row_axe : Figure|SubFigure|None = both_plots["rows"].get_figure()
    column_axe : Figure|SubFigure|None = both_plots['columns'].get_figure()
    if isinstance(row_axe, Figure) and isinstance(column_axe, Figure):
        row_axe.savefig('row_plot_MCA.png')
        column_axe.savefig('columns_plot_MCA.png')
    return [
        tools.mpl_to_plotly(row_axe),
        tools.mpl_to_plotly(column_axe)
    ]

def process_and_fit_data(base_data : pd.DataFrame) -> prince.MCA:
    base_data.columns = ['time_control', 'opening', 'title']
    mca : prince.MCA = prince.MCA(
        n_components=2, # do not change, in plot is fixed to 2 
        n_iter=10,
        copy=False,
        check_input=True,
        engine='sklearn',
        random_state=None
    )    
    return mca.fit(base_data)

def format_data_for_scatter_biplot(base_data : pd.DataFrame, mca : prince.MCA) -> dict[str,pd.DataFrame]:    
    return {
        'row_data': mca.row_coordinates(base_data).reset_index(),
        'column_data' : mca.column_coordinates(base_data).reset_index()
           }

