import sys
import argparse
import os
from json import load
import logging

import networkx as nx
from community import community_louvain

from Louvain import *

from DataCollection import validate_and_extract_params

# Initialize logging
logging.basicConfig(level=logging.INFO,
										format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Set up argument parser
parser = argparse.ArgumentParser(
	description="Create a network graph with chess player-opening data from a "
							"postgreSQL database, find communities with Louvain's "
							"algorithm and output to JSON."
)
parser.add_argument("-c", "--color", type=str,
										choices=["white", "black"],
										help="Get data for the players"
												 " with the white or black pieces (required).")
parser.add_argument("-l", "--layout", type=str,
										choices=["spring", "kamada"],
										help="How to position the nodes/vertices"
												 " for the graph (required).")
parser.add_argument("-w", "--weighted", action="store_true",
	help="Use weighted edges between openings in the graph, if not specified,"
			 " the weights between openings and their variations is 1 (optional)."
)
parser.add_argument("json_file", type=str,
										help="Path to the output JSON file (required).")
parser.add_argument("--min_count", type=int,
										help="Minimum amount of games played by a player"
												 " in an opening to be included as a node"
												 " (optional, default = 100).")
parser.add_argument("--min_percent", type=float,
										help="Minimum percentage of games played in an opening"
												 " by a player compared to total amount of games"
												 " played by the player before being included"
												 " as a node (optional, default = 0.05).")
parser.add_argument("--Louvain", type=str, choices=["true", "false"],
										help="Perform partitioning of players into communities"
												 " with Louvain's algorithm (optional, default = true).")
parser.add_argument("--iterations", type=int,
										help="For layout = 'spring', how many iterations"
												 " of the Fruchterman-Reingold force-directed algorithm"
												 " (optional, default = 50).")
parser.add_argument("--save", type=str,
										help="Plot the result and save to a png"
												 " with the specified name and path (optional).")

# Parse arguments
args = parser.parse_args()

# Validate JSON file path
if not os.path.isfile(args.json_file):
	raise ValueError(f"File {args.json_file} does not exist.")

# Assign parsed arguments to variables
color = args.color
layout = args.layout
weighted = args.weighted
min_count = args.min_count
min_percent = args.min_percent
louvain = args.Louvain.lower() == "true" if args.Louvain else None
iterations = args.iterations
save = args.save

with (open(args.json_file, 'r') as file):
	all_params = load(file)

required_db_keys = ["dbname", "user", "host", "port"]
optional_db_keys = ["password", "sslmode", "sslkey", "sslcert", "sslrootcert"]
db_params = validate_and_extract_params(all_params, required_db_keys,
																				optional_db_keys)

data = getPlayersOpenings(
	db_params,
	color,
	min_games=min_count if min_count is not None else 100,
	min_percent=min_percent if min_percent is not None else 0.01
)

logger.info("Displaying fetched data:")
print(data)

logger.info("Creating network graph...")
graph = getNetworkGraph(data, weighted)

logger.info(
	f"Calculating node positions for {graph.number_of_nodes()} nodes. "
	f"This can take a while...")
if layout == "kamada":
	pos = nx.kamada_kawai_layout(graph)
elif layout == "spring":
	pos = nx.spring_layout(graph,
												 iterations=iterations if iterations is not None else 50)
else:
	raise ValueError("Invalid layout type. Must be 'kamada' or 'spring'.")

partitions = None
if louvain is None or louvain:
	logger.info("Calculating Louvain partitions...")
	partitions = community_louvain.best_partition(graph)
	if save is not None:
		plotLouvainPartitions(graph, pos, save, partitions)
else:
	if save is not None:
		plotBasic(graph, pos, save, show_edge_labels=False)

exportPlotToJSON(
	graph,
	pos,
	validate_and_extract_params(all_params, ["output"], [""]).get('output'),
	partitions
)
