import json
import plotly.tools as tools
from matplotlib.axes import  Axes
import os
"""
DESCRIPTION

This is the entry point of the application, the usage is : <interpreter_command> <input_json_path> <output_json_path>

In this JSON file I would like
    - attribute "analysis" that will correspond to the name of a registered analysis
        - in this attribute there will be plots that you can select from
            - each plot will have functions that are assigned to it
            
This means : the program needs to have 
"""

plot_registry : dict = {}

def register_analysis(analysis_name: str):
    """Registers a plot name in the registry with a default value of False,
       meaning that it is empty -> will be easier to read"""
    def decorator(func):
        if analysis_name not in plot_registry:
            plot_registry[analysis_name] = []
        return func
    return decorator

def assign_plot_to_analysis(analysis_name: str, plot_function_name : str):
    def decorator(func):
        if analysis_name not in plot_registry:
            print("ERROR, plot name not in registry")
        if isinstance(plot_registry[analysis_name], list):
            if func.__name__ not in plot_registry[analysis_name]:
                plot_registry[analysis_name].append(plot_function_name)
        return func
    return decorator
            
def plot_to_json(plot_directory_path : str, plot_name):
    def decorator(func):
        os.makedirs(plot_directory_path + plot_name ,exist_ok=True)
        with open(plot_name, "w") as plot_file:
            plot_file.write(json.dumps(tools.mpl_to_plotly(func)))