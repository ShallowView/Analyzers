from email import contentmanager

from Analyses.STATS.clusters import STATS_analysis_clusters
from Analyses.STATS.openings import STATS_analysis_openings

from .STATS.descriptions import * 
from .O_TC.opening_and_time_control import * 
from .T_TC.title_and_time_control import *
from .MCA.correspondance_opening_time_control_title import *

from .registry import *
from .base import * 
import json
import argparse
import warnings
import sys

"""
This warning is because of a conversion from a seaborn heatmap to a plotly object
I am not sure if this will cause issues when reading in JSON, I am ignorign it for now
"""
warnings.filterwarnings('ignore', message='Dang! That path collection is out of this world')

if __name__ == "__main__":
    
    with open("possible_analyses.json", "w") as possible_analyses_file:
        possible_analyses_file.write(json.dumps(plot_registry))
    
    if (len(sys.argv) == 1):
        with open("possible_analyses.json") as default_all:
            content = json.load(default_all)
    
    if (len(sys.argv) != 1):
        arguments = argparse.ArgumentParser(description=f"""
        JSON file containing list of analyses to run as well as the plotts needed from those analyses
        """)
        arguments.add_argument("path_to_json", type=str)
        args = arguments.parse_args()
        recieved_json_path = args.path_to_json
        
        with open(recieved_json_path) as file:
            content = json.load(file)
    
    content_copy = content.copy()
    processed = False
    while content_copy:
        remaining_keys : list[str] = list(content_copy.keys())
        match content_copy:
            case {"T_TC_analysis": plot_list, **rest}:
                T_TC_analysis(plot_list)
                content_copy.pop("T_TC_analysis")
                processed = True
            case {"O_TC_analysis": plot_list, **rest}:
                O_TC_analysis(plot_list)
                content_copy.pop("O_TC_analysis")
                processed = True
            case {"MCA_analysis" : plot_list, **rest}:
                MCA_analysis(plot_list)
                content_copy.pop("MCA_analysis")
                processed = True
            case {"STATS_analysis" : plot_list, **rest}:
                STATS_analysis(plot_list)
                content_copy.pop("STATS_analysis")
                processed = True
            case {"STATS_analysis_openings" : plot_list, **rest}:
                STATS_analysis_openings(plot_list)
                content_copy.pop("STATS_analysis_openings")
                processed = True
            case {"STATS_analysis_clusters" : plot_list, **rest}:
                STATS_analysis_clusters(plot_list)
                content_copy.pop("STATS_analysis_clusters")
                processed = True
            case _:
                raise Exception(f"Analysis not possible for: {remaining_keys[0]}")
    