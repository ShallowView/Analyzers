from Analyses.O_TC.opening_and_time_control import * 
from Analyses.registry import *
from Analyses.base import * 
import json

OUTPUT_DIR = 'json'
if __name__ == "__main__":
    O_TC_analysis(["O_TC_heatmap", "O_TC_barplot"])
    
    