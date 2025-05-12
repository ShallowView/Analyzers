from Analyses.base import *

"""
ADMIN ZONE : delcaring filenames and other
""" 
storage_directory = set_storage_directory(DEFAULT_STORAGE_DIR, __file__)
json_storage_directory = set_storage_directory("json", __file__)


"""
ANALYSIS PROFILE

Uses tables             : games, players
Uses columns            : games: {opening, time_control}, players: {title}
Description             : Doing an MCA on the most prevalent categorical features
Question                : Is there feature in this set that is more favoured or irrelevant?
Answer                  : 
Speculation             : 
"""

opening_time_control_title_query = """

"""
